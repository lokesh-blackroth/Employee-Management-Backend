from django.urls import path

from .views import EmployeeListAPIView, EmployeeDetailAPIView


urlpatterns = [
    path(
        'employees/',
        EmployeeListAPIView.as_view(),
        name='employee-list'
    ),
    path(
        'employees/<int:employee_id>/',
        EmployeeDetailAPIView.as_view(),
        name='employee-detail'
    ),
]