from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_tenant_for_fresh_install(sender, **kwargs):
    """Create default tenant for fresh installations only."""
    from paperless.tenants.models import Tenant

    # Only create if no tenants exist (fresh install)
    if not Tenant.objects.exists():
        Tenant.objects.create(
            name="Default Tenant",
            identifier="default",
            is_active=True,
        )


class TenantsConfig(AppConfig):
    """Configuration for tenants app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "paperless.tenants"
    verbose_name = "Tenants"

    def ready(self):
        """Initialize tenant app for fresh installations."""
        # Import signals to register them
        from paperless.tenants import signals  # noqa: F401

        # Create default tenant after migrations run (fresh install only)
        post_migrate.connect(create_default_tenant_for_fresh_install, sender=self)
