"""Tests for automatic tenant assignment on document creation."""

import pytest

from documents.models import Document
from paperless.tenants.models import Tenant
from paperless.tenants.utils import set_current_tenant


@pytest.mark.django_db
def test_document_auto_assigns_tenant():
    """Test that document automatically assigns tenant from context."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

    set_current_tenant(tenant)

    # Create document without explicitly setting tenant
    doc = Document(title="Test Document")
    doc.save()  # Should auto-assign tenant

    assert doc.tenant == tenant
    assert doc.tenant_id == tenant.id


@pytest.mark.django_db
def test_document_fails_without_tenant_context():
    """Test that document creation fails if tenant context not set."""
    # Don't set tenant context

    doc = Document(title="Test Document")

    with pytest.raises(ValueError, match="Tenant context not set"):
        doc.save()
