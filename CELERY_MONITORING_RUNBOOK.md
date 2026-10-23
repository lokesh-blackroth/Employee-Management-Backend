# Celery Monitoring & Recovery Runbook

## Purpose

Monitor Redis, Celery workers, queues, tasks and cache behavior and provide safe recovery steps.

## Healthy State

- Redis status: healthy
- At least one Celery worker responding
- Queue backlog within expected limits
- No unexpected active/reserved task buildup
- Cache responding normally

## Failure Symptoms

### Redis Failure

Symptoms:
- Redis health check reports unhealthy
- Celery tasks may fail or remain pending
- Cache operations fail

Recovery:
1. Check Redis/Memurai service.
2. Restart Redis if required.
3. Verify Redis health.
4. Restart Celery worker if it does not reconnect.
5. Submit a test task and verify successful processing.

### Celery Worker Failure

Symptoms:
- Worker health reports zero workers
- Tasks remain pending/reserved
- Queue backlog increases

Recovery:
1. Check worker process.
2. Restart the Celery worker.
3. Verify worker appears in health monitoring.
4. Submit a test task.
5. Confirm the task completes successfully.

## Queue Monitoring

Monitor:
- Active tasks
- Reserved tasks
- Scheduled tasks
- Queue backlog

Increasing backlog can indicate insufficient workers, blocked tasks or a dependency failure.

## Cache Monitoring

Track:
- Cache hits
- Cache misses
- Hit rate

A cache miss is not itself a failure. Repeated misses or Redis errors indicate a possible cache problem.

## Negative/Boundary Cases

- Redis unavailable
- Celery worker unavailable
- Invalid task payload
- Failed task requiring retry
- Duplicate task execution

## Verification After Recovery

Confirm:
1. Redis is healthy.
2. Celery worker is responding.
3. Queue backlog is processing.
4. Test task succeeds.
5. Cache operations work.

## Known Limitations

Current monitoring provides live worker/task-state information. Historical success/failure/retry rates require a persistent event/metrics backend and are not inferred from current worker state.
