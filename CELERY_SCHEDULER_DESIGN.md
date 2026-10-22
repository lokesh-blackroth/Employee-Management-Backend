# Day 3 — Schedulers, Queue Topology and Backpressure

## Objective

Configure Celery periodic task execution, queue routing, concurrency controls,
task expiration, and overlap protection to prevent uncontrolled queue growth
and duplicate scheduled executions.

---

## 1. Celery Scheduler

Celery Beat is configured using `django-celery-beat`.

### Configuration

```python
CELERY_BEAT_SCHEDULER = (
    "django_celery_beat.schedulers:DatabaseScheduler"
)

CELERY_TIMEZONE = TIME_ZONE

The application timezone is:
Asia/Kolkata

This allows periodic tasks to be managed through the Django database scheduler.
2. Queue Topology
Separate queues are used to isolate different types of background work.
Queue	Purpose
default	General tasks without an explicit route
reports	Employee report generation
maintenance	CSV processing and scheduled maintenance
notifications	Welcome email processing


Task Routing
CELERY_TASK_ROUTES = {    "employees.tasks.generate_employee_report": {        "queue": "reports",    },    "employees.tasks.process_employee_csv": {        "queue": "maintenance",    },    "employees.tasks.scheduled_employee_summary": {        "queue": "maintenance",    },    "employees.tasks.send_welcome_email": {        "queue": "notifications",    },}


Queue separation prevents report generation or maintenance work from
competing directly with notification tasks.
3. Backpressure Control
The worker prefetch multiplier is set to 1.
CELERY_WORKER_PREFETCH_MULTIPLIER = 1


This limits the number of additional tasks a worker reserves from the broker.
Reason
A large prefetch value can allow a worker to reserve many tasks before
processing them. During a backlog, this can result in poor task distribution
and increased waiting time for tasks assigned to other workers.

Using a prefetch multiplier of 1 provides controlled task consumption and
better backpressure behavior.
4. Task Acknowledgement
Late acknowledgement is enabled:
CELERY_TASK_ACKS_LATE = True


The task is acknowledged after execution rather than immediately when the
worker receives it.

Worker-loss recovery is also enabled:
CELERY_TASK_REJECT_ON_WORKER_LOST = True


If a worker disappears while processing a task, the broker can make the task
available again instead of permanently losing the work.
5. Task Expiration
A default task expiration of 300 seconds is configured:
CELERY_TASK_DEFAULT_EXPIRES = 300


This prevents stale tasks from remaining in the queue indefinitely.

The scheduled employee summary has a more specific expiration:
@app.task(    bind=True,    expires=240,    soft_time_limit=30,    time_limit=60,)


Why expiration is required
Scheduled or background work can become stale when a queue is overloaded.
Expiration prevents old work from being processed after it is no longer useful.
6. Scheduled Task
The scheduled employee summary task is:
employees.tasks.scheduled_employee_summary

It is routed to:
maintenance

The task calculates:
active employees
inactive employees
execution duration

It also logs the beginning and completion of each execution.
7. Overlap Protection
A Redis-backed distributed lock is used by the scheduled summary task.
lock = TaskLockService.acquire(    "scheduled_employee_summary",    timeout=300,)


If another execution already owns the lock:
if lock is None:    return {        "status": "skipped",        "reason": "already_running",    }


The lock is released in the finally block:
finally:    TaskLockService.release(lock)


Reason
If a scheduled task takes longer than expected, another scheduler execution
could start before the first one finishes.

The Redis lock ensures that only one instance of the same scheduled task can
execute at a time.
8. Verification Evidence
Django configuration check
Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Python compilation check:
python -m py_compile employees\tasks.py

Result:
No errors

Runtime Celery configuration
The application loaded the following queues:
default
reports
maintenance
notifications

Task routing was verified as:
generate_employee_report
    -> reports

process_employee_csv
    -> maintenance

scheduled_employee_summary
    -> maintenance

send_welcome_email
    -> notifications

Runtime configuration also confirmed:
Prefetch multiplier: 1
Late acknowledgement: True
Task expiration: 300 seconds
Timezone: Asia/Kolkata

9. Queue Routing Test — Reports
A reports-only worker was started using:
celery -A employee_management worker --loglevel=INFO --pool=solo -Q reports -n reports@%h

The worker reported:
[queues]
    .> reports

The employee report task was then submitted.

Evidence:
Task employees.tasks.generate_employee_report[...] received
Employee report generated successfully: 40 employees
Task ... succeeded

Execution completed successfully in approximately:
0.23 seconds

This confirms that the report task was successfully consumed from the
reports queue.
10. Queue Routing Test — Maintenance
A maintenance-only worker was started using:
celery -A employee_management worker --loglevel=INFO --pool=solo -Q maintenance -n maintenance@%h

The worker reported:
[queues]
    .> maintenance

The scheduled employee summary was submitted.

Evidence:
Task employees.tasks.scheduled_employee_summary[...] received
Scheduled employee summary started
Scheduled employee summary finished:
active=37, inactive=3, duration=0.2647 seconds
Task ... succeeded

This confirms successful execution through the maintenance queue.
11. Negative / Boundary Test — Overlapping Lock
The Redis task lock was tested directly.

Test sequence:
First lock  -> acquired
Second lock -> rejected
First lock  -> released
Third lock  -> acquired

Actual result:
First lock: celery:task-lock:day3_overlap_test
Second lock: None
Third lock after release: celery:task-lock:day3_overlap_test

Interpretation
The second execution could not acquire the same lock while the first lock
was active.

After releasing the first lock, another execution could acquire it.

This demonstrates the required overlap-prevention behavior.
12. Known Limitations
1. --pool=solo is used for Windows-based local development and testing.
   Production workers can use a more appropriate execution pool.
2. Queue isolation is configured at the Celery level, but production
   deployments should run dedicated workers for each queue based on actual
   workload.
3. The Redis lock timeout must be longer than the expected maximum task
   execution time. If a task legitimately runs longer than the lock timeout,
   the lock could expire before the task finishes.
4. Task expiration prevents stale work from being processed, but it does not
   replace queue monitoring or capacity planning.
5. Prefetch multiplier 1 improves backpressure behavior but can reduce
   throughput for workloads where aggressive prefetching would be beneficial.
6. Celery Beat scheduling and worker execution are separate processes and
   both must be running for periodic tasks to execute.
13. Day 3 Outcome
The project now has:
- Periodic task scheduling support
- Dedicated Celery queues
- Explicit task routing
- Controlled worker prefetch
- Late task acknowledgement
- Worker-loss recovery configuration
- Task expiration
- Redis-based overlap protection
- Queue routing verification
- Successful execution evidence
- Negative overlap test evidence
- Documented design decisions and limitations