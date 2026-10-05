# ADV-001 — Advanced Django: Middleware & Signals

## 1. Objective

Implemented Django middleware and signals for request tracing, request/response logging, execution-time tracking, and employee audit logging.

---

## 2. Request Logging Middleware

### File

`employees/middleware.py`

### Responsibilities

The middleware handles request/response-level concerns:

- Generates a unique request/correlation ID.
- Records request start time.
- Logs HTTP method.
- Logs request path.
- Identifies authenticated users.
- Handles anonymous requests.
- Logs response status code.
- Calculates execution time.
- Adds the request ID to the response header.

### Request Flow

```text
Client Request
      ↓
RequestLoggingMiddleware
      ↓
Generate Request ID
      ↓
Record Start Time
      ↓
Django View/ViewSet
      ↓
Response
      ↓
Calculate Execution Time
      ↓
Log Request Information
      ↓
Add X-Request-ID Header
      ↓
Client Response
```

### Request ID

A UUID is generated for every request:

```python
request.request_id = str(uuid.uuid4())
```

The same ID is returned through:

```text
X-Request-ID
```

This allows a request to be traced across logs.

### Logged Information

The middleware logs:

```text
Request ID
HTTP Method
Request Path
User
Response Status
Execution Time
```

Anonymous requests are logged as:

```text
anonymous
```

Authenticated requests use the authenticated user's username.

### Sensitive Data Protection

The middleware does not log:

- Passwords
- JWT access tokens
- JWT refresh tokens
- Request bodies
- Salary
- Phone numbers
- Other sensitive personal information

---

## 3. Logging Configuration

Logging was configured in:

`employee_management/settings.py`

The `employees` logger uses an INFO logging level and console handler.

The formatter includes:

```text
Level
Timestamp
Logger name
Message
```

This allows middleware and signal events to be visible during development and debugging.

---

## 4. Health API Verification

A health endpoint was implemented:

```text
GET /api/v1/health/
```

Response:

```json
{
    "status": "success",
    "message": "Employee Management Backend is running"
}
```

The endpoint returned:

```text
HTTP 200 OK
```

The response also contained:

```text
X-Request-ID: <UUID>
```

This verified that the request logging middleware is active.

---

## 5. Middleware Testing

### Successful request

```text
GET /api/v1/health/
→ 200 OK
→ X-Request-ID returned
```

### Authentication test

```text
GET /api/v1/employees/
→ 401 Unauthorized
```

This verified middleware execution for an authenticated API that requires credentials.

### Not Found test

```text
GET /api/v1/not-found/
→ 404 Not Found
```

This verified that middleware also processes error responses.

---

## 6. Middleware Debugging

The middleware registration was intentionally broken in `settings.py`.

Incorrect configuration:

```python
'employees.middleware.RequestLoggingMiddlewar',
```

Django produced an import error because the middleware class name did not exist.

The correct configuration was restored:

```python
'employees.middleware.RequestLoggingMiddleware',
```

The server then started successfully.

This verified the middleware registration and debugging process.

---

## 7. AuditLog Model

An `AuditLog` model was added to:

`employees/models.py`

The model stores important employee changes.

### Fields

```text
employee
action
performed_by
description
timestamp
```

### Supported Actions

```text
CREATED
UPDATED
```

The audit log is associated with the employee using a ForeignKey.

`performed_by` is nullable because normal Django model signals do not automatically receive the HTTP request or authenticated user context.

### Migration

Created:

```text
employees/migrations/0010_auditlog.py
```

Migration was successfully applied using:

```powershell
python manage.py makemigrations employees
python manage.py migrate
```

---

## 8. Employee Audit Signals

### File

`employees/signals.py`

A `post_save` signal was implemented for the `Employee` model.

The signal creates an audit record when an employee is:

- Created
- Updated

### Create Flow

```text
Employee created
      ↓
post_save
      ↓
employee_audit_log()
      ↓
AuditLog
      ↓
CREATED
```

### Update Flow

