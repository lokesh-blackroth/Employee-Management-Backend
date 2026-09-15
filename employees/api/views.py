from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.models import Employee
from .serializers import EmployeeSerializer


class EmployeeListAPIView(APIView):

    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class EmployeeDetailAPIView(APIView):

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployeeSerializer(employee)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )