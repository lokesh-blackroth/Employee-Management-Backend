# Celery Task Contracts and Idempotency

## Day 2 — 20 October 2026

### Objective

Make Celery tasks safer for repeated delivery and temporary failures.

## Task Contract

The `send_welcome_email` task requires:

- `employee_id` must be a positive integer.
- A missing employee raises `ValueError`.
- Invalid payloads are rejected before processing.

## Idempotent Side Effects

The welcome notification workflow checks for an existing successfully
sent `WELCOME` notification before creating another notification.

This prevents duplicate business effects when the same Celery task is
executed more than once.

Verified by:

```text
First execution  -> notification created + email sent
Second execution -> existing notification reused
Notification count -> 1
Email send count   -> 1

Retry and Backoff
Temporary email failures use bounded retry behavior:
- Maximum retries: 3
- Exponential retry backoff enabled
- Maximum backoff: 60 seconds
- Retry jitter enabled
The retry configuration prevents an unlimited retry loop and spreads
retry attempts when multiple tasks fail simultaneously.
Time Limits
The welcome email task uses:
- Soft time limit: 30 seconds
- Hard time limit: 60 seconds
These limits prevent a stuck task from consuming a worker indefinitely.
Failure Handling
Permanent input failures are not retried.

Examples:
- Invalid employee ID type
- Zero or negative employee ID
- Employee does not exist
Temporary email failures are treated separately and are eligible for
bounded retries.
Evidence
Test suite:
python manage.py test employees.tests.test_celery_tasks -v 2

Result:
Ran 6 tests
OK

The tests cover:
1. Successful welcome email processing
2. Duplicate execution without duplicate business effects
3. Missing employee handling
4. Invalid task payload
5. Failed email retry behavior
6. Bounded retry/time-limit configuration
Known Limitations
The idempotency check currently relies on the existing successfully
sent notification lookup. Concurrent duplicate workers could still race
between checking and creating the notification.

A database-level uniqueness constraint or transactional idempotency key
would provide stronger protection against concurrent duplicate delivery.