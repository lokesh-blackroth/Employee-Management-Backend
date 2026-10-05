from django.urls import include, path

from .routers import router
from .views import (
    DepartmentSummaryView,
    LoginView,
    MyProfileView,
    ProjectSummaryView,
    RegistrationView,
    SalarySummaryView,
    EmployeeProfileView,
    HealthCheckView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # ========================================================
    # HEALTH CHECK
    # ========================================================

    path(
        "health/",
        HealthCheckView.as_view(),
        name="health",
    ),

    # ========================================================
    # EMPLOYEE ROUTER APIs
    # ========================================================

    path(
        "",
        include(router.urls),
    ),

    # ========================================================
    # MY PROFILE
    # SEC-003 RBAC OWNERSHIP
    # ========================================================

    path(
        "profile/me/",
        MyProfileView.as_view(),
        name="my-profile",
    ),

    # ========================================================
    # EMPLOYEE PROFILE
    # ========================================================

    path(
        "employees/<int:pk>/profile/",
        EmployeeProfileView.as_view(),
        name="employee-profile",
    ),

    # ========================================================
    # REPORTING APIs
    # ========================================================

    path(
        "reports/department-summary/",
        DepartmentSummaryView.as_view(),
        name="department-summary",
    ),

    path(
        "reports/project-summary/",
        ProjectSummaryView.as_view(),
        name="project-summary",
    ),

    path(
        "reports/salary-summary/",
        SalarySummaryView.as_view(),
        name="salary-summary",
    ),

    # ========================================================
    # AUTHENTICATION APIs
    # ========================================================

    path(
        "auth/register/",
        RegistrationView.as_view(),
        name="register",
    ),

    path(
        "auth/login/",
        LoginView.as_view(),
        name="login",
    ),

    # ========================================================
    # JWT APIs
    # ========================================================

    path(
        "auth/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]