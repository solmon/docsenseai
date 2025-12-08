"""Tests for X-Tenant-ID header verification."""

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from paperless.tenants.middleware import TenantMiddleware
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import get_current_tenant


@pytest.mark.django_db
def test_valid_header_matches_user_tenant():
    """Test that valid X-Tenant-ID header matching user's tenant works."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID=str(tenant.id))
    request.user = user

    def dummy_view(req):
        current_tenant = get_current_tenant()
        assert current_tenant == tenant
        return None

    middleware = TenantMiddleware(dummy_view)
    response = middleware(request)
    assert response is None  # View executed successfully


@pytest.mark.django_db
def test_header_mismatch_rejected():
    """Test that X-Tenant-ID header mismatch is rejected."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant1)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID=str(tenant2.id))  # Wrong tenant
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 403
    assert "does not match" in response.data["detail"]


@pytest.mark.django_db
def test_invalid_header_format_rejected():
    """Test that invalid X-Tenant-ID header format is rejected."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID="invalid-format")
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 400
    assert "Invalid tenant ID format" in response.data["detail"]


@pytest.mark.django_db
def test_missing_header_uses_user_tenant():
    """Test that missing X-Tenant-ID header uses user's tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/")  # No header
    request.user = user

    def dummy_view(req):
        current_tenant = get_current_tenant()
        assert current_tenant == tenant
        return None

    middleware = TenantMiddleware(dummy_view)
    response = middleware(request)
    assert response is None  # View executed successfully
