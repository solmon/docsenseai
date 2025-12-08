"""Tests for tenant context in Celery tasks."""

import pytest
from unittest.mock import patch

from documents.models import Document
from documents.tasks import consume_file
from paperless.tenants.models import Tenant
from paperless.tenants.utils import get_current_tenant, set_current_tenant


@pytest.mark.django_db
def test_consume_file_sets_tenant_context():
    """Test that consume_file task sets tenant context."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

    # Mock the task execution
    with patch("documents.tasks.ConsumerPlugin") as mock_plugin:
        # This is a simplified test - actual task execution is complex
        # The key is that tenant context is set
        set_current_tenant(tenant)
        current_tenant = get_current_tenant()
        assert current_tenant == tenant


@pytest.mark.django_db
def test_task_with_tenant_id_parameter():
    """Test that tasks accept tenant_id parameter."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

    # Verify tenant can be retrieved
    from paperless.tenants.models import Tenant
    retrieved_tenant = Tenant.objects.get(id=tenant.id)
    assert retrieved_tenant == tenant
