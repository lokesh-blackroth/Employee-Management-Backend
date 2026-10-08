from datetime import date
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from employees.models import UserRole
from employees.models import Notification
from employees.services.notification_service import NotificationService
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

        # ----------------------------------------------------
        # ADMIN TEST USER
        # ----------------------------------------------------

        self.user = User.objects.create_user(
            username="admin_test",
            password="Test@12345",
        )

        UserRole.objects.create(
            user=self.user,
            role="ADMIN",
        )

        self.client.force_authenticate(
            user=self.user
        )

        # ----------------------------------------------------
        # DEPARTMENT
        # ----------------------------------------------------

        self.department = Department.objects.create(
            name="Test Department",
            code="TEST_DEPT",
            description="Department for automated tests",
        )

        # ----------------------------------------------------
        # EMPLOYEE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # URLS
        # ----------------------------------------------------

        self.list_url = reverse(
            "employee-list"
        )

        self.detail_url = reverse(
            "employee-detail",
            kwargs={
                "pk": self.employee.id
            },
        )

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    def test_employee_list(self):

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------------

    def test_employee_detail(self):

        response = self.client.get(
            self.detail_url
        )

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
            "joining_date": str(
                self.employee.joining_date
            ),
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

        response = self.client.delete(
            self.detail_url
        )

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
            kwargs={
                "pk": 99999
            },
        )

        response = self.client.get(
            url
        )

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

        self.employee1.projects.add(
            self.project
        )

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

        # ----------------------------------------------------
        # ADMIN TEST USER
        # ----------------------------------------------------

        self.user = User.objects.create_user(
            username="reportuser",
            password="Test@12345",
        )

        UserRole.objects.create(
            user=self.user,
            role="ADMIN",
        )

        self.client.force_authenticate(
            user=self.user
        )

        # ----------------------------------------------------
        # DEPARTMENT
        # ----------------------------------------------------

        self.department = Department.objects.create(
            name="Reporting Department",
            code="REPORT_DEPT",
            description="Department for ORM reporting tests",
        )

        # ----------------------------------------------------
        # EMPLOYEES
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # PROJECT
        # ----------------------------------------------------

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

        employees_without_projects = (
            Employee.objects
            .annotate(
                project_count=Count(
                    "projects",
                    distinct=True,
                )
            )
            .filter(
                project_count=0
            )
        )

        self.assertEqual(
            employees_without_projects.count(),
            2,
        )

    # --------------------------------------------------------
    # DEPARTMENT SALARY CALCULATION
    # --------------------------------------------------------

    def test_department_salary_calculation(self):

        from django.db.models import (
            Avg,
            Count,
            Max,
        )

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

        from django.db.models import (
            Avg,
            Count,
            Max,
            Min,
            Sum,
        )

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
        from django.test.utils import (
            CaptureQueriesContext,
        )

        with CaptureQueriesContext(
            connection
        ) as context:

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
      
# ============================================================
# RBAC TESTS
# ============================================================

