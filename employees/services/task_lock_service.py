from django.core.cache import cache


class TaskLockService:
    """
    Redis-backed distributed lock used to prevent
    overlapping execution of scheduled tasks.
    """

    PREFIX = "celery:task-lock"

    @classmethod
    def acquire(cls, name, timeout=300):
        key = f"{cls.PREFIX}:{name}"

        acquired = cache.add(
            key,
            "locked",
            timeout=timeout,
        )

        if acquired:
            return key

        return None

    @classmethod
    def release(cls, lock):
        if lock is not None:
            cache.delete(lock)