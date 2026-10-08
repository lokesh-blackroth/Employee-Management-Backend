import logging

from django.core.mail import send_mail

from employee_management.celery import app
from employees.models import Employee


logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    max_retries=3,
)
def send_welcome_email(self, employee_id):
    logger.info(
        "Starting welcome email task for employee_id=%s",
        employee_id,
    )

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        logger.error(
            "Employee not found: employee_id=%s",
            employee_id,
        )
        raise

    try:
        send_mail(
            subject="Welcome to the Company",
            message=f"Hello {employee.first_name}, welcome to the company!",
            from_email=None,
            recipient_list=[employee.email],
        )
    except Exception as exc:
        logger.exception(
            "Welcome email failed for employee_id=%s",
            employee_id,
        )

        raise self.retry(
            exc=exc,
            countdown=2 ** self.request.retries,
        )

    logger.info(
        "Welcome email sent successfully to employee_id=%s",
        employee_id,
    )

    return f"Welcome email sent to {employee.email}"


@app.task
def generate_employee_report():
    logger.info("Starting employee report generation")

    employees = Employee.objects.select_related("department").values(
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department__name",
        "designation",
        "salary",
        "joining_date",
        "is_active",
    )

    report = []

    for employee in employees:
        report.append(
            {
                "employee_code": employee["employee_code"],
                "first_name": employee["first_name"],
                "last_name": employee["last_name"],
                "email": employee["email"],
                "department__name": employee["department__name"],
                "designation": employee["designation"],
                "salary": (
                    str(employee["salary"])
                    if employee["salary"] is not None
                    else None
                ),
                "joining_date": (
                    employee["joining_date"].isoformat()
                    if employee["joining_date"] is not None
                    else None
                ),
                "is_active": employee["is_active"],
            }
        )

    logger.info(
        "Employee report generated successfully: %s employees",
        len(report),
    )

    return {
        "status": "success",
        "employee_count": len(report),
        "report": report,
    }


@app.task
def process_employee_csv(csv_file_path):
    logger.info(
        "Starting employee CSV processing: %s",
        csv_file_path,
    )

    try:
        import csv

        from employees.services.csv_employee_service import (
            EmployeeCSVImportService,
        )

        service = EmployeeCSVImportService()

        with open(
            csv_file_path,
            "r",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            rows = [
                (row_number, row)
                for row_number, row in enumerate(reader, start=2)
            ]

        result = service.import_rows(rows)

        logger.info(
            "Employee CSV processing completed: %s",
            result,
        )

        return result

    except Exception:
        logger.exception(
            "Employee CSV processing failed: %s",
            csv_file_path,
        )
        raise