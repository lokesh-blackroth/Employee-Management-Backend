import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger("employees")


class RequestLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.request_id = str(uuid.uuid4())
        request.start_time = time.perf_counter()

    def process_response(self, request, response):
        start_time = getattr(request, "start_time", None)

        if start_time is not None:
            execution_time = time.perf_counter() - start_time
        else:
            execution_time = 0

        request_id = getattr(request, "request_id", "unknown")

        if hasattr(request, "user") and request.user.is_authenticated:
            user = request.user.username
        else:
            user = "anonymous"

        logger.info(
            "Request ID=%s | Method=%s | Path=%s | User=%s | "
            "Status=%s | Execution Time=%.4fs",
            request_id,
            request.method,
            request.path,
            user,
            response.status_code,
            execution_time,
        )

        response["X-Request-ID"] = request_id

        return response