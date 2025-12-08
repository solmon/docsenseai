"""Tests for user-tenant association."""

import pytest
from django.contrib.auth.models import User

from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_user_profile_creation():
    """Test creating user profile with tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")

    profile = UserProfile.objects.create(user=user, tenant=tenant)

    assert profile.user == user
    assert profile.tenant == tenant
    assert user.tenant == tenant


@pytest.mark.django_db
def test_user_tenant_property():
    """Test user.tenant property access."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")
    UserProfile.objects.create(user=user, tenant=tenant)

    assert user.tenant == tenant


@pytest.mark.django_db
def test_user_without_tenant():
    """Test user without tenant returns None."""
    user = User.objects.create_user(username="testuser", password="testpass")

    assert user.tenant is None
