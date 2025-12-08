"""Merge tenant and workflow migrations."""

from django.db import migrations


class Migration(migrations.Migration):
    """Merge migration for tenant and workflow branches."""

    dependencies = [
        ("documents", "1078_make_tenant_required"),
        ("documents", "1079_workflowrun_deleted_at_workflowrun_restored_at_and_more"),
    ]

    operations = [
        # This is a merge migration with no operations
        # It simply combines the two migration branches
    ]

