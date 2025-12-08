"""Migration removed - data population not needed for fresh installations.

This migration is kept for historical reference but does nothing.
For fresh installations, all tenant-specific models are created with tenant_id
from the start via TenantModel base class, and tenant is auto-assigned from
context when saving.
"""

from django.db import migrations


class Migration(migrations.Migration):
    """Empty migration - tenant_id population not needed for fresh installs."""

    dependencies = [
        ("paperless_mail", "0031_update_mail_unique_constraints_with_tenant"),
        ("tenants", "0003_create_default_tenant"),
    ]

    operations = [
        # No operations - tenant_id is set automatically via TenantModel.save() for fresh installs
    ]
