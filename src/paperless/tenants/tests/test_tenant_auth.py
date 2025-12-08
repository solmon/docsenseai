"""Integration tests for tenant context in authentication."""

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from paperless.tenants.middleware import TenantMiddleware
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import get_current_tenant


@pytest.mark.django_db
def test_tenant_context_set_on_authenticated_request():
    """Test that tenant context is set for authenticated user."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    def dummy_view(req):
        # Check tenant context is set
        current_tenant = get_current_tenant()
        assert current_tenant == tenant
        return None

    middleware = TenantMiddleware(dummy_view)
    middleware(request)


@pytest.mark.django_db
def test_user_without_tenant_cannot_access():
    """Test that user without tenant cannot access system."""
    user = User.objects.create_user(username="testuser", password="testpass")
    # No UserProfile created

    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 403
    assert "No tenant association" in response.data["detail"]
