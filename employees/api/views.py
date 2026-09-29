from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
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

from employees.api.serializers import (
    EmployeeSerializer,
    EmployeeTransferSerializer,
)

from employees.models import (
    Employee,
    EmployeeProfile,
    EmployeeTransfer,
)

from employees.services import EmployeeTransferService


# ============================================================
# EMPLOYEE VIEWSET
# ============================================================

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # JWT protection
    permission_classes = [IsAuthenticated]

    # Filtering
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

    # ========================================================
    # ACTIVE EMPLOYEES
    # ========================================================

    @action(
        detail=False,
        methods=["get"],
    )
    def active(self, request):

        employees = self.get_queryset().filter(
            is_active=True
        )

        serializer = self.get_serializer(
            employees,
            many=True,
        )

        return Response(serializer.data)

    # ========================================================
    # EMPLOYEE DETAILS
    # DB-004 QUERY OPTIMIZATION
    # ========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="details",
    )
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

    # ========================================================
    # EMPLOYEE TRANSFER
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="transfer",
    )
    def transfer(self, request, pk=None):

        to_department = request.data.get(
            "to_department"
        )

        reason = request.data.get(
            "reason"
        )

        if not to_department:

            return Response(
                {
                    "detail": (
                        "Target department is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        transferred_by = (
            request.user
            if request.user.is_authenticated
            else User.objects.first()
        )

        if transferred_by is None:

            return Response(
                {
                    "detail": (
                        "No user exists to record "
                        "the transfer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            transfer = (
                EmployeeTransferService
                .transfer_employee(
                    employee_id=pk,
                    to_department_id=to_department,
                    reason=reason,
                    transferred_by=transferred_by,
                )
            )

            return Response(
                EmployeeTransferSerializer(
                    transfer
                ).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # ========================================================
    # TRANSFER HISTORY
    # ========================================================

    @action(
        detail=True,
        methods=["get"],
        url_path="transfer-history",
    )
    def transfer_history(
        self,
        request,
        pk=None,
    ):

        transfers = (
            EmployeeTransfer.objects
            .filter(
                employee_id=pk
            )
            .select_related(
                "from_department",
                "to_department",
                "transferred_by",
            )
            .order_by(
                "-transferred_at"
            )
        )

        serializer = EmployeeTransferSerializer(
            transfers,
            many=True,
        )

        return Response(
            serializer.data
        )


# ============================================================
# REPORTING APIs
# ============================================================

class DepartmentSummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = get_department_summary()

        return Response(data)


class ProjectSummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = get_project_summary()

        return Response(data)


class SalarySummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = get_salary_summary()

        return Response(data)


# ============================================================
# USER REGISTRATION
# ============================================================

class RegistrationView(APIView):

    def post(self, request):

        serializer = RegistrationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": (
                        "User registered successfully."
                    ),
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ============================================================
# USER LOGIN
# ============================================================

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
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED,
        )