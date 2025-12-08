"""Integration tests for user-tenant association."""

import pytest
from django.contrib.auth.models import User

from paperless.tenants.models import Tenant, UserProfile


@pytest.mark.django_db
def test_associate_user_with_tenant():
    """Test associating a user with a tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user = User.objects.create_user(username="testuser", password="testpass")

    # Create user profile with tenant
    profile = UserProfile.objects.create(user=user, tenant=tenant)

    assert profile.user == user
    assert profile.tenant == tenant
    assert user.tenant == tenant


@pytest.mark.django_db
def test_user_without_tenant():
    """Test user without tenant association."""
    user = User.objects.create_user(username="testuser", password="testpass")

    assert user.tenant is None


@pytest.mark.django_db
def test_multiple_users_same_tenant():
    """Test multiple users can belong to same tenant."""
    tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
    user1 = User.objects.create_user(username="user1", password="pass1")
    user2 = User.objects.create_user(username="user2", password="pass2")

    UserProfile.objects.create(user=user1, tenant=tenant)
    UserProfile.objects.create(user=user2, tenant=tenant)

    assert user1.tenant == tenant
    assert user2.tenant == tenant
    assert tenant.users.count() == 2
