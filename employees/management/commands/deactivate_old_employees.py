from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from employees.models import Employee


class Command(BaseCommand):
    help = "Deactivate employees who joined more than 5 years ago."

    def handle(self, *args, **options):
        today = timezone.localdate()

        cutoff_date = date(
            today.year - 5,
            today.month,
            today.day,
        )

        employees = Employee.objects.filter(
            joining_date__lt=cutoff_date,
            is_active=True,
        )

        count = employees.update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Deactivated {count} employees who joined "
                f"before {cutoff_date}."
            )
        )