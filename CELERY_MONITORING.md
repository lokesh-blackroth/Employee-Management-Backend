# Celery Task Monitoring

## Overview

The Employee Management Backend uses Celery Worker and Celery Beat
for background and scheduled task processing.

Redis is used as the Celery message broker.

This document describes basic health checks, task checks, and
queue-depth monitoring.

## 1. Celery Worker Health Check

Use the following command to check whether a Celery Worker is
online and responding:

```text
celery -A employee_management inspect ping
Expected response:
-> celery@<worker-name>: OK
    pong

1 node online.

A successful pong confirms that the worker is online and
responding to Celery control commands.
2. Registered Task Check
Use:
celery -A employee_management inspect registered

This displays the tasks currently registered with the worker.
Expected project tasks include:
- employees.tasks.generate_employee_report
- employees.tasks.process_employee_csv
- employees.tasks.scheduled_employee_summary
- employees.tasks.send_welcome_email
3. Redis Connectivity Check
Redis connectivity can be checked through the Django shell:
import redisr = redis.Redis(    host="127.0.0.1",    port=6379,    db=0,)print(r.ping())


Expected result:
True

4. Celery Queue Depth
The Celery broker queue can be checked using Redis:
print(r.llen("celery"))


The returned value represents the number of tasks currently
waiting in the celery queue.
Example:
0

means there are currently no tasks waiting in the queue.
A growing queue depth may indicate that tasks are arriving faster
than available workers can process them.
5. Task Execution Monitoring
Celery task logs record:
- Task start
- Task completion
- Execution duration
- Task failure
Example successful execution:
Scheduled employee summary started
Scheduled employee summary finished:
active=37, inactive=3, duration=0.1559 seconds

Example failure:
Test failure task started
Test failure task failed: duration=0.0024 seconds

6. Monitoring Flow
Celery Beat
    |
    | scheduled task
    v
Redis
    |
    | queue depth
    v
Celery Worker
    |
    +--> Task started
    |
    +--> Task completed
    |
    +--> Duration recorded
    |
    +--> Failure recorded

7. Current Verification
The following checks were performed during development:
- Celery Worker health check: successful
- Registered task check: successful
- Redis connectivity check: successful
- Celery queue-depth check: successful
- Scheduled employee summary success logging: verified
- Task failure logging: verified

Save it.

### Step 6.1 — Check the files

Run:

```powershell
git status

@'
# Celery Monitoring & Recovery

## 16-Oct — Recovery Demo & Failure Validation

### Objective

Validate Celery and Redis recovery behavior by simulating Redis interruption, restoring the broker, testing task retries and final failure, checking duplicate task execution, validating scheduled jobs, comparing execution with baseline, and documenting rollback procedures.

---

## 1. Baseline

### Employee Report

Task:

`employees.tasks.generate_employee_report`

Observed result:

- Employee records processed: 40
- Successful execution
- Observed execution time: approximately 0.12–0.24 seconds

### Scheduled Employee Summary

Task:

`employees.tasks.scheduled_employee_summary`

Observed result:

- Active employees: 37
- Inactive employees: 3
- Observed execution time: approximately 0.16 seconds

---

## 2. Redis Interruption Test

Memurai was running as the local Redis service.

Redis service was stopped to simulate broker/result-store interruption.

Observed connection failure:

`redis.exceptions.ConnectionError`

Target:

`127.0.0.1:6379`

Observed Windows error:

`WinError 10061 - No connection could be made because the target machine actively refused it.`

This confirmed that the application could detect Redis unavailability.

---

## 3. Recovery Test

Memurai was restarted successfully.

Verification:

- Memurai service: Running
- Redis process: Running
- Celery worker reconnected to:

`redis://127.0.0.1:6379/0`

The Celery worker reached the `ready` state.

A subsequent employee report task completed successfully for 40 employees.

### Result

Redis and Celery recovered successfully after the simulated interruption.

---

## 4. Retry Test

The `send_welcome_email` task is configured with:

```python
@app.task(
    bind=True,
    max_retries=3,
)

The task uses:
countdown=2 ** self.request.retries



Also change the retry section from plain text:

```text
Attempt Delay
Initial failure Immediate
Retry 1 1 second
Retry 2 2 seconds
Retry 3 4 seconds
Final failure After retry limit

to:
| Attempt | Delay |
|---|---:|
| Initial failure | Immediate |
| Retry 1 | 1 second |
| Retry 2 | 2 seconds |
| Retry 3 | 4 seconds |
| Final failure | After retry limit |