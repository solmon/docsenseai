"""Tests for automatic tenant filtering in document models."""

import pytest
from django.contrib.auth.models import User

from documents.models import Document, Tag, Correspondent
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import set_current_tenant


@pytest.mark.django_db
def test_document_queries_filtered_by_tenant():
    """Test that Document queries are automatically filtered by tenant."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create documents using raw SQL to bypass manager (for test setup)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Doc 1", tenant1.id]
        )
        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Doc 2", tenant2.id]
        )

    # Set tenant context
    set_current_tenant(tenant1)

    # Query should only return tenant1's documents
    documents = Document.objects.all()
    assert documents.count() == 1
    assert documents.first().tenant == tenant1


@pytest.mark.django_db
def test_tag_queries_filtered_by_tenant():
    """Test that Tag queries are automatically filtered by tenant."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create tags using raw SQL
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_tag (name, tenant_id, tn_parent_id, tn_level, tn_order, tn_priority) VALUES (%s, %s, NULL, 0, 0, 0)",
            ["Tag 1", tenant1.id]
        )
        cursor.execute(
            "INSERT INTO documents_tag (name, tenant_id, tn_parent_id, tn_level, tn_order, tn_priority) VALUES (%s, %s, NULL, 0, 0, 0)",
            ["Tag 2", tenant2.id]
        )

    set_current_tenant(tenant1)

    tags = Tag.objects.all()
    assert tags.count() == 1
    assert tags.first().tenant == tenant1


@pytest.mark.django_db
def test_correspondent_queries_filtered_by_tenant():
    """Test that Correspondent queries are automatically filtered by tenant."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create correspondents using raw SQL
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_correspondent (name, tenant_id) VALUES (%s, %s)",
            ["Correspondent 1", tenant1.id]
        )
        cursor.execute(
            "INSERT INTO documents_correspondent (name, tenant_id) VALUES (%s, %s)",
            ["Correspondent 2", tenant2.id]
        )

    set_current_tenant(tenant1)

    correspondents = Correspondent.objects.all()
    assert correspondents.count() == 1
    assert correspondents.first().tenant == tenant1


@pytest.mark.django_db
def test_query_fails_without_tenant_context():
    """Test that queries fail safely when tenant context not set."""
    with pytest.raises(ValueError, match="Tenant context not set"):
        Document.objects.all()
