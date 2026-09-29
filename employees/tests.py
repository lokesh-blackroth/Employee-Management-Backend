from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Department,
    Employee,
    EmployeeProfile,
    Project,
)


# ============================================================
# API TESTS
# ============================================================

class EmployeeAPITestCase(APITestCase):

    def setUp(self):
        # Authenticate all Employee API test requests
        self.user = User.objects.create_user(
            username="testuser",
            password="Test@12345"
        )
        self.client.force_authenticate(user=self.user)

        self.department = Department.objects.create(
            name="Test Department",
            code="TEST_DEPT",
            description="Department for automated tests",
        )

        self.employee = Employee.objects.create(
            employee_code="TEST001",
            first_name="Test",
            last_name="Employee",
            email="test@example.com",
            phone="9876543210",
            department=self.department,
            designation="Developer",
            salary=50000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        self.list_url = reverse("employee-list")

        self.detail_url = reverse(
            "employee-detail",
            kwargs={"pk": self.employee.id},
        )

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    def test_employee_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------------

    def test_employee_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def test_create_employee(self):
        data = {
            "employee_code": "TEST002",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "9876543211",
            "department": self.department.id,
            "designation": "Tester",
            "salary": 45000,
            "joining_date": "2026-02-01",
            "is_active": True,
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def test_update_employee(self):
        data = {
            "employee_code": self.employee.employee_code,
            "first_name": "Updated",
            "last_name": self.employee.last_name,
            "email": self.employee.email,
            "phone": self.employee.phone,
            "department": self.department.id,
            "designation": self.employee.designation,
            "salary": 60000,
            "joining_date": str(self.employee.joining_date),
            "is_active": True,
        }

        response = self.client.put(
            self.detail_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def test_delete_employee(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    def test_search_employee(self):
        response = self.client.get(
            f"{self.list_url}?search=Test"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # DEPARTMENT FILTER
    # --------------------------------------------------------

    def test_department_filter(self):
        response = self.client.get(
            f"{self.list_url}?department={self.department.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # ACTIVE FILTER
    # --------------------------------------------------------

    def test_active_filter(self):
        response = self.client.get(
            f"{self.list_url}?is_active=true"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    def test_employee_not_found(self):
        url = reverse(
            "employee-detail",
            kwargs={"pk": 99999},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
# ============================================================
# RELATIONSHIP TESTS
# ============================================================

class EmployeeRelationshipTestCase(TestCase):

    def setUp(self):

        # ----------------------------------------------------
        # Department
        # ----------------------------------------------------

        self.department = Department.objects.create(
            name="Test Department",
            code="TEST_DEPT",
            description="Department for relationship tests",
        )

        # ----------------------------------------------------
        # Employees
        # ----------------------------------------------------

        self.employee1 = Employee.objects.create(
            employee_code="REL001",
            first_name="John",
            last_name="Smith",
            email="rel001@example.com",
            phone="9000000001",
            department=self.department,
            designation="Developer",
            salary=50000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        self.employee2 = Employee.objects.create(
            employee_code="REL002",
            first_name="Jane",
            last_name="Smith",
            email="rel002@example.com",
            phone="9000000002",
            department=self.department,
            designation="Tester",
            salary=45000,
            joining_date=date(2026, 1, 2),
            is_active=True,
        )

        # ----------------------------------------------------
        # Project
        # ----------------------------------------------------

        self.project = Project.objects.create(
            name="Relationship Project",
            project_code="RELPRJ001",
            description="Project for relationship testing",
            client_name="Test Client",
            start_date=date(2026, 1, 1),
            status="Active",
        )

    # ========================================================
    # FOREIGN KEY
    # ========================================================

    def test_employee_department_relationship(self):

        employee = Employee.objects.get(
            employee_code="REL001"
        )

        self.assertEqual(
            employee.department,
            self.department,
        )

        self.assertEqual(
            employee.department.name,
            "Test Department",
        )

    # ========================================================
    # REVERSE FOREIGN KEY
    # ========================================================

    def test_department_has_employees(self):

        employees = self.department.employees.all()

        self.assertEqual(
            employees.count(),
            2,
        )

        self.assertIn(
            self.employee1,
            employees,
        )

        self.assertIn(
            self.employee2,
            employees,
        )

    # ========================================================
    # ONE TO ONE
    # ========================================================

    def test_employee_profile_relationship(self):

        profile = EmployeeProfile.objects.create(
            employee=self.employee1,
            date_of_birth=date(2000, 1, 1),
            address="Test Address",
            emergency_contact="9111111111",
            blood_group="O+",
        )

        self.assertEqual(
            self.employee1.profile,
            profile,
        )

        self.assertEqual(
            profile.employee,
            self.employee1,
        )

    # ========================================================
    # EMPLOYEE WITHOUT PROFILE
    # ========================================================

    def test_employee_without_profile(self):

        self.assertFalse(
            EmployeeProfile.objects.filter(
                employee=self.employee2
            ).exists()
        )

    # ========================================================
    # MANY TO MANY
    # ========================================================

    def test_employee_project_relationship(self):

        self.employee1.projects.add(self.project)

        self.assertIn(
            self.project,
            self.employee1.projects.all(),
        )

        self.assertIn(
            self.employee1,
            self.project.employees.all(),
        )

    # ========================================================
    # PROJECT WITH MULTIPLE EMPLOYEES
    # ========================================================

    def test_project_multiple_employees(self):

        self.project.employees.add(
            self.employee1,
            self.employee2,
        )

        employees = self.project.employees.all()

        self.assertEqual(
            employees.count(),
            2,
        )

        self.assertIn(
            self.employee1,
            employees,
        )

        self.assertIn(
            self.employee2,
            employees,
        )

    # ========================================================
    # INVALID DEPARTMENT
    # ========================================================

    def test_invalid_department(self):

        self.assertFalse(
            Department.objects.filter(
                id=99999
            ).exists()
        )


# ============================================================
# ADVANCED ORM REPORTING TESTS
# ============================================================

class AdvancedORMReportingTestCase(APITestCase):

    def setUp(self):
        # Authenticate API requests used by the query optimization test
        self.user = User.objects.create_user(
            username="reportuser",
            password="Test@12345"
        )
        self.client.force_authenticate(user=self.user)

        self.department = Department.objects.create(
            name="Reporting Department",
            code="REPORT_DEPT",
            description="Department for ORM reporting tests",
        )

        self.employee1 = Employee.objects.create(
            employee_code="REPORT001",
            first_name="Alice",
            last_name="Test",
            email="alice.report@example.com",
            phone="9111111111",
            department=self.department,
            designation="Developer",
            salary=50000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        self.employee2 = Employee.objects.create(
            employee_code="REPORT002",
            first_name="Bob",
            last_name="Test",
            email="bob.report@example.com",
            phone="9222222222",
            department=self.department,
            designation="Tester",
            salary=60000,
            joining_date=date(2026, 1, 2),
            is_active=True,
        )

        self.project = Project.objects.create(
            name="Reporting Project",
            project_code="REPORTPRJ001",
            description="Project for ORM reporting tests",
            client_name="Reporting Client",
            start_date=date(2026, 1, 1),
            status="Active",
        )

    # --------------------------------------------------------
    # EMPTY DEPARTMENT
    # --------------------------------------------------------

    def test_empty_department(self):
        from django.db.models import Count

        empty_department = Department.objects.create(
            name="Empty Department",
            code="EMPTY_DEPT",
            description="Department with no employees",
        )

        result = Department.objects.annotate(
            employee_count=Count("employees")
        ).get(
            id=empty_department.id
        )

        self.assertEqual(
            result.employee_count,
            0,
        )

    # --------------------------------------------------------
    # DEPARTMENT WITH EMPLOYEES
    # --------------------------------------------------------

    def test_department_with_employees(self):
        from django.db.models import Count

        result = Department.objects.annotate(
            employee_count=Count("employees")
        ).get(
            id=self.department.id
        )

        self.assertEqual(
            result.employee_count,
            2,
        )

    # --------------------------------------------------------
    # MANY EMPLOYEES
    # --------------------------------------------------------

    def test_many_employees(self):
        from django.db.models import Count

        for i in range(3, 13):
            Employee.objects.create(
                employee_code=f"REPORT{i:03d}",
                first_name=f"Employee{i}",
                last_name="Test",
                email=f"employee{i}.report@example.com",
                phone=f"93333333{i:02d}",
                department=self.department,
                designation="Developer",
                salary=40000 + (i * 1000),
                joining_date=date(2026, 1, 10),
                is_active=True,
            )

        result = Department.objects.annotate(
            employee_count=Count("employees")
        ).get(
            id=self.department.id
        )

        self.assertEqual(
            result.employee_count,
            12,
        )

    # --------------------------------------------------------
    # PROJECT WITHOUT EMPLOYEES
    # --------------------------------------------------------

    def test_project_without_employees(self):
        from django.db.models import Count

        result = Project.objects.annotate(
            employee_count=Count(
                "employees",
                distinct=True,
            )
        ).get(
            id=self.project.id
        )

        self.assertEqual(
            result.employee_count,
            0,
        )

    # --------------------------------------------------------
    # EMPLOYEES WITHOUT PROJECTS
    # --------------------------------------------------------

    def test_employees_without_projects(self):
        from django.db.models import Count

        employees_without_projects = Employee.objects.annotate(
            project_count=Count(
                "projects",
                distinct=True,
            )
        ).filter(
            project_count=0
        )

        self.assertEqual(
            employees_without_projects.count(),
            2,
        )

    # --------------------------------------------------------
    # DEPARTMENT SALARY CALCULATION
    # --------------------------------------------------------

    def test_department_salary_calculation(self):
        from django.db.models import Avg, Count, Max

        result = Department.objects.annotate(
            employee_count=Count("employees"),
            average_salary=Avg("employees__salary"),
            maximum_salary=Max("employees__salary"),
        ).get(
            id=self.department.id
        )

        self.assertEqual(
            result.employee_count,
            2,
        )

        self.assertEqual(
            float(result.average_salary),
            55000.0,
        )

        self.assertEqual(
            float(result.maximum_salary),
            60000.0,
        )

    # --------------------------------------------------------
    # SALARY AGGREGATION
    # --------------------------------------------------------

    def test_salary_aggregation(self):
        from django.db.models import Avg, Count, Max, Min, Sum

        result = Employee.objects.aggregate(
            total_employees=Count("id"),
            average_salary=Avg("salary"),
            maximum_salary=Max("salary"),
            minimum_salary=Min("salary"),
            total_salary_expenditure=Sum("salary"),
        )

        self.assertEqual(
            result["total_employees"],
            2,
        )

        self.assertEqual(
            float(result["average_salary"]),
            55000.0,
        )

        self.assertEqual(
            float(result["maximum_salary"]),
            60000.0,
        )

        self.assertEqual(
            float(result["minimum_salary"]),
            50000.0,
        )

        self.assertEqual(
            float(result["total_salary_expenditure"]),
            110000.0,
        )

    # --------------------------------------------------------
    # PROJECT WITH EMPLOYEES
    # --------------------------------------------------------

    def test_project_with_employees(self):
        from django.db.models import Count

        self.project.employees.add(
            self.employee1,
            self.employee2,
        )

        result = Project.objects.annotate(
            employee_count=Count(
                "employees",
                distinct=True,
            )
        ).get(
            id=self.project.id
        )

        self.assertEqual(
            result.employee_count,
            2,
        )

    # --------------------------------------------------------
    # DB-004 QUERY OPTIMIZATION
    # --------------------------------------------------------

    def test_employee_details_query_count(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as context:
            response = self.client.get(
                "/api/v1/employees/details/"
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        # Optimized endpoint should use:
        # 1 query for Employee + Department + Profile
        # 1 query for Projects
        self.assertEqual(
            len(context.captured_queries),
            2,
        )