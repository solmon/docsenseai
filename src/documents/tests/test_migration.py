"""Tests for document model migration."""

import pytest
from django.contrib.auth.models import User

from documents.models import Document, Tag, Correspondent
from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_document_migration_preserves_data():
    """Test that document migration preserves all data."""
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")

    # Create document with data
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_document (title, content, checksum, created, added) VALUES (%s, %s, %s, NOW(), NOW())",
            ["Test Document", "Test content", "abc123"]
        )
        doc_id = cursor.lastrowid

    # Migrate: add tenant_id
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE documents_document SET tenant_id = %s WHERE id = %s",
            [default_tenant.id, doc_id]
        )

    # Verify data preserved
    doc = Document.objects.get(id=doc_id)
    assert doc.title == "Test Document"
    assert doc.content == "Test content"
    assert doc.checksum == "abc123"
    assert doc.tenant == default_tenant


@pytest.mark.django_db
def test_relationship_preservation():
    """Test that document-tag relationships are preserved."""
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")

    # Create related objects
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_tag (name, tenant_id, tn_parent_id, tn_level, tn_order, tn_priority) VALUES (%s, %s, NULL, 0, 0, 0)",
            ["Tag 1", default_tenant.id]
        )
        tag_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Doc 1", default_tenant.id]
        )
        doc_id = cursor.lastrowid

    # Establish relationship
    doc = Document.objects.get(id=doc_id)
    tag = Tag.objects.get(id=tag_id)
    doc.tags.add(tag)

    # Verify relationship preserved
    assert doc.tags.count() == 1
    assert doc.tags.first() == tag
