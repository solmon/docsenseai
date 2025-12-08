"""Tests for tenant context utilities."""

import pytest

from paperless.tenants.models import Tenant
from paperless.tenants.utils import clear_current_tenant, get_current_tenant, set_current_tenant


@pytest.mark.django_db
def test_set_and_get_current_tenant():
    """Test setting and getting current tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

    assert get_current_tenant() is None

    set_current_tenant(tenant)
    assert get_current_tenant() == tenant

    clear_current_tenant()
    assert get_current_tenant() is None


@pytest.mark.django_db
def test_clear_current_tenant():
    """Test clearing current tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

    set_current_tenant(tenant)
    assert get_current_tenant() == tenant

    clear_current_tenant()
    assert get_current_tenant() is None
