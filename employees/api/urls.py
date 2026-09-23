from django.urls import include, path

from .routers import router
from .views import (
    DepartmentSummaryView,
    ProjectSummaryView,
    SalarySummaryView,
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
]