import logging
import time

from employee_management.celery import app
from employees.models import Employee
from employees.services.notification_service import (
    NotificationService,
)
from employees.services.task_lock_service import (
    TaskLockService,
)


logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(RuntimeError,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    soft_time_limit=30,
    time_limit=60,
)
def send_welcome_email(self, employee_id):
    """
    Send a welcome email for an employee.

    Task contract:
        employee_id: positive integer

    Idempotency:
        NotificationService checks for an existing successfully
        sent WELCOME notification before creating another one.

    Retry policy:
        RuntimeError failures are retried up to 3 times with
        exponential backoff and jitter.

    Time limits:
        Soft limit: 30 seconds.
        Hard limit: 60 seconds.
    """

    if not isinstance(employee_id, int) or employee_id <= 0:
        raise ValueError(
            "employee_id must be a positive integer"
        )

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
        raise ValueError(
            f"Employee {employee_id} does not exist"
        )

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

    logger.info(
        "Welcome email processed successfully for employee_id=%s",
        employee_id,
    )

    return f"Welcome email processed for {employee.email}"


@app.task(
    expires=600,
    soft_time_limit=120,
    time_limit=180,
)
def generate_employee_report():
    """
    Generate the employee report.

    Task expiration:
        600 seconds.

    Time limits:
        Soft limit: 120 seconds.
        Hard limit: 180 seconds.
    """

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


@app.task(
    expires=600,
    soft_time_limit=120,
    time_limit=180,
)
def process_employee_csv(csv_file_path):
    """
    Process an employee CSV file.

    Task expiration:
        600 seconds.

    Time limits:
        Soft limit: 120 seconds.
        Hard limit: 180 seconds.
    """

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


@app.task(
    bind=True,
    expires=240,
    soft_time_limit=30,
    time_limit=60,
)
def scheduled_employee_summary(self):
    """
    Generate the scheduled employee summary.

    Queue:
        maintenance

    Task expiration:
        240 seconds.

    Overlap protection:
        A Redis-backed lock prevents multiple instances
        of this scheduled task from running simultaneously.

    Time limits:
        Soft limit: 30 seconds.
        Hard limit: 60 seconds.
    """

    lock = TaskLockService.acquire(
        "scheduled_employee_summary",
        timeout=300,
    )

    if lock is None:
        logger.warning(
            "Scheduled employee summary skipped: "
            "another execution is already running"
        )

        return {
            "status": "skipped",
            "reason": "already_running",
        }

    start_time = time.perf_counter()

    logger.info(
        "Scheduled employee summary started"
    )

    try:
        active_count = Employee.objects.filter(
            is_active=True
        ).count()

        inactive_count = Employee.objects.filter(
            is_active=False
        ).count()

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
            "Scheduled employee summary failed: "
            "duration=%.4f seconds",
            duration,
        )

        raise

    finally:
        TaskLockService.release(lock)