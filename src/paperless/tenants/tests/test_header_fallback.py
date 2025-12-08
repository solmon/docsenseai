"""Tests for missing X-Tenant-ID header fallback."""

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from paperless.tenants.middleware import TenantMiddleware
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import get_current_tenant


@pytest.mark.django_db
def test_missing_header_uses_user_tenant():
    """Test that missing X-Tenant-ID header uses user's tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/")  # No X-Tenant-ID header
    request.user = user

    def dummy_view(req):
        current_tenant = get_current_tenant()
        assert current_tenant == tenant
        return None

    middleware = TenantMiddleware(dummy_view)
    response = middleware(request)
    assert response is None  # View executed successfully


@pytest.mark.django_db
def test_missing_header_with_no_user_tenant():
    """Test that missing header with no user tenant is rejected."""
    user = User.objects.create_user(username="testuser", password="testpass")
    # No UserProfile created

    factory = RequestFactory()
    request = factory.get("/")  # No header
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 403
    assert "No tenant association" in response.data["detail"]
