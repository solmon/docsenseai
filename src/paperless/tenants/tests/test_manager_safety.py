"""Tests for TenantManager safety mechanisms."""

import pytest
from django.db import models

from paperless.tenants.managers import TenantManager
from paperless.tenants.models import Tenant, TenantModel


class TestModel(TenantModel):
    """Test model for safety tests."""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tenants"


@pytest.mark.django_db
def test_manager_fails_safely_without_context():
    """Test that manager fails safely when tenant context not set."""
    with pytest.raises(ValueError, match="Tenant context not set"):
        TestModel.objects.all()


@pytest.mark.django_db
def test_for_tenant_explicit_override():
    """Test that for_tenant() allows explicit tenant filtering."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create test models using raw SQL
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tenants_testmodel (name, tenant_id) VALUES (%s, %s)",
            ["Item 1", tenant1.id]
        )
        cursor.execute(
            "INSERT INTO tenants_testmodel (name, tenant_id) VALUES (%s, %s)",
            ["Item 2", tenant2.id]
        )

    # for_tenant should work even without context
    items = TestModel.objects.for_tenant(tenant1)
    assert items.count() == 1
