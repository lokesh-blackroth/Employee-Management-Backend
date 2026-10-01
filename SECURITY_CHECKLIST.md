# SEC-004 Security Checklist

## Security Configuration
- [x] DEBUG controlled through environment variable
- [x] SECRET_KEY loaded from environment
- [x] ALLOWED_HOSTS controlled through environment
- [x] CSRF middleware enabled
- [x] CORS restricted to allowed origins
- [x] Production HTTPS settings reviewed

## Secret Management
- [x] .env used for real secrets
- [x] .env not committed to Git
- [x] .env.example contains placeholders
- [x] Database credentials removed from source code

## Authentication & Authorization
- [x] JWT authentication enabled
- [x] RBAC permissions reviewed
- [x] Unauthorized request returns 401
- [x] Insufficient role returns 403
- [x] Employee ownership/profile access reviewed

## Input Validation
- [x] Empty employee code rejected
- [x] Invalid email rejected
- [x] Negative salary rejected
- [x] Oversized text values rejected
- [x] Required fields validated
- [x] Invalid input returns 400

## SQL Injection
- [x] Django ORM used
- [x] No raw SQL usage found in employees app

## Sensitive Data Exposure
- [x] Passwords not returned by login response
- [x] JWT tokens not returned by custom login response
- [x] Database credentials not exposed
- [x] Employee serializer explicitly controls API fields
- [ ] Legacy model_to_dict() views should be reviewed separately

## Rate Limiting
- [x] DRF throttling configured
- [x] Anonymous requests throttled
- [x] Authenticated requests throttled

## OWASP API Security Review
- [x] Broken Object Level Authorization reviewed
- [x] Broken Authentication reviewed
- [x] Broken Object Property Level Authorization reviewed
- [x] Unrestricted Resource Consumption reviewed
- [x] Security Misconfiguration reviewed
- [x] Improper Inventory Management reviewed

## Verification
- [x] python manage.py check
- [x] python manage.py test
- [x] 37 tests passing
