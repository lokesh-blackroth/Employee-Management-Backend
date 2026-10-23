from employee_management.celery import app
import logging
import time

from django.core.cache import cache
from django.core.cache.backends.base import CacheKeyWarning

logger = logging.getLogger(__name__)


class CeleryMonitoringService:
    """
    Provides lightweight monitoring information for the
    Celery/Redis infrastructure.

    The service is intentionally read-only:
    it observes system health without modifying tasks,
    queues, or application data.
    """

    CACHE_METRICS_KEY = "monitoring:cache-metrics"

    @classmethod
    def check_redis(cls):
        """Check whether the configured Redis cache is reachable."""

        try:
            start = time.perf_counter()

            health_key = "monitoring:health-check"
            cache.set(health_key, "ok", timeout=10)
            result = cache.get(health_key)

            duration = time.perf_counter() - start

            return {
                "status": "healthy" if result == "ok" else "unhealthy",
                "response_time_ms": round(duration * 1000, 2),
            }

        except Exception as exc:
            logger.exception("Redis health check failed")

            return {
                "status": "unhealthy",
                "error": str(exc),
            }

    @classmethod
    def record_cache_hit(cls):
        """Record a cache hit for monitoring purposes."""

        try:
            metrics = cache.get(cls.CACHE_METRICS_KEY) or {
                "hits": 0,
                "misses": 0,
            }

            metrics["hits"] += 1
            cache.set(cls.CACHE_METRICS_KEY, metrics, timeout=3600)

        except Exception:
            logger.exception("Unable to record cache hit")

    @classmethod
    def record_cache_miss(cls):
        """Record a cache miss for monitoring purposes."""

        try:
            metrics = cache.get(cls.CACHE_METRICS_KEY) or {
                "hits": 0,
                "misses": 0,
            }

            metrics["misses"] += 1
            cache.set(cls.CACHE_METRICS_KEY, metrics, timeout=3600)

        except Exception:
            logger.exception("Unable to record cache miss")

    @classmethod
    def get_cache_metrics(cls):
        """Return cache hit/miss statistics."""

        try:
            metrics = cache.get(cls.CACHE_METRICS_KEY) or {
                "hits": 0,
                "misses": 0,
            }

            total = metrics["hits"] + metrics["misses"]

            hit_rate = (
                metrics["hits"] / total
                if total > 0
                else 0
            )

            return {
                "hits": metrics["hits"],
                "misses": metrics["misses"],
                "total": total,
                "hit_rate": round(hit_rate, 4),
            }

        except Exception:
            logger.exception("Unable to read cache metrics")

            return {
                "hits": 0,
                "misses": 0,
                "total": 0,
                "hit_rate": 0,
                "status": "unavailable",
            }

    @classmethod
    def check_workers(cls):
        """
        Check whether Celery workers are responding.

        A worker is considered healthy when Celery responds
        to a ping request.
        """

        try:
            inspector = app.control.inspect(timeout=2)
            response = inspector.ping()

            if not response:
                return {
                    "status": "unhealthy",
                    "worker_count": 0,
                    "workers": [],
                }

            workers = list(response.keys())

            return {
                "status": "healthy",
                "worker_count": len(workers),
                "workers": workers,
            }

        except Exception as exc:
            logger.exception("Celery worker health check failed")

            return {
                "status": "unhealthy",
                "worker_count": 0,
                "workers": [],
                "error": str(exc),
            }

    @classmethod
    def get_snapshot(cls):
        """
        Return a monitoring snapshot.

        This snapshot is intended for dashboards,
        operational checks and recovery runbooks.
        """

        redis = cls.check_redis()
        workers = cls.check_workers()
        queues = cls.get_queue_metrics()
        cache_metrics = cls.get_cache_metrics()
        tasks = cls.get_task_metrics()

        return {
            "timestamp": time.time(),
            "redis": redis,
            "workers": workers,
            "queues": queues,
            "cache": cache_metrics,
            "tasks": tasks,
        }

    @classmethod
    def get_queue_metrics(cls):
        """
        Return queue depth information for configured Celery queues.

        Queue depth represents the number of messages waiting
        to be consumed by workers.
        """

        try:
            inspector = app.control.inspect(timeout=2)
            reserved = inspector.reserved() or {}
            scheduled = inspector.scheduled() or {}

            reserved_count = sum(
                len(tasks) for tasks in reserved.values()
            )

            scheduled_count = sum(
                len(tasks) for tasks in scheduled.values()
            )

            return {
                "reserved_tasks": reserved_count,
                "scheduled_tasks": scheduled_count,
                "status": "healthy",
            }

        except Exception as exc:
            logger.exception("Celery queue monitoring failed")

            return {
                "reserved_tasks": 0,
                "scheduled_tasks": 0,
                "status": "unavailable",
                "error": str(exc),
            }

    @classmethod
    def get_task_metrics(cls):
        """Return current Celery task-state metrics."""

        try:
            inspector = app.control.inspect(timeout=2)

            active = inspector.active() or {}
            reserved = inspector.reserved() or {}
            scheduled = inspector.scheduled() or {}

            active_count = sum(len(tasks) for tasks in active.values())
            reserved_count = sum(len(tasks) for tasks in reserved.values())
            scheduled_count = sum(
                len(tasks) for tasks in scheduled.values()
            )

            return {
                "status": "healthy",
                "active_tasks": active_count,
                "reserved_tasks": reserved_count,
                "scheduled_tasks": scheduled_count,
            }

        except Exception as exc:
            logger.exception("Celery task monitoring failed")

            return {
                "status": "unavailable",
                "active_tasks": 0,
                "reserved_tasks": 0,
                "scheduled_tasks": 0,
                "error": str(exc),
            }
