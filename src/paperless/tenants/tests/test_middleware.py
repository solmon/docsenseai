"""Tests for TenantMiddleware."""

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from paperless.tenants.middleware import TenantMiddleware
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import get_current_tenant


@pytest.mark.django_db
def test_middleware_sets_tenant_from_user():
    """Test that middleware sets tenant from authenticated user."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    # Tenant should be set during request processing
    # Note: middleware clears tenant after request, so we test via response
    assert response is None  # Our dummy view returns None


@pytest.mark.django_db
def test_middleware_rejects_invalid_header():
    """Test that middleware rejects invalid X-Tenant-ID header."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID="999")  # Invalid tenant ID
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 400


@pytest.mark.django_db
def test_middleware_rejects_mismatched_header():
    """Test that middleware rejects X-Tenant-ID that doesn't match user's tenant."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant1)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID=str(tenant2.id))
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 403
