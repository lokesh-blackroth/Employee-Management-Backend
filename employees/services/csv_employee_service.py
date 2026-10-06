import re
from decimal import Decimal, InvalidOperation

from django.db import transaction

from employees.models import Employee


REQUIRED_COLUMNS = {
    "employee_code",
    "first_name",
    "last_name",
    "email",
    "phone",
    "designation",
    "salary",
    "joining_date",
}


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


class EmployeeCSVImportService:

    def validate_headers(self, headers):
        missing_columns = REQUIRED_COLUMNS - set(headers or [])

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        return True

    def validate_row(self, row):
        errors = []

        required_fields = [
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "phone",
            "designation",
            "salary",
            "joining_date",
        ]

        for field in required_fields:
            value = row.get(field, "")

            if not value or not value.strip():
                errors.append(f"{field} is required")

        email = row.get("email", "").strip()

        if email and not EMAIL_PATTERN.match(email):
            errors.append("invalid email")

        salary = row.get("salary", "").strip()

        if salary:
            try:
                Decimal(salary)
            except InvalidOperation:
                errors.append("invalid salary")

        return errors

    def check_duplicate(self, row):
        employee_code = row.get("employee_code", "").strip()
        email = row.get("email", "").strip()

        return (
            Employee.objects.filter(
                employee_code=employee_code
            ).exists()
            or
            Employee.objects.filter(
                email=email
            ).exists()
        )

    def import_rows(self, rows, atomic=False):
        if atomic:
            with transaction.atomic():
                results = self._process_rows(rows)

                if results["failed"] > 0:
                    raise ValueError(
                        "Import failed. All changes were rolled back."
                    )

                return results

        return self._process_rows(rows)

    def _process_rows(self, rows):
        results = {
            "successful": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }

        for row_number, row in rows:
            errors = self.validate_row(row)

            if errors:
                results["failed"] += 1
                results["errors"].append({
                    "row": row_number,
                    "errors": errors,
                })
                continue

            if self.check_duplicate(row):
                results["skipped"] += 1
                continue

            try:
                Employee.objects.create(
                    employee_code=row["employee_code"].strip(),
                    first_name=row["first_name"].strip(),
                    last_name=row["last_name"].strip(),
                    email=row["email"].strip(),
                    phone=row["phone"].strip(),
                    designation=row["designation"].strip(),
                    salary=Decimal(row["salary"].strip()),
                    joining_date=row["joining_date"].strip(),
                )

                results["successful"] += 1

            except Exception as exc:
                results["failed"] += 1
                results["errors"].append({
                    "row": row_number,
                    "errors": [str(exc)],
                })

        return results