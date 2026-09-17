from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from employees.models import Employee
from .serializers import EmployeeSerializer


class EmployeeListAPIView(ListCreateAPIView):
    """
    GET  /api/v1/employees/
    POST /api/v1/employees/
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/employees/<employee_id>/
    PUT    /api/v1/employees/<employee_id>/
    PATCH  /api/v1/employees/<employee_id>/
    DELETE /api/v1/employees/<employee_id>/
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "id"
    lookup_url_kwarg = "employee_id"