from django.urls import include, path

from .routers import router
from .views import (
    DepartmentSummaryView,
    LoginView,
    ProjectSummaryView,
    RegistrationView,
    SalarySummaryView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("", include(router.urls)),

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