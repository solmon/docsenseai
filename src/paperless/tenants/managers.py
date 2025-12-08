"""Tenant-aware queryset manager."""

import sys
from django.apps import apps
from django.db import models

from paperless.tenants.utils import get_current_tenant


def _is_app_initialization():
    """Check if we're in Django app initialization phase."""
    # During app initialization, apps may not be ready yet
    # or we may be in a migration context
    if not apps.ready:
        return True

    # Check if we're being called during class definition or introspection
    # by examining the call stack
    frame = sys._getframe()
    depth = 0
    max_depth = 15  # Increased depth to catch more cases

    while frame and depth < max_depth:
        frame = frame.f_back
        depth += 1
        if frame:
            filename = frame.f_code.co_filename
            # django-filters introspects models during class definition
            if 'django_filters' in filename or 'filterset' in filename.lower():
                return True
            # Django's model introspection
            if 'django/db/models' in filename and 'options' in filename:
                return True
            # DRF serializers access querysets during class definition
            if 'serialisers.py' in filename or 'serializers.py' in filename:
                return True
            # URL configuration checks
            if 'urls.py' in filename:
                return True
            # Django URL resolver checks
            if 'django/urls' in filename:
                return True
            # Django checks framework
            if 'django/core/checks' in filename:
                return True
            # Django management commands
            if 'django/core/management' in filename:
                return True

    return False


class TenantQuerySet(models.QuerySet):
    """QuerySet that automatically filters by current tenant."""

    def for_tenant(self, tenant):
        """Explicitly filter by a specific tenant (for admin/global superuser use)."""
        return self.filter(tenant=tenant)


class TenantManager(models.Manager):
    """Manager that automatically filters queries by current tenant."""

    def get_queryset(self):
        """Return queryset filtered by current tenant."""
        queryset = super().get_queryset()
        tenant = get_current_tenant()

        if tenant is not None:
            return queryset.filter(tenant=tenant)

        # During app initialization or model introspection, allow unfiltered access
        # This is needed for FilterSet creation, migrations, and admin registration
        if _is_app_initialization():
            return queryset

        # Fail safely if tenant context not set during normal operation
        raise ValueError(
            "Tenant context not set. Ensure middleware is configured correctly and user has tenant association."
        )

    def for_tenant(self, tenant):
        """Explicitly filter by a specific tenant (for admin/global superuser use)."""
        return self.get_queryset().for_tenant(tenant)
