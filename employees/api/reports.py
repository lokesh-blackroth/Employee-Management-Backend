from django.db.models import Count, Sum, Avg, Min, Max

from employees.models import Department, Project, Employee


def get_department_summary():
    departments = Department.objects.annotate(
        employee_count=Count("employees"),
        average_salary=Avg("employees__salary"),
        maximum_salary=Max("employees__salary"),
    )

    return list(
        departments.values(
            "name",
            "employee_count",
            "average_salary",
            "maximum_salary",
        )
    )


def get_project_summary():
    projects = Project.objects.annotate(
        employee_count=Count("employees", distinct=True),
    )

    return list(
        projects.values(
            "name",
            "project_code",
            "employee_count",
        )
    )
def get_salary_summary():
    return Employee.objects.aggregate(
        total_employees=Count("id"),
        average_salary=Avg("salary"),
        maximum_salary=Max("salary"),
        minimum_salary=Min("salary"),
        total_salary_expenditure=Sum("salary"),
    )