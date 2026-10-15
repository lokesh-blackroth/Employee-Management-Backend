# Celery Deployment Topology

## Overview

The Employee Management Backend uses Django, PostgreSQL, Redis,
Celery Worker, and Celery Beat for API handling, database storage,
caching, and background task processing.

## Components

### Django API

The Django application provides the REST API and contains the
business logic and Celery task definitions.

### PostgreSQL

PostgreSQL is the primary application database.

It stores employee data, application data, and django-celery-beat
periodic task configuration.

### Redis

Redis is used as the Celery message broker and also as the
Django cache backend.

Celery Beat publishes scheduled tasks to Redis, and Celery Workers
consume tasks from Redis.

### Celery Beat

Celery Beat is responsible for triggering periodic tasks according
to their configured schedules.

The project uses django-celery-beat's DatabaseScheduler.

### Celery Worker

Celery Worker consumes queued tasks from Redis and executes the
registered Celery tasks.

## Task Flow

```text
Celery Beat
    |
    | scheduled task
    v
Redis
    |
    | queued task
    v
Celery Worker
    |
    | executes task
    v
Django Application
    |
    v
PostgreSQL

API Flow
Client
   |
   v
Django REST API
   |
   v
PostgreSQL

Monitoring Flow
Celery Beat
    |
    v
Redis Queue
    |
    v
Celery Worker
    |
    +--> Success
    |
    +--> Failure
    |
    +--> Execution Duration

Timezone Configuration
The application uses:
- Django TIME_ZONE: Asia/Kolkata
- Django USE_TZ: True
- Celery CELERY_TIMEZONE: Asia/Kolkata
Celery Beat therefore uses the configured application timezone
when evaluating periodic schedules.
Current Periodic Tasks
The periodic tasks are managed through django-celery-beat's
database scheduler.
Current configured tasks include:
- celery.backend_cleanup
- employees.tasks.scheduled_employee_summary
The Scheduled Employee Summary task is currently configured
with an interval schedule of every 5 minutes.