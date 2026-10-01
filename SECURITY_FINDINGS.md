# SEC-004 Security Findings

## Input Validation
- Employee code: empty values rejected.
- First name: empty/oversized values rejected.
- Last name: empty/oversized values rejected.
- Email: invalid email format rejected.
- Salary: negative salary rejected.
- Required fields are validated by DRF/model validation.

## Authentication & Authorization
- JWT authentication enabled.
- Employee create/update requires Admin or HR role.
- Unauthorized requests return 401.
- Unauthorized roles return 403.

## CORS
- CORS restricted to configured localhost origins.
- CORS_ALLOW_ALL_ORIGINS is not enabled.

## CSRF
- Django CsrfViewMiddleware is enabled.
- API authentication uses JWT Bearer tokens rather than session authentication.

## Secrets
- SECRET_KEY is loaded from environment variables.
- Database credentials are loaded from .env.
- .env is not committed to Git.
- .env.example contains placeholders only.

## SQL Injection
- Django ORM is used for database queries.
- No unsafe user-controlled SQL identified during review.

## Sensitive Data Exposure
- Passwords are handled through Django authentication.
- JWT credentials and database secrets are not returned by employee APIs.

## Rate Limiting
- Login/registration throttling review required before final security acceptance.

## OWASP API Security Review
- Broken Object Level Authorization: reviewed through RBAC/profile ownership.
- Broken Authentication: JWT authentication implemented.
- Broken Object Property Level Authorization: serializer fields reviewed.
- Unrestricted Resource Consumption: throttling review required.
- Security Misconfiguration: DEBUG/secrets/CORS reviewed.
- Improper Inventory Management: API routes reviewed.
