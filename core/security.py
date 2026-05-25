# backend/core/security.py
from django.core.exceptions import PermissionDenied


def check_permission(request, permission_codename: str):
    """
    Validates if the authenticated user possesses the specific Django permission.
    If they don't, it cuts the request off right here.
    """
    user = request.auth  # This is the User instance returned by JWTAuth()

    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication credentials missing or invalid.")

    if not user.has_perm(permission_codename):
        raise PermissionDenied(
            f"Access Denied: You do not have permission to execute '{permission_codename}'."
        )

    return True
