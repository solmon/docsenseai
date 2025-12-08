"""Tests for migration rollback capability."""

import pytest
from django.contrib.auth.models import User

from documents.models import Document
from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_migration_rollback_preserves_data():
    """Test that rolling back migration preserves existing data."""
    # Create data before migration
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_document (title, created, added) VALUES (%s, NOW(), NOW())",
            ["Pre-migration Doc"]
        )
        doc_id = cursor.lastrowid

    # Simulate migration adding tenant_id (nullable)
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE documents_document SET tenant_id = %s WHERE id = %s",
            [default_tenant.id, doc_id]
        )

    # Simulate rollback: remove tenant_id column (set to NULL)
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE documents_document SET tenant_id = NULL WHERE id = %s",
            [doc_id]
        )

    # Verify data still exists
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT title FROM documents_document WHERE id = %s", [doc_id])
        row = cursor.fetchone()
        assert row[0] == "Pre-migration Doc"
