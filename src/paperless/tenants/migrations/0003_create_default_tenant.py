"""Migration removed - default tenant creation handled by AppConfig.ready() for fresh installations.

This migration is kept for historical reference but does nothing.
For fresh installations, the default tenant is created automatically via
TenantsConfig.ready() -> post_migrate signal.
"""

from django.db import migrations


class Migration(migrations.Migration):
    """Empty migration - tenant creation handled by AppConfig."""

    dependencies = [
        ("tenants", "0002_userprofile"),
    ]

    operations = [
        # No operations - default tenant created via AppConfig.ready() for fresh installs
    ]
