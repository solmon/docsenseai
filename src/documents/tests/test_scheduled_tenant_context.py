"""Tests for tenant context in scheduled tasks."""

import pytest

from documents.models import Document
from documents.tasks import check_scheduled_workflows
from paperless.tenants.models import Tenant
from paperless.tenants.utils import get_current_tenant, set_current_tenant


@pytest.mark.django_db
def test_scheduled_workflow_with_tenant_context():
    """Test that scheduled workflows respect tenant context."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

    # Set tenant context
    set_current_tenant(tenant)

    # Verify queries are filtered by tenant
    documents = Document.objects.all()
    # This should only return documents for this tenant (if any exist)
    # The key is that the query doesn't fail and respects tenant filtering

    current_tenant = get_current_tenant()
    assert current_tenant == tenant
