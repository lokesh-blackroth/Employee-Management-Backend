import json
import logging

from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Employee
from .forms import EmployeeForm


logger = logging.getLogger(__name__)


def health_check(request):
    return JsonResponse({
        "status": "success",
        "message": "Employee Management Backend is running"
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def employee_list(request):

    # READ - Get all employees
    if request.method == "GET":
        employees = Employee.objects.all()

        search = request.GET.get("search")
        department = request.GET.get("department")
        is_active = request.GET.get("is_active")

        if search:
            employees = employees.filter(
                models.Q(employee_code__icontains=search)
                | models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
                | models.Q(email__icontains=search)
            )

        if department:
            employees = employees.filter(
                department__iexact=department
            )

        if is_active is not None:
            if is_active.lower() == "true":
                employees = employees.filter(is_active=True)
            elif is_active.lower() == "false":
                employees = employees.filter(is_active=False)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "is_active must be true or false"
                }, status=400)

        data = [
            model_to_dict(employee)
            for employee in employees
        ]

        return JsonResponse({
            "status": "success",
            "employees": data
        })

    # CREATE - Create employee
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON data received")
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)

    form = EmployeeForm(data)

    if form.is_valid():
        employee = form.save()
        logger.info("Employee created: %s", employee.employee_code)

        return JsonResponse({
            "status": "success",
            "message": "Employee created successfully",
            "employee": model_to_dict(employee)
        }, status=201)

    return JsonResponse({
        "status": "error",
        "errors": form.errors
    }, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def employee_detail(request, id):

    try:
        employee = Employee.objects.get(id=id)
    except Employee.DoesNotExist:
        logger.warning("Employee not found: %s", id)
        return JsonResponse({
            "status": "error",
            "message": "Employee not found"
        }, status=404)

    # READ - Get single employee
    if request.method == "GET":
        return JsonResponse({
            "status": "success",
            "employee": model_to_dict(employee)
        })

    # UPDATE
    if request.method in ["PUT", "PATCH"]:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON data received")
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON data"
            }, status=400)

        form = EmployeeForm(
            data,
            instance=employee
        )

        if form.is_valid():
            employee = form.save()
            logger.info("Employee updated: %s", employee.employee_code)

            return JsonResponse({
                "status": "success",
                "message": "Employee updated successfully",
                "employee": model_to_dict(employee)
            })

        return JsonResponse({
            "status": "error",
            "errors": form.errors
        }, status=400)

    # DELETE
    if request.method == "DELETE":
        logger.info("Employee deleted: %s", employee.employee_code)
        employee.delete()

        return JsonResponse({
            "status": "success",
            "message": "Employee deleted successfully"
        })

def get_queryset(self):

    queryset = Employee.objects.all()

    if (
        self.request.user.is_authenticated
        and hasattr(self.request.user, "user_role")
        and self.request.user.user_role.role == "MANAGER"
    ):
        try:
            manager_employee = self.request.user.employee

            queryset = queryset.filter(
                department=manager_employee.department
            )

        except Employee.DoesNotExist:
            queryset = queryset.none()

    return queryset
class HealthCheckView(APIView):
    permission_classes = []

def get(self, request):
        return Response({
            "status": "success",
            "message": "Employee Management Backend is running"
        })
    