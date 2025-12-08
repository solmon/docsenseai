"""Signals for tenants app."""

from django.contrib.auth.models import User
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from paperless.tenants.models import Tenant, UserProfile


def _tenant_table_exists():
    """Check if tenants_tenant table exists (for migration safety)."""
    with connection.cursor() as cursor:
        table_name = Tenant._meta.db_table
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
            """,
            [table_name],
        )
        return cursor.fetchone()[0]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile and associate with default tenant when User is created."""
    if not created:
        return

    # Skip during migrations - tenant tables may not exist yet
    if not _tenant_table_exists():
        return

    try:
        # Get or create default tenant
        default_tenant, _ = Tenant.objects.get_or_create(
            identifier="default",
            defaults={
                "name": "Default Tenant",
                "is_active": True,
            },
        )

        # Create UserProfile for new user
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={"tenant": default_tenant},
        )
    except Exception:
        # Silently fail during migrations or if tenant app not ready
        # The post_migrate signal will handle tenant creation for fresh installs
        pass

