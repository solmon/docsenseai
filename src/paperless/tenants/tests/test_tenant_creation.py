"""Integration tests for tenant creation."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from paperless.tenants.models import Tenant


@pytest.mark.django_db
def test_create_tenant_via_api(admin_user):
    """Test creating a tenant via API."""
    client = APIClient()
    client.force_authenticate(user=admin_user)

    data = {
        "name": "Test Tenant",
        "identifier": "test-tenant",
        "is_active": True,
    }

    response = client.post("/api/tenants/", data, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "Test Tenant"
    assert response.data["identifier"] == "test-tenant"

    # Verify tenant was created
    tenant = Tenant.objects.get(identifier="test-tenant")
    assert tenant.name == "Test Tenant"
    assert tenant.is_active is True


@pytest.mark.django_db
def test_create_tenant_duplicate_identifier(admin_user):
    """Test that duplicate identifiers are rejected."""
    Tenant.objects.create(name="Existing Tenant", identifier="existing")

    client = APIClient()
    client.force_authenticate(user=admin_user)

    data = {
        "name": "New Tenant",
        "identifier": "existing",  # Duplicate
        "is_active": True,
    }

    response = client.post("/api/tenants/", data, format="json")
    assert response.status_code == 400
    assert "unique" in str(response.data).lower()


@pytest.mark.django_db
def test_list_tenants(admin_user):
    """Test listing tenants."""
    Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.get("/api/tenants/")
    assert response.status_code == 200
    assert response.data["count"] == 2
