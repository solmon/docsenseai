"""Tests for raw SQL query tenant filtering."""

import pytest
from django.db import connection

from paperless.tenants.models import Tenant
from paperless.tenants.utils import get_current_tenant, set_current_tenant


@pytest.mark.django_db
def test_raw_sql_queries_should_include_tenant_filter():
    """Test that raw SQL queries should manually include tenant filtering."""
    tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")

    # Create test data
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Doc 1", tenant1.id]
        )
        cursor.execute(
            "INSERT INTO documents_document (title, tenant_id, created, added) VALUES (%s, %s, NOW(), NOW())",
            ["Doc 2", tenant2.id]
        )

    set_current_tenant(tenant1)

    # Raw SQL queries must manually include tenant filter
    with connection.cursor() as cursor:
        tenant = get_current_tenant()
        cursor.execute(
            "SELECT COUNT(*) FROM documents_document WHERE tenant_id = %s",
            [tenant.id]
        )
        count = cursor.fetchone()[0]
        assert count == 1
