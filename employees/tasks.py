import logging
import time

from employee_management.celery import app
from employees.models import Employee
from employees.services.notification_service import (
    NotificationService,
)


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
        notification = NotificationService.send_welcome_notification(
            employee
        )

        if notification is None:
            logger.warning(
                "Welcome notification skipped because employee has no user: "
                "employee_id=%s",
                employee_id,
            )
            return "Welcome notification skipped"

        if not notification.email_sent:
            raise RuntimeError(
                notification.email_error
                or "Welcome email failed"
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
        "Welcome email processed successfully for employee_id=%s",
        employee_id,
    )

    return (
        f"Welcome email processed for {employee.email}"
    )


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
    
@app.task
def scheduled_employee_summary():
    start_time = time.perf_counter()

    logger.info("Scheduled employee summary started")

    try:
        active_count = Employee.objects.filter(is_active=True).count()
        inactive_count = Employee.objects.filter(is_active=False).count()

        duration = time.perf_counter() - start_time

        logger.info(
            "Scheduled employee summary finished: "
            "active=%s, inactive=%s, duration=%.4f seconds",
            active_count,
            inactive_count,
            duration,
        )

        return {
            "status": "success",
            "active_employees": active_count,
            "inactive_employees": inactive_count,
        }

    except Exception:
        duration = time.perf_counter() - start_time

        logger.exception(
            "Scheduled employee summary failed: duration=%.4f seconds",
            duration,
        )
        raise

