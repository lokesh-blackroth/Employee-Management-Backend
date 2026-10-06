import csv

from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "Export employees to a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            required=True,
            help="Output CSV file path.",
        )

    def handle(self, *args, **options):
        output = options["output"]

        fields = [
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "designation",
            "salary",
            "joining_date",
            "is_active",
        ]

        employees = Employee.objects.all().order_by("id")

        with open(
            output,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow(fields)

            for employee in employees:
                writer.writerow([
                    employee.employee_code,
                    employee.first_name,
                    employee.last_name,
                    employee.email,
                    employee.phone,
                    (
                        employee.department.name
                        if employee.department
                        else ""
                    ),
                    employee.designation,
                    employee.salary,
                    employee.joining_date,
                    employee.is_active,
                ])

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported {employees.count()} "
                f"employees to {output}"
            )
        )