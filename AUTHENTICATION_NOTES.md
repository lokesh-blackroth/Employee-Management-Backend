# Authentication & Authorization

## Authentication

Authentication answers:

> Who are you?

It verifies the identity of a user.

Examples:
- Username and password
- Login
- Session authentication
- Token authentication

In Django, authentication can be handled using the built-in authentication system.

## Authorization

Authorization answers:

> What are you allowed to do?

It determines what an authenticated user is permitted to access or perform.

Examples:
- Normal user can view their profile
- Staff user can access admin functionality
- Superuser has full permissions

## Authentication vs Authorization

| Authentication | Authorization |
|---|---|
| Verifies user identity | Determines user permissions |
| Answers "Who are you?" | Answers "What can you do?" |
| Happens before authorization | Depends on authenticated identity |
| Example: Login | Example: Access admin page |

## Django User Fields

### username
Unique identifier used to identify the user.

### email
Email address associated with the user.

### password
Django does not store the user's plain-text password.

Instead, Django stores a secure password hash.

### is_active
Determines whether the user account is active.

Inactive users should not be allowed to authenticate.

### is_staff
Determines whether the user can access the Django admin site.

### is_superuser
Grants all permissions without explicitly assigning individual permissions.

## Password Security

Passwords must never be stored as plain text.

Bad:

    SecurePassword123!

Good:

    pbkdf2_sha256$...

Django provides password hashing and password verification mechanisms.

Passwords should be created using Django's password handling methods such as:

    user.set_password(password)

Passwords should be verified using Django's authentication system rather than comparing plain-text passwords directly.