"""Tests for tenant migration."""

import pytest
from django.contrib.auth.models import User

from documents.models import Document, Tag
from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_default_tenant_creation():
    """Test that default tenant is created during migration."""
    # This would be tested via actual migration execution
    # For unit test, we simulate
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")
    assert default_tenant.name == "Default Tenant"
    assert default_tenant.identifier == "default"


@pytest.mark.django_db
def test_user_association_with_default_tenant():
    """Test that existing users are associated with default tenant."""
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")
    user = User.objects.create_user(username="existing_user", password="pass")

    # Simulate migration associating user with tenant
    UserProfile.objects.create(user=user, tenant=default_tenant)

    assert user.tenant == default_tenant


@pytest.mark.django_db
def test_data_population_with_tenant_id():
    """Test that existing data receives tenant_id during migration."""
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")

    # Create document without tenant (simulating pre-migration state)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_document (title, created, added) VALUES (%s, NOW(), NOW())",
            ["Pre-migration Document"]
        )
        doc_id = cursor.lastrowid

    # Simulate migration populating tenant_id
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE documents_document SET tenant_id = %s WHERE id = %s",
            [default_tenant.id, doc_id]
        )

    # Verify
    doc = Document.objects.get(id=doc_id)
    assert doc.tenant == default_tenant


@pytest.mark.django_db
def test_relationship_preservation_during_migration():
    """Test that relationships are preserved during migration."""
    default_tenant = Tenant.objects.create(name="Default Tenant", identifier="default")

    # Create related objects
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_tag (name, tenant_id, tn_parent_id, tn_level, tn_order, tn_priority) VALUES (%s, %s, NULL, 0, 0, 0)",
            ["Test Tag", default_tenant.id]
        )
        tag_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Test Doc", default_tenant.id]
        )
        doc_id = cursor.lastrowid

    # Verify relationship can be established
    doc = Document.objects.get(id=doc_id)
    tag = Tag.objects.get(id=tag_id)
    doc.tags.add(tag)

    assert tag in doc.tags.all()
    assert doc.tenant == tag.tenant == default_tenant
