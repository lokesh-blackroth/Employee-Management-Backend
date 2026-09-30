from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allows access only to users with ADMIN role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "user_role")
            and request.user.user_role.role == "ADMIN"
        )


class IsHR(BasePermission):
    """
    Allows access only to users with HR role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "user_role")
            and request.user.user_role.role == "HR"
        )


class IsManager(BasePermission):
    """
    Allows access only to users with MANAGER role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "user_role")
            and request.user.user_role.role == "MANAGER"
        )


class IsEmployee(BasePermission):
    """
    Allows access only to users with EMPLOYEE role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "user_role")
            and request.user.user_role.role == "EMPLOYEE"
        )


class IsAdminOrHR(BasePermission):
    """
    Allows access to ADMIN and HR users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "user_role")
            and request.user.user_role.role in [
                "ADMIN",
                "HR",
            ]
        )


class IsAdminHROrManager(BasePermission):
    """
    Allows access to ADMIN, HR and MANAGER users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "user_role")
            and request.user.user_role.role in [
                "ADMIN",
                "HR",
                "MANAGER",
            ]
        )