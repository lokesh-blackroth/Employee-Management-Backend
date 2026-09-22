from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if response.status_code == 400:
        message = "Validation failed"
    elif response.status_code == 404:
        message = "Resource not found"
    elif response.status_code == 401:
        message = "Authentication required"
    elif response.status_code == 403:
        message = "Permission denied"
    elif response.status_code == 405:
        message = "Method not allowed"
    else:
        message = "An error occurred"

    errors = response.data

    response.data = {
        "status": "error",
        "message": message,
        "errors": errors,
    }

    return response