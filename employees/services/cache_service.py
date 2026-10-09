import logging

from django.core.cache import cache

from employees.api.reports import get_department_summary

logger = logging.getLogger("employees")

DEPARTMENT_SUMMARY_CACHE_KEY = "department_summary:v1"
DEPARTMENT_SUMMARY_CACHE_TIMEOUT = 300


def get_cached_department_summary():
    """
    Return cached department statistics when available.
    Calculate and cache the summary on a cache miss.
    """

    try:
        cached_data = cache.get(
            DEPARTMENT_SUMMARY_CACHE_KEY
        )

        if cached_data is not None:
            logger.info(
                "Department summary cache hit"
            )
            return cached_data

        logger.info(
            "Department summary cache miss"
        )

        data = get_department_summary()

        cache.set(
            DEPARTMENT_SUMMARY_CACHE_KEY,
            data,
            timeout=DEPARTMENT_SUMMARY_CACHE_TIMEOUT,
        )

        return data

    except Exception:
        logger.exception(
            "Redis cache operation failed; "
            "generating department summary directly"
        )

        return get_department_summary()


def invalidate_department_summary_cache():
    """
    Remove cached department statistics after employee changes.
    """

    try:
        cache.delete(DEPARTMENT_SUMMARY_CACHE_KEY)

        logger.info(
            "Department summary cache invalidated"
        )

    except Exception:
        logger.exception(
            "Failed to invalidate department summary cache"
        )