```text
Employee updated
      ↓
post_save
      ↓
employee_audit_log()
      ↓
AuditLog
      ↓
UPDATED
```

---

## 9. Signal Registration

Signals are registered in:

`employees/apps.py`

The application uses:

```python
class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"

    def ready(self):
        import employees.signals
```

The application configuration is enabled in:

`employee_management/settings.py`

using:

```python
'employees.apps.EmployeesConfig',
```

This ensures the signals are loaded when Django starts.

---

## 10. Signal Debugging

Signal registration was intentionally broken.

Incorrect import:

```python
import employees.signal
```

The actual module is:

```text
employees.signals
```

Django produced:

```text
ModuleNotFoundError: No module named 'employees.signal'
```

The correct import was restored:

```python
import employees.signals
```

The server then started successfully.

---

## 11. Signal Exception Handling Debugging

An intentional exception was added to reproduce a signal failure:

```python
@receiver(post_save, sender=Employee)
def employee_audit_log(sender, instance, created, **kwargs):
    raise Exception("Intentional signal failure")
```

An existing employee was then updated:

```python
employee.first_name = "SignalTest"
employee.save()
```

The exception was successfully reproduced:

```text
Exception: Intentional signal failure
```

The traceback confirmed that the exception originated from:

```text
employees/signals.py
```

This verified the signal exception handling failure scenario.

---

## 12. Signal Exception Handling Fix

The signal was updated to use exception handling:

```python
try:
    ...
except Exception:
    logger.exception(
        "Failed to create audit log for employee %s",
        instance.employee_code,
    )
```

This ensures unexpected audit logging errors are recorded using the application's logging system.

Only the employee code is included in the error message. Sensitive employee information is not logged.

---

## 13. Signal Retest

After fixing the signal, an employee was updated:

```python
employee.first_name = "SignalTestFixed"
employee.save()
```

The save completed successfully without the intentional exception.

The audit record was verified:

```text
action: UPDATED
description: Employee EMP031 was updated.
```

This confirmed that the corrected signal successfully creates an audit record.

---

## 14. Business Logic Separation

Middleware and signals have separate responsibilities.

### Middleware

Responsible for:

```text
Request/response processing
Request ID
Execution time
Request logging
Response headers
```

### Signals

Responsible for:

```text
Reacting to Employee model save events
Creating audit records
```

### Business Services / Views

Responsible for:

```text
Business rules
Validation
Authorization
Employee operations
```

Business rules are not placed inside signals.

---

## 15. Final Architecture

```text
                    HTTP Request
                         │
                         ▼
              RequestLoggingMiddleware
                         │
              ┌──────────┴──────────┐
              │                     │
        Request ID             Start Time
              │                     │
              └──────────┬──────────┘
                         ▼
                    API ViewSet
                         │
                         ▼
                    Serializer
                         │
                         ▼
                       ORM
                         │
                         ▼
                  Employee.save()
                         │
                         ▼
                    post_save
                         │
                         ▼
                 AuditLog Signal
                         │
                         ▼
                    AuditLog DB
                         │
                         ▼
                     Response
                         │
                         ▼
              Middleware calculates
                execution time
                         │
                         ▼
                 X-Request-ID
                         │
                         ▼
                  Client Response
```

---

## 16. Acceptance Criteria

| Requirement | Status |
|---|---|
| Middleware implemented | PASS |
| Unique request ID generated | PASS |
| Request ID returned in response | PASS |
| Request/response logging | PASS |
| Execution time recorded | PASS |
| Anonymous request handling | PASS |
| Authenticated request handling | PASS |
| 400/404 handling tested | PASS |
| AuditLog model created | PASS |
| Audit migration created | PASS |
| Employee create audit | PASS |
| Employee update audit | PASS |
| Signal registration | PASS |
| Middleware debugging | PASS |
| Signal registration debugging | PASS |
| Signal exception debugging | PASS |
| Signal exception handling | PASS |
| Sensitive data protection | PASS |
| Business rules kept outside signals | PASS |