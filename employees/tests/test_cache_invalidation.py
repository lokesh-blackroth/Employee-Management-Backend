
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from employees.services.cache_service import (
    DEPARTMENT_SUMMARY_CACHE_KEY,
    get_cached_department_summary,
    invalidate_department_summary_cache,
)


TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "department-summary-tests",
    }
}


@override_settings(CACHES=TEST_CACHES)
class DepartmentSummaryCacheTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("employees.services.cache_service.get_department_summary")
    def test_cache_miss_calculates_and_caches_summary(self, get_summary):
        expected = {"total_employees": 5}
        get_summary.return_value = expected

        result = get_cached_department_summary()

        self.assertEqual(result, expected)
        get_summary.assert_called_once_with()
        self.assertEqual(
            cache.get(DEPARTMENT_SUMMARY_CACHE_KEY),
            expected,
        )

    @patch("employees.services.cache_service.get_department_summary")
    def test_cache_hit_does_not_query_summary_again(self, get_summary):
        expected = {"total_employees": 5}
        cache.set(DEPARTMENT_SUMMARY_CACHE_KEY, expected)

        result = get_cached_department_summary()

        self.assertEqual(result, expected)
        get_summary.assert_not_called()

    @patch("employees.services.cache_service.get_department_summary")
    def test_invalidation_prevents_stale_values(self, get_summary):
        get_summary.side_effect = [
            {"total_employees": 5},
            {"total_employees": 6},
        ]

        first_result = get_cached_department_summary()
        self.assertEqual(first_result["total_employees"], 5)

        # Simulate an employee write by invalidating the cache.
        invalidate_department_summary_cache()

        second_result = get_cached_department_summary()

        self.assertEqual(second_result["total_employees"], 6)
        self.assertEqual(get_summary.call_count, 2)

    @patch("employees.services.cache_service.get_department_summary")
    @patch("employees.services.cache_service.cache.get",
           side_effect=ConnectionError("Redis unavailable"))
    def test_redis_read_failure_falls_back_to_database(
        self, cache_get, get_summary
    ):
        expected = {"total_employees": 5}
        get_summary.return_value = expected

        result = get_cached_department_summary()

        self.assertEqual(result, expected)
        get_summary.assert_called_once_with()

    @patch("employees.services.cache_service.get_department_summary")
    @patch("employees.services.cache_service.cache.set",
           side_effect=ConnectionError("Redis unavailable"))
    def test_redis_write_failure_falls_back_to_database(
        self, cache_set, get_summary
    ):
        expected = {"total_employees": 5}
        get_summary.return_value = expected

        result = get_cached_department_summary()

        self.assertEqual(result, expected)
        self.assertTrue(get_summary.called)
