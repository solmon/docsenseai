"""Tests for X-Tenant-ID header mismatch rejection."""

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from paperless.tenants.middleware import TenantMiddleware
from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_header_mismatch_rejected():
    """Test that X-Tenant-ID header mismatch is rejected."""
    tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
    tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant_a)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID=str(tenant_b.id))  # Wrong tenant
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 403
    assert "does not match" in response.data["detail"]


@pytest.mark.django_db
def test_header_mismatch_logged():
    """Test that header mismatch is logged."""
    tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
    tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant_a)

    factory = RequestFactory()
    request = factory.get("/", HTTP_X_TENANT_ID=str(tenant_b.id))
    request.user = user

    middleware = TenantMiddleware(lambda req: None)
    response = middleware(request)

    assert response.status_code == 403
