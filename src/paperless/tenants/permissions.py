"""Permissions for tenants app."""

from rest_framework.permissions import BasePermission


class SuperAdminPermission(BasePermission):
    """Permission class that requires superuser status."""

    def has_permission(self, request, view):
        """Check if user is a superuser."""
        return request.user and request.user.is_authenticated and request.user.is_superuser

