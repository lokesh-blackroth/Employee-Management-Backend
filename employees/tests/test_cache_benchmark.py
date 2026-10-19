import statistics
import time
from datetime import date

from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from employees.api.reports import get_department_summary
from employees.models import Department, Employee
from employees.services.cache_service import (
    DEPARTMENT_SUMMARY_CACHE_KEY,
    get_cached_department_summary,
)


class DepartmentSummaryBenchmarkTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        departments = list(
            Department.objects.order_by("id")[:3]
        )

        if not departments:
            departments = [
                Department.objects.create(
                    name="Benchmark Engineering",
                    code="BENCH-ENG",
                    description="Benchmark Department",
                ),
                Department.objects.create(
                    name="Benchmark HR",
                    code="BENCH-HR",
                    description="Benchmark Department",
                ),
                Department.objects.create(
                    name="Benchmark Finance",
                    code="BENCH-FIN",
                    description="Benchmark Department",
                ),
            ]

        employees = []

        for index in range(30):
            employees.append(
                Employee(
                    employee_code=f"BENCH{index + 1:03d}",
                    first_name=f"Test{index + 1}",
                    last_name="Employee",
                    email=f"benchmark{index + 1}@example.com",
                    phone=f"900000{index + 1:04d}",
                    department=departments[index % len(departments)],
                    designation="Software Engineer",
                    salary=50000 + (index * 1000),
                    joining_date=date(2024, 1, 1),
                    is_active=True,
                )
            )

        Employee.objects.bulk_create(employees)

    def test_department_summary_baseline_vs_cache(self):
        runs = 10

        # --------------------------------------------------
        # BASELINE: direct database calculation
        # --------------------------------------------------
        baseline_times = []
        baseline_queries = []

        for _ in range(runs):
            with CaptureQueriesContext(connection) as queries:
                start = time.perf_counter()

                get_department_summary()

                elapsed = (
                    time.perf_counter() - start
                ) * 1000

            baseline_times.append(elapsed)
            baseline_queries.append(len(queries))

        # --------------------------------------------------
        # CACHE MISS: database calculation + Redis write
        # --------------------------------------------------
        cache.delete(DEPARTMENT_SUMMARY_CACHE_KEY)

        with CaptureQueriesContext(connection) as queries:
            start = time.perf_counter()

            get_cached_department_summary()

            cache_miss_time = (
                time.perf_counter() - start
            ) * 1000

        cache_miss_queries = len(queries)

        # --------------------------------------------------
        # CACHE HIT: Redis only
        # --------------------------------------------------
        cache_hit_times = []
        cache_hit_queries = []

        for _ in range(runs):
            with CaptureQueriesContext(connection) as queries:
                start = time.perf_counter()

                get_cached_department_summary()

                elapsed = (
                    time.perf_counter() - start
                ) * 1000

            cache_hit_times.append(elapsed)
            cache_hit_queries.append(len(queries))

        # --------------------------------------------------
        # RESULTS
        # --------------------------------------------------
        print("\n" + "=" * 60)
        print("DEPARTMENT SUMMARY CACHE BENCHMARK")
        print("=" * 60)

        print(f"Employees: {Employee.objects.count()}")
        print(f"Runs: {runs}")

        print("\nBASELINE - DIRECT DATABASE")
        print(
            f"Median latency: "
            f"{statistics.median(baseline_times):.3f} ms"
        )
        print(
            f"Average latency: "
            f"{statistics.mean(baseline_times):.3f} ms"
        )
        print(
            f"Median SQL queries: "
            f"{statistics.median(baseline_queries):.1f}"
        )

        print("\nCACHE MISS")
        print(f"Latency: {cache_miss_time:.3f} ms")
        print(f"SQL queries: {cache_miss_queries}")

        print("\nCACHE HIT - REDIS")
        print(
            f"Median latency: "
            f"{statistics.median(cache_hit_times):.3f} ms"
        )
        print(
            f"Average latency: "
            f"{statistics.mean(cache_hit_times):.3f} ms"
        )
        print(
            f"Median SQL queries: "
            f"{statistics.median(cache_hit_queries):.1f}"
        )

        print("=" * 60)

        # --------------------------------------------------
        # ASSERTIONS
        # --------------------------------------------------
        self.assertEqual(
            Employee.objects.count(),
            30,
        )

        self.assertTrue(
            all(
                query_count > 0
                for query_count in baseline_queries
            )
        )

        self.assertGreater(
            cache_miss_queries,
            0,
        )

        self.assertTrue(
            all(
                query_count == 0
                for query_count in cache_hit_queries
            )
        )