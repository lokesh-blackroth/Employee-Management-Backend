from django.test import TestCase
from django.urls import reverse

from .models import Employee


class EmployeeAPITestCase(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            employee_code="EMP001",
            first_name="Rahul",
            last_name="Sharma",
            email="rahul@example.com",
            phone="9876543210",
            department="IT",
            designation="Software Engineer",
            salary=60000,
            joining_date="2024-01-15",
            is_active=True
        )

        self.list_url = reverse("employee-list")
        self.detail_url = reverse(
            "employee-detail",
            kwargs={"employee_id": self.employee.id}
        )

    def test_create_employee(self):
        data = {
            "employee_code": "EMP002",
            "first_name": "Priya",
            "last_name": "Kumar",
            "email": "priya@example.com",
            "phone": "9876543211",
            "department": "HR",
            "designation": "HR Executive",
            "salary": 50000,
            "joining_date": "2024-02-15",
            "is_active": True
        }

        response = self.client.post(
            self.list_url,
            data=data,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Employee.objects.count(), 2)

    def test_list_employees(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)

    def test_view_employee(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["employee_code"],
            "EMP001"
        )

    def test_update_employee_put(self):
        data = {
            "employee_code": "EMP001",
            "first_name": "Rahul",
            "last_name": "Sharma",
            "email": "rahul@example.com",
            "phone": "9876543210",
            "department": "IT",
            "designation": "Senior Software Engineer",
            "salary": 70000,
            "joining_date": "2024-01-15",
            "is_active": True
        }

        response = self.client.put(
            self.detail_url,
            data=data,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.designation,
            "Senior Software Engineer"
        )
        self.assertEqual(
            float(self.employee.salary),
            70000.0
        )

    def test_update_employee_patch(self):
        response = self.client.patch(
            self.detail_url,
            data={"salary": 65000},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        self.employee.refresh_from_db()

        self.assertEqual(
            float(self.employee.salary),
            65000.0
        )

    def test_delete_employee(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Employee.objects.count(), 0)

    def test_employee_not_found(self):
        response = self.client.get(
            reverse(
                "employee-detail",
                kwargs={"employee_id": 99999}
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_missing_required_field(self):
        data = {
            "first_name": "Test",
            "last_name": "User"
        }

        response = self.client.post(
            self.list_url,
            data=data,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_email(self):
        data = {
            "employee_code": "EMP002",
            "first_name": "Duplicate",
            "last_name": "User",
            "email": "rahul@example.com",
            "phone": "9876543212",
            "department": "IT",
            "designation": "Developer",
            "salary": 50000,
            "joining_date": "2024-03-15",
            "is_active": True
        }

        response = self.client.post(
            self.list_url,
            data=data,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)