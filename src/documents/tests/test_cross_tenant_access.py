"""Tests for cross-tenant access denial."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from documents.models import Document
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import set_current_tenant


@pytest.mark.django_db
def test_cross_tenant_document_access_denied():
    """Test that accessing another tenant's document returns 404."""
    tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
    tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

    user_a = User.objects.create_user(username="usera", password="pass")
    UserProfile.objects.create(user=user_a, tenant=tenant_a)

    # Create document for tenant B
    set_current_tenant(tenant_b)
    doc_b = Document.objects.create(title="Tenant B Doc", tenant=tenant_b)

    # User A tries to access tenant B's document
    client = APIClient()
    client.force_authenticate(user=user_a)
    set_current_tenant(tenant_a)

    response = client.get(f"/api/documents/{doc_b.id}/")
    assert response.status_code in [403, 404]  # Should be denied


@pytest.mark.django_db
def test_cross_tenant_document_update_denied():
    """Test that updating another tenant's document is denied."""
    tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
    tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

    user_a = User.objects.create_user(username="usera", password="pass")
    UserProfile.objects.create(user=user_a, tenant=tenant_a)

    # Create document for tenant B
    set_current_tenant(tenant_b)
    doc_b = Document.objects.create(title="Tenant B Doc", tenant=tenant_b)

    # User A tries to update tenant B's document
    client = APIClient()
    client.force_authenticate(user=user_a)
    set_current_tenant(tenant_a)

    data = {"title": "Hacked Title"}
    response = client.patch(f"/api/documents/{doc_b.id}/", data, format="json")
    assert response.status_code in [403, 404]  # Should be denied
