from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "Seed sample employees into the database safely."

    def handle(self, *args, **options):
        employees = [
            {
                "employee_code": "SEED001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "9876543210",
                "designation": "Software Engineer",
                "salary": Decimal("50000.00"),
                "joining_date": date(2025, 1, 10),
            },
            {
                "employee_code": "SEED002",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "phone": "9876543211",
                "designation": "QA Engineer",
                "salary": Decimal("55000.00"),
                "joining_date": date(2025, 2, 15),
            },
            {
                "employee_code": "SEED003",
                "first_name": "Mike",
                "last_name": "Johnson",
                "email": "mike.johnson@example.com",
                "phone": "9876543212",
                "designation": "Backend Developer",
                "salary": Decimal("60000.00"),
                "joining_date": date(2025, 3, 20),
            },
        ]

        created = 0
        skipped = 0

        for employee_data in employees:
            employee_code = employee_data["employee_code"]

            if Employee.objects.filter(
                employee_code=employee_code
            ).exists():
                skipped += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped existing employee: {employee_code}"
                    )
                )

                continue

            Employee.objects.create(**employee_data)

            created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created employee: {employee_code}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding completed. Created: {created}, "
                f"Skipped: {skipped}"
            )
        )