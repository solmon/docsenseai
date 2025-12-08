"""Add composite indexes for tenant_id."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "1075_update_unique_constraints_with_tenant"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE INDEX IF NOT EXISTS documents_document_tenant_created_idx ON documents_document(tenant_id, created);",
                "CREATE INDEX IF NOT EXISTS documents_document_tenant_modified_idx ON documents_document(tenant_id, modified);",
                "CREATE INDEX IF NOT EXISTS documents_document_tenant_checksum_idx ON documents_document(tenant_id, checksum);",
                "CREATE INDEX IF NOT EXISTS documents_tag_tenant_name_idx ON documents_tag(tenant_id, name);",
                "CREATE INDEX IF NOT EXISTS documents_correspondent_tenant_name_idx ON documents_correspondent(tenant_id, name);",
                "CREATE INDEX IF NOT EXISTS documents_documenttype_tenant_name_idx ON documents_documenttype(tenant_id, name);",
                "CREATE INDEX IF NOT EXISTS documents_storagepath_tenant_name_idx ON documents_storagepath(tenant_id, name);",
                "CREATE INDEX IF NOT EXISTS documents_customfield_tenant_name_idx ON documents_customfield(tenant_id, name);",
                "CREATE INDEX IF NOT EXISTS documents_note_tenant_created_idx ON documents_note(tenant_id, created);",
                "CREATE INDEX IF NOT EXISTS documents_sharelink_tenant_slug_idx ON documents_sharelink(tenant_id, slug);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS documents_document_tenant_created_idx;",
                "DROP INDEX IF EXISTS documents_document_tenant_modified_idx;",
                "DROP INDEX IF EXISTS documents_document_tenant_checksum_idx;",
                "DROP INDEX IF EXISTS documents_tag_tenant_name_idx;",
                "DROP INDEX IF EXISTS documents_correspondent_tenant_name_idx;",
                "DROP INDEX IF EXISTS documents_documenttype_tenant_name_idx;",
                "DROP INDEX IF EXISTS documents_storagepath_tenant_name_idx;",
                "DROP INDEX IF EXISTS documents_customfield_tenant_name_idx;",
                "DROP INDEX IF EXISTS documents_note_tenant_created_idx;",
                "DROP INDEX IF EXISTS documents_sharelink_tenant_slug_idx;",
            ],
        ),
    ]
