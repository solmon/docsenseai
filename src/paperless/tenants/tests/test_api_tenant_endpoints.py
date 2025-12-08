"""Tests for tenant API endpoints."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_get_current_user_tenant(api_client, user_with_tenant):
    """Test GET /api/profile/tenant/ returns current user's tenant."""
    user, tenant = user_with_tenant
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/profile/tenant/")

    assert response.status_code == 200
    assert response.data["id"] == tenant.id
    assert response.data["name"] == tenant.name
    assert response.data["identifier"] == tenant.identifier


@pytest.mark.django_db
def test_get_current_user_tenant_no_tenant(api_client):
    """Test GET /api/profile/tenant/ returns 404 when user has no tenant."""
    user = User.objects.create_user(username="notenant", password="testpass")
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/profile/tenant/")

    assert response.status_code == 404
    assert "No tenant association" in response.data["detail"]


@pytest.mark.django_db
def test_get_user_tenants(api_client, user_with_tenant):
    """Test GET /api/users/{id}/tenants/ returns user's tenants."""
    user, tenant = user_with_tenant
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/users/{user.id}/tenants/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == tenant.id


@pytest.mark.django_db
def test_get_user_tenants_requires_permission(api_client, user_with_tenant):
    """Test that users can only view their own tenants unless superuser."""
    user1, tenant1 = user_with_tenant
    user2 = User.objects.create_user(username="user2", password="testpass")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")
    UserProfile.objects.create(user=user2, tenant=tenant2)

    api_client.force_authenticate(user=user1)

    # User1 cannot view user2's tenants
    response = api_client.get(f"/api/users/{user2.id}/tenants/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_user_tenants_superuser_can_view_any(api_client, user_with_tenant):
    """Test that superuser can view any user's tenants."""
    user1, tenant1 = user_with_tenant
    user2 = User.objects.create_user(username="user2", password="testpass")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")
    UserProfile.objects.create(user=user2, tenant=tenant2)

    # Make user1 a superuser
    user1.is_superuser = True
    user1.save()

    api_client.force_authenticate(user=user1)

    # Superuser can view user2's tenants
    response = api_client.get(f"/api/users/{user2.id}/tenants/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == tenant2.id


@pytest.mark.django_db
def test_api_request_includes_tenant_header(api_client, user_with_tenant):
    """Test that API requests with X-Tenant-ID header work correctly."""
    user, tenant = user_with_tenant
    api_client.force_authenticate(user=user)

    # Make request with X-Tenant-ID header
    response = api_client.get(
        "/api/profile/tenant/", HTTP_X_TENANT_ID=str(tenant.id)
    )

    assert response.status_code == 200
    assert response.data["id"] == tenant.id


@pytest.mark.django_db
def test_api_request_with_wrong_tenant_header(api_client, user_with_tenant):
    """Test that API requests with wrong X-Tenant-ID header are rejected."""
    user, tenant = user_with_tenant
    other_tenant = Tenant.objects.create(
        name="Other Tenant", identifier="other-tenant"
    )
    api_client.force_authenticate(user=user)

    # Make request with wrong X-Tenant-ID header
    response = api_client.get(
        "/api/profile/tenant/", HTTP_X_TENANT_ID=str(other_tenant.id)
    )

    assert response.status_code == 403
    assert "does not match" in response.data["detail"]


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


@pytest.fixture
def user_with_tenant():
    """Create a user with a tenant association."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)
    return user, tenant