class RBACTestCase(APITestCase):

    def setUp(self):

        # ----------------------------------------------------
        # DEPARTMENTS
        # ----------------------------------------------------

        self.hr_department = Department.objects.create(
            name="RBAC HR",
            code="RBAC_HR",
            description="RBAC HR test department",
        )

        self.tech_department = Department.objects.create(
            name="RBAC Technology",
            code="RBAC_TECH",
            description="RBAC technology test department",
        )

        # ----------------------------------------------------
        # USERS
        # ----------------------------------------------------

        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="Test@12345",
        )

        self.hr_user = User.objects.create_user(
            username="hr_test",
            password="Test@12345",
        )

        self.manager_user = User.objects.create_user(
            username="manager_test",
            password="Test@12345",
        )

        self.employee_user = User.objects.create_user(
            username="employee_test",
            password="Test@12345",
        )

        # ----------------------------------------------------
        # ROLES
        # ----------------------------------------------------

        UserRole.objects.create(
            user=self.admin_user,
            role="ADMIN",
        )

        UserRole.objects.create(
            user=self.hr_user,
            role="HR",
        )

        UserRole.objects.create(
            user=self.manager_user,
            role="MANAGER",
        )

        UserRole.objects.create(
            user=self.employee_user,
            role="EMPLOYEE",
        )

        # ----------------------------------------------------
        # EMPLOYEE RECORDS
        # ----------------------------------------------------

        self.admin_employee = Employee.objects.create(
            user=self.admin_user,
            employee_code="ADMIN001",
            first_name="Admin",
            last_name="Test",
            email="admin@test.com",
            phone="9000000001",
            department=self.hr_department,
            designation="Administrator",
            salary=80000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        self.hr_employee = Employee.objects.create(
            user=self.hr_user,
            employee_code="HR001",
            first_name="HR",
            last_name="Test",
            email="hr@test.com",
            phone="9000000002",
            department=self.hr_department,
            designation="HR Executive",
            salary=60000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        self.manager_employee = Employee.objects.create(
            user=self.manager_user,
            employee_code="MANAGER001",
            first_name="Manager",
            last_name="Test",
            email="manager@test.com",
            phone="9000000003",
            department=self.tech_department,
            designation="Manager",
            salary=70000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        self.employee = Employee.objects.create(
            user=self.employee_user,
            employee_code="EMP001",
            first_name="Employee",
            last_name="Test",
            email="employee@test.com",
            phone="9000000004",
            department=self.tech_department,
            designation="Developer",
            salary=50000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        # ----------------------------------------------------
        # PROFILE URL
        # ----------------------------------------------------

        self.profile_url = reverse("my-profile")

    # ========================================================
    # EMPLOYEE OWN PROFILE
    # ========================================================

    def test_employee_can_access_own_profile(self):

        self.client.force_authenticate(
            user=self.employee_user
        )

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["employee_code"],
            "EMP001",
        )

    # ========================================================
    # EMPLOYEE CANNOT ACCESS ANOTHER EMPLOYEE
    # ========================================================

    def test_employee_cannot_access_another_employee_profile(self):

        self.client.force_authenticate(
            user=self.employee_user
        )

        # Employee A accesses own profile
        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["employee_code"],
            "EMP001",
        )

        # Create Employee B
        other_employee_user = User.objects.create_user(
            username="employee_b",
            password="Test@12345",
        )

        UserRole.objects.create(
            user=other_employee_user,
            role="EMPLOYEE",
        )

        Employee.objects.create(
            user=other_employee_user,
            employee_code="EMP002",
            first_name="Employee",
            last_name="B",
            email="employee_b@test.com",
            phone="9000000005",
            department=self.tech_department,
            designation="Tester",
            salary=50000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

        # Employee A requests /profile/me/
        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        # Still Employee A's profile
        self.assertEqual(
            response.data["employee_code"],
            "EMP001",
        )

        self.assertNotEqual(
            response.data["employee_code"],
            "EMP002",
        )

    # ========================================================
    # UNAUTHENTICATED ACCESS
    # ========================================================

    def test_unauthenticated_user_cannot_access_profile(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    # ========================================================
    # ADMIN CREATE
    # ========================================================

    def test_admin_can_create_employee(self):

        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.post(
            reverse("employee-list"),
            {
                "employee_code": "ADMIN_CREATE_001",
                "first_name": "New",
                "last_name": "Employee",
                "email": "newemployee@test.com",
                "phone": "9000000010",
                "department": self.tech_department.id,
                "designation": "Developer",
                "salary": "55000.00",
                "joining_date": "2026-01-01",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    # ========================================================
    # ADMIN DELETE
    # ========================================================

    def test_admin_can_delete_employee(self):

        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.delete(
            reverse(
                "employee-detail",
                kwargs={
                    "pk": self.employee.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )
            # ========================================================
    # HR VIEW
    # ========================================================

    def test_hr_can_view_employees(self):

        self.client.force_authenticate(
            user=self.hr_user
        )

        response = self.client.get(
            reverse("employee-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # ========================================================
    # HR CREATE
    # ========================================================

    def test_hr_can_create_employee(self):

        self.client.force_authenticate(
            user=self.hr_user
        )

        response = self.client.post(
            reverse("employee-list"),
            {
                "employee_code": "HR_CREATE_001",
                "first_name": "HR",
                "last_name": "Created",
                "email": "hrcreated@test.com",
                "phone": "9000000011",
                "department": self.tech_department.id,
                "designation": "Tester",
                "salary": "50000.00",
                "joining_date": "2026-01-01",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    # ========================================================
    # HR CANNOT DELETE
    # ========================================================

    def test_hr_cannot_delete_employee(self):

        self.client.force_authenticate(
            user=self.hr_user
        )

        response = self.client.delete(
            reverse(
                "employee-detail",
                kwargs={
                    "pk": self.employee.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )
    # ========================================================
    # MANAGER VIEW
    # ========================================================

    def test_manager_can_view_employees(self):

        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.get(
            reverse("employee-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # ========================================================
    # MANAGER CANNOT CREATE
    # ========================================================

    def test_manager_cannot_create_employee(self):

        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.post(
            reverse("employee-list"),
            {
                "employee_code": "MANAGER_CREATE_001",
                "first_name": "Manager",
                "last_name": "Created",
                "email": "managercreated@test.com",
                "phone": "9000000012",
                "department": self.tech_department.id,
                "designation": "Developer",
                "salary": "50000.00",
                "joining_date": "2026-01-01",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # ========================================================
    # MANAGER CANNOT DELETE
    # ========================================================

    def test_manager_cannot_delete_employee(self):

        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.delete(
            reverse(
                "employee-detail",
                kwargs={
                    "pk": self.employee.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )
            # ========================================================
    # MANAGER BUSINESS SCOPE
    # ========================================================

    def test_manager_cannot_view_employee_outside_scope(self):

        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.get(
            reverse(
                "employee-detail",
                kwargs={
                    "pk": self.hr_employee.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
class NotificationServiceTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="notification_test",
            password="Test@12345",
            email="notification@example.com",
        )

        self.department = Department.objects.create(
            name="Notification Department",
            code="NOTIFY_DEPT",
        )

        self.employee = Employee.objects.create(
            user=self.user,
            employee_code="NOTIFY001",
            first_name="Notification",
            last_name="Employee",
            email="notification@example.com",
            phone="9876543210",
            department=self.department,
            designation="Developer",
            salary=50000,
            joining_date=date(2026, 1, 1),
            is_active=True,
        )

    def test_create_notification(self):
        notification = NotificationService.create_notification(
            recipient=self.user,
            notification_type="GENERAL",
            title="Test Notification",
            message="This is a test notification.",
        )

        self.assertIsNotNone(notification)
        self.assertEqual(
            notification.recipient,
            self.user,
        )
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.email_sent)

    def test_welcome_notification_sends_email(self):
        notification = NotificationService.send_welcome_notification(
            self.employee
        )

        self.assertIsNotNone(notification)
        self.assertTrue(notification.email_sent)
        self.assertEqual(
            Notification.objects.count(),
            1,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertIn(
            "Welcome",
            mail.outbox[0].subject,
        )

        self.assertIn(
            "Notification",
            mail.outbox[0].body,
        )

    def test_duplicate_welcome_notification(self):
        first_notification = (
            NotificationService.send_welcome_notification(
                self.employee
            )
        )

        second_notification = (
            NotificationService.send_welcome_notification(
                self.employee
            )
        )

        self.assertEqual(
            first_notification.id,
            second_notification.id,
        )

        self.assertEqual(
            Notification.objects.count(),
            1,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_missing_recipient_email(self):
        self.user.email = ""
        self.user.save(update_fields=["email"])

        notification = (
            NotificationService.send_welcome_notification(
                self.employee
            )
        )

        self.assertIsNotNone(notification)
        self.assertFalse(notification.email_sent)
        self.assertEqual(
            notification.email_error,
            "Recipient email is missing.",
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_missing_template_records_failure(self):
        notification = NotificationService.create_notification(
            recipient=self.user,
            notification_type="WELCOME",
            title="Test Welcome",
            message="Test welcome message.",
        )

        result = NotificationService.send_email(
            notification=notification,
            subject="Test Welcome",
            template_name="emails/template_that_does_not_exist.html",
            context={
                "employee": self.employee,
            },
        )

        notification.refresh_from_db()

        self.assertFalse(result)
        self.assertFalse(notification.email_sent)
        self.assertTrue(notification.email_error)

    def test_welcome_email_html_rendering(self):
        notification = NotificationService.send_welcome_notification(
            self.employee
        )

        self.assertTrue(notification.email_sent)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.content_subtype,
            "plain",
        )

        self.assertEqual(len(email.alternatives), 1)

        html_content = email.alternatives[0].content

        self.assertIn(
            self.employee.first_name,
            html_content,
        )

        self.assertIn(
            self.employee.employee_code,
            html_content,
        )

    @patch(
        "employees.services.notification_service.EmailMultiAlternatives.send"
    )
    def test_email_sending_failure(self, mock_send):
        mock_send.side_effect = Exception(
            "SMTP configuration error"
        )

        notification = NotificationService.send_welcome_notification(
            self.employee
        )

        notification.refresh_from_db()

        self.assertFalse(notification.email_sent)

        self.assertIn(
            "SMTP configuration error",
            notification.email_error,
        )

class NotificationAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="api_notification_user",
            password="Test@12345",
            email="api_notification@example.com",
        )

        self.other_user = User.objects.create_user(
            username="other_notification_user",
            password="Test@12345",
            email="other_notification@example.com",
        )

        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type="GENERAL",
            title="Test Notification",
            message="This is a test notification.",
        )

        self.other_notification = Notification.objects.create(
            recipient=self.other_user,
            notification_type="GENERAL",
            title="Other Notification",
            message="This belongs to another user.",
        )

    def test_list_notifications(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "/api/v1/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["title"],
            "Test Notification",
        )

    def test_user_can_only_see_own_notifications(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "/api/v1/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.other_notification.id,
            notification_ids,
        )

    def test_mark_notification_as_read(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/v1/notifications/"
            f"{self.notification.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertTrue(
            response.data["is_read"]
        )

    def test_mark_notification_as_read_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.patch(
            f"/api/v1/notifications/"
            f"{self.notification.id}/read/"
        )

        second_response = self.client.patch(
            f"/api/v1/notifications/"
            f"{self.notification.id}/read/"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

    def test_invalid_notification_id(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            "/api/v1/notifications/999999/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_notification_list(self):
        response = self.client.get(
            "/api/v1/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        from unittest.mock import patch

from django.test import TestCase

from employees.models import Employee
from employees.tasks import (
    generate_employee_report,
    process_employee_csv,
    send_welcome_email,
)


class CeleryTaskTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.employee = Employee.objects.create(
            employee_code="CELERYTEST001",
            first_name="Celery",
            last_name="Test",
            email="celery.test@example.com",
            phone="9999999999",
            designation="Developer",
            salary=50000,
            joining_date="2026-01-01",
        )

    def test_send_welcome_email_success(self):
        with patch("employees.tasks.send_mail") as mock_send_mail:
            result = send_welcome_email.run(self.employee.id)

        mock_send_mail.assert_called_once()
        self.assertIn(self.employee.email, result)

    def test_send_welcome_email_invalid_employee(self):
        with self.assertRaises(Employee.DoesNotExist):
            send_welcome_email.run(999999)

    def test_generate_employee_report_success(self):
        result = generate_employee_report.run()

        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["employee_count"], 1)
        self.assertIsInstance(result["report"], list)

    def test_process_employee_csv_success(self):
        import csv
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "employee_code",
                "first_name",
                "last_name",
                "email",
                "phone",
                "designation",
                "salary",
                "joining_date",
            ])

            writer.writerow([
                "CELERYCSV001",
                "CSV",
                "Test",
                "celerycsv@example.com",
                "8888888888",
                "Developer",
                "55000",
                "2026-01-01",
            ])

            csv_path = csv_file.name

        result = process_employee_csv.run(csv_path)

        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["failed"], 0)
