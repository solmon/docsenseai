"""Tests for TenantManager."""

import pytest
from django.db import models

from paperless.tenants.managers import TenantManager
from paperless.tenants.models import Tenant, TenantModel
from paperless.tenants.utils import set_current_tenant


class TestModel(TenantModel):
    """Test model for manager tests."""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tenants"


@pytest.mark.django_db
def test_tenant_manager_filters_by_current_tenant():
    """Test that TenantManager automatically filters by current tenant."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create test models (using raw create to bypass manager)
    TestModel.objects.using("default").bulk_create(
        [
            TestModel(tenant=tenant1, name="Item 1"),
            TestModel(tenant=tenant2, name="Item 2"),
        ]
    )

    # Set tenant context
    set_current_tenant(tenant1)

    # Query should only return tenant1's items
    items = TestModel.objects.all()
    assert items.count() == 1
    assert items.first().tenant == tenant1


@pytest.mark.django_db
def test_tenant_manager_fails_without_context():
    """Test that TenantManager fails safely when tenant context not set."""
    with pytest.raises(ValueError, match="Tenant context not set"):
        TestModel.objects.all()


@pytest.mark.django_db
def test_for_tenant_explicit_filtering():
    """Test explicit tenant filtering via for_tenant()."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create test models
    TestModel.objects.using("default").bulk_create(
        [
            TestModel(tenant=tenant1, name="Item 1"),
            TestModel(tenant=tenant2, name="Item 2"),
        ]
    )

    # Explicit filtering should work regardless of context
    items = TestModel.objects.for_tenant(tenant1)
    assert items.count() == 1
    assert items.first().tenant == tenant1
