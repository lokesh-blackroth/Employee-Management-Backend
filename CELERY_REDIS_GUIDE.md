# Celery & Redis Background Processing

## Overview

The Employee Management Backend uses Celery for asynchronous background
processing and Redis as the message broker and result backend.

## Architecture

Django API
    |
    | Queue task
    v
Redis
    |
    | Deliver task
    v
Celery Worker
    |
    v
Background Task

## Configuration

Environment variables:

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1

Redis database 0 is used as the broker.

Redis database 1 is used as the Celery result backend.

## Starting Redis

Windows uses Memurai as the Redis-compatible server.

Verify Redis:

& "C:\Program Files\Memurai\memurai-cli.exe" ping

Expected:

PONG

## Starting the Celery Worker

Activate the virtual environment:

.\.venv\Scripts\Activate.ps1

Start the worker:

celery -A employee_management worker --loglevel=INFO --pool=solo

The `solo` pool is used for Windows compatibility.

## Starting Django

python manage.py runserver

## Registered Tasks

### send_welcome_email

Sends a welcome email asynchronously for an employee.

The task receives the employee ID instead of an Employee model object.

The task supports retries for email delivery failures.

Maximum retries: 3.

Retry delay uses exponential backoff:

1 second
2 seconds
4 seconds

### generate_employee_report

Generates an employee report asynchronously.

The task retrieves employee information using Django ORM and returns
JSON-safe report data.

### process_employee_csv

Processes an employee CSV file asynchronously using the existing
EmployeeCSVImportService.

The task receives the CSV file path instead of passing file contents
through the Celery message.

## API Trigger

Welcome email processing can be triggered through:

POST /api/v1/employees/{employee_id}/welcome-email/

The API returns HTTP 202 Accepted with a Celery task ID.

Example response:

{
    "status": "success",
    "message": "Welcome email task queued successfully",
    "task_id": "<celery-task-id>"
}

The API does not wait for the email operation to complete.

## Logging

Tasks log:

- task start
- successful completion
- failures
- employee identifiers
- CSV processing results

Celery worker logs show task receipt, execution and completion.

## Failure Handling

### Invalid Employee ID

An invalid employee ID raises Employee.DoesNotExist and is logged.

### Email Failure

Email delivery failures trigger Celery retries.

### Redis Unavailable

If Redis is unavailable, Celery cannot communicate with the broker and
connection errors are reported.

Redis can be restored using:

Start-Service Memurai

### Worker Unavailable

Tasks remain queued in Redis while the worker is unavailable.

When the worker starts again, queued tasks can be consumed.

## Testing

Run all tests:

python manage.py test

Current verification includes:

- Celery task success
- invalid employee ID
- CSV processing
- employee report generation
- email failure and retry behavior
- duplicate task submission
- Redis availability
- worker availability
- existing application regression tests

## Windows Development

Recommended terminals:

Terminal 1:
Redis/Memurai

Terminal 2:
Celery worker

Terminal 3:
Django development server

## Shutdown

Stop Django with:

Ctrl+C

Stop Celery with:

Ctrl+C

Stop Memurai from Administrator PowerShell:

Stop-Service Memurai