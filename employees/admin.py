from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee_code",
        "first_name",
        "last_name",
        "email",
    )

    search_fields = (
        "employee_code",
        "first_name",
        "last_name",
        "email",
    )

    list_filter = ()

    ordering = (
        "id",
    )