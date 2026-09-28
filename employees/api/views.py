from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.api.auth_serializers import (
    LoginSerializer,
    RegistrationSerializer,
)
from employees.api.reports import (
    get_department_summary,
    get_project_summary,
    get_salary_summary,
)
from employees.api.serializers import EmployeeSerializer
from employees.models import Employee, EmployeeProfile


class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "department",
        "is_active",
        "salary",
    ]

    search_fields = [
        "first_name",
        "last_name",
        "email",
        "employee_code",
        "department__name",
    ]

    ordering_fields = [
        "salary",
        "joining_date",
    ]

    @action(detail=False, methods=["get"])
    def active(self, request):

        employees = self.get_queryset().filter(
            is_active=True
        )

        serializer = self.get_serializer(
            employees,
            many=True,
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="details")
    def details(self, request):

        employees = (
            Employee.objects
            .select_related(
                "department",
                "profile",
            )
            .prefetch_related(
                "projects"
            )
        )

        data = []

        for employee in employees:

            try:
                profile = employee.profile
            except EmployeeProfile.DoesNotExist:
                profile = None

            data.append({
                "id": employee.id,
                "employee_code": employee.employee_code,
                "name": (
                    f"{employee.first_name} "
                    f"{employee.last_name}"
                ),
                "department": (
                    employee.department.name
                    if employee.department
                    else None
                ),
                "profile": {
                    "address": (
                        profile.address
                        if profile
                        else None
                    ),
                    "blood_group": (
                        profile.blood_group
                        if profile
                        else None
                    ),
                    "emergency_contact": (
                        profile.emergency_contact
                        if profile
                        else None
                    ),
                },
                "projects": [
                    project.name
                    for project in employee.projects.all()
                ],
            })

        return Response(data)


class DepartmentSummaryView(APIView):

    def get(self, request):

        data = get_department_summary()

        return Response(data)


class ProjectSummaryView(APIView):

    def get(self, request):

        data = get_project_summary()

        return Response(data)


class SalarySummaryView(APIView):

    def get(self, request):

        data = get_salary_summary()

        return Response(data)


class RegistrationView(APIView):

    def post(self, request):

        serializer = RegistrationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully.",
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            return Response(
                {
                    "message": "Login successful.",
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )