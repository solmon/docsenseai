"""Tests for Document API endpoint tenant filtering."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from documents.models import Document
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import set_current_tenant


@pytest.mark.django_db
def test_document_api_filters_by_tenant(admin_user):
    """Test that Document API automatically filters by tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    UserProfile.objects.create(user=admin_user, tenant=tenant)

    # Create documents
    set_current_tenant(tenant)
    doc1 = Document.objects.create(title="Document 1", tenant=tenant)
    doc2 = Document.objects.create(title="Document 2", tenant=tenant)

    # Create another tenant's document (using raw SQL to bypass manager)
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Other Tenant Doc", tenant2.id]
        )

    client = APIClient()
    client.force_authenticate(user=admin_user)

    # Set tenant context for request
    set_current_tenant(tenant)

    response = client.get("/api/documents/")
    assert response.status_code == 200
    assert response.data["count"] == 2  # Only tenant's documents


@pytest.mark.django_db
def test_document_api_creates_with_tenant(admin_user):
    """Test that Document API automatically assigns tenant on creation."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    UserProfile.objects.create(user=admin_user, tenant=tenant)

    client = APIClient()
    client.force_authenticate(user=admin_user)
    set_current_tenant(tenant)

    data = {"title": "New Document"}
    response = client.post("/api/documents/", data, format="json")
    assert response.status_code in [200, 201]

    # Verify document has tenant assigned
    doc = Document.objects.get(title="New Document")
    assert doc.tenant == tenant
