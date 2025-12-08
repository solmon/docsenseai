"""Integration tests for cross-tenant data isolation."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from documents.models import Document
from paperless.tenants.models import Tenant, UserProfile
from paperless.tenants.utils import set_current_tenant


@pytest.mark.django_db
def test_cross_tenant_data_isolation():
    """Test that users from different tenants cannot see each other's data."""
    tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
    tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

    user_a = User.objects.create_user(username="usera", password="pass")
    user_b = User.objects.create_user(username="userb", password="pass")
    UserProfile.objects.create(user=user_a, tenant=tenant_a)
    UserProfile.objects.create(user=user_b, tenant=tenant_b)

    # Create documents for each tenant
    set_current_tenant(tenant_a)
    doc_a = Document.objects.create(title="Document A", tenant=tenant_a)

    set_current_tenant(tenant_b)
    doc_b = Document.objects.create(title="Document B", tenant=tenant_b)

    # User A should only see tenant A's documents
    set_current_tenant(tenant_a)
    documents = Document.objects.all()
    assert documents.count() == 1
    assert documents.first() == doc_a
    assert documents.first().tenant == tenant_a

    # User B should only see tenant B's documents
    set_current_tenant(tenant_b)
    documents = Document.objects.all()
    assert documents.count() == 1
    assert documents.first() == doc_b
    assert documents.first().tenant == tenant_b


@pytest.mark.django_db
def test_simultaneous_tenant_operations():
    """Test that users from different tenants can operate simultaneously."""
    tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
    tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

    user_a = User.objects.create_user(username="usera", password="pass")
    user_b = User.objects.create_user(username="userb", password="pass")
    UserProfile.objects.create(user=user_a, tenant=tenant_a)
    UserProfile.objects.create(user=user_b, tenant=tenant_b)

    # Simulate simultaneous operations
    set_current_tenant(tenant_a)
    doc_a = Document.objects.create(title="Doc A", tenant=tenant_a)

    set_current_tenant(tenant_b)
    doc_b = Document.objects.create(title="Doc B", tenant=tenant_b)

    # Verify isolation
    set_current_tenant(tenant_a)
    assert Document.objects.count() == 1
    assert Document.objects.first() == doc_a

    set_current_tenant(tenant_b)
    assert Document.objects.count() == 1
    assert Document.objects.first() == doc_b
