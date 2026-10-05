from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.api.permissions import (
    IsAdmin,
    IsAdminOrHR,
    IsAdminHROrManager,
)

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
    EmployeeProfileSerializer,
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

    # ========================================================
    # ROLE-BASED PERMISSIONS
    # ========================================================

    def get_permissions(self):

        if self.action == "destroy":
            permission_classes = [IsAdmin]

        elif self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            permission_classes = [IsAdminOrHR]

        elif self.action in [
            "list",
            "retrieve",
            "active",
            "details",
            "transfer",
            "transfer_history",
        ]:
            permission_classes = [IsAdminHROrManager]

        else:
            permission_classes = [IsAuthenticated]

        return [
            permission()
            for permission in permission_classes
        ]

    # ========================================================
    # MANAGER SCOPE
    # ========================================================

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

    # ========================================================
    # FILTERING
    # ========================================================

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
            self.get_queryset()
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

            data.append(
                {
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
                }
            )

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

        employee_queryset = self.get_queryset()

        if not employee_queryset.filter(pk=pk).exists():
            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

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

        if not self.get_queryset().filter(
            pk=pk
        ).exists():

            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

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

    # Salary reporting is restricted to ADMIN.
    permission_classes = [IsAdmin]

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


# ============================================================
# MY PROFILE API
# SEC-003 RBAC OWNERSHIP
# ============================================================

class MyProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get_employee(self, request):

        try:
            return (
                Employee.objects
                .select_related(
                    "department",
                    "profile",
                )
                .get(
                    user=request.user
                )
            )

        except Employee.DoesNotExist:
            return None

    def get(self, request):

        employee = self.get_employee(request)

        if employee is None:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            profile = employee.profile

        except EmployeeProfile.DoesNotExist:
            profile = None
             

        return Response(
            {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "phone": employee.phone,
                "department": (
                    employee.department.name
                    if employee.department
                    else None
                ),
                "designation": employee.designation,
                "joining_date": employee.joining_date,
                "is_active": employee.is_active,
                "profile": EmployeeProfileSerializer(
                    profile
                ).data,
            }
        )

    def patch(self, request):

        employee = self.get_employee(request)

        if employee is None:
            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            profile = employee.profile

        except EmployeeProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ============================================================
# EMPLOYEE PROFILE API
# SEC-005 OBJECT-LEVEL AUTHORIZATION
# ============================================================

class EmployeeProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get_employee(self, request, pk):

        try:
            return (
                Employee.objects
                .select_related(
                    "department",
                    "profile",
                    "user",
                )
                .get(pk=pk)
            )

        except Employee.DoesNotExist:
            return None

    def check_access(
        self,
        request,
        employee,
    ):

        user = request.user

        if not hasattr(user, "user_role"):
            return False, "You do not have permission to access this profile."

        role = user.user_role.role

        # ADMIN has full access.
        if role == "ADMIN":
            return True, None

        # HR can manage employee profiles.
        if role == "HR":
            return True, None

        # EMPLOYEE can access only their own profile.
        if role == "EMPLOYEE":

            try:
                own_employee = user.employee

            except Employee.DoesNotExist:
                return False, "Employee profile not found."

            if own_employee.id == employee.id:
                return True, None

            return False, "You can access only your own profile."

        # Managers are not given profile-management access.
        return False, "You do not have permission to access this profile."

    def get(self, request, pk):

        employee = self.get_employee(
            request,
            pk
        )

        if employee is None:
            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        allowed, message = self.check_access(
            request,
            employee,
        )

        if not allowed:
            return Response(
                {
                    "detail": message
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            profile = employee.profile

        except EmployeeProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "employee": {
                    "id": employee.id,
                    "employee_code": employee.employee_code,
                    "first_name": employee.first_name,
                    "last_name": employee.last_name,
                    "email": employee.email,
                    "phone": employee.phone,
                    "department": (
                        employee.department.name
                        if employee.department
                        else None
                    ),
                    "designation": employee.designation,
                    "joining_date": employee.joining_date,
                    "is_active": employee.is_active,
                },
                "profile": EmployeeProfileSerializer(
                    profile
                ).data,
            }
        )

    def patch(self, request, pk):

        employee = self.get_employee(
            request,
            pk
        )

        if employee is None:
            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        allowed, message = self.check_access(
            request,
            employee,
        )

        if not allowed:
            return Response(
                {
                    "detail": message
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            profile = employee.profile

        except EmployeeProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({
            "status": "success",
            "message": "Employee Management Backend is running"
        })