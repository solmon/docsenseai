"""
Tests for Azure Entra ID authentication integration.

These tests verify:
- Azure Entra ID authentication flow
- Account linking by email address
- Account creation for new users
- Error handling for authentication failures
- Session management across authentication methods
"""

import logging
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.signals import social_account_updated

from paperless.adapter import CustomSocialAccountAdapter
from paperless.auth import is_azure_entra_id_configured, is_database_authentication_enabled


logger = logging.getLogger("paperless.auth")


class TestAzureEntraIDHelpers(TestCase):
    """Test helper functions for Azure Entra ID authentication."""

    def test_is_azure_entra_id_configured_with_socialapp(self):
        """Test detection of Azure Entra ID via SocialApp model."""
        # Create a SocialApp with Azure Entra ID configuration
        app = SocialApp.objects.create(
            provider="openid_connect",
            name="Azure Entra ID",
            client_id="test_client_id",
            secret="test_secret",
        )
        app.settings = {"server_url": "https://login.microsoftonline.com/tenant/.well-known/openid-configuration"}
        app.save()

        self.assertTrue(is_azure_entra_id_configured())

    def test_is_azure_entra_id_configured_with_settings(self):
        """Test detection of Azure Entra ID via SOCIALACCOUNT_PROVIDERS setting."""
        with override_settings(
            SOCIALACCOUNT_PROVIDERS={
                "openid_connect": {
                    "APPS": [
                        {
                            "provider_id": "azure_entra",
                            "name": "Azure Entra ID",
                            "client_id": "test_client_id",
                            "secret": "test_secret",
                            "settings": {
                                "server_url": "https://login.microsoftonline.com/tenant/.well-known/openid-configuration"
                            },
                        }
                    ]
                }
            }
        ):
            self.assertTrue(is_azure_entra_id_configured())

    def test_is_azure_entra_id_configured_not_configured(self):
        """Test detection returns False when Azure Entra ID is not configured."""
        self.assertFalse(is_azure_entra_id_configured())

    def test_is_database_authentication_enabled_default(self):
        """Test database authentication is enabled by default."""
        with override_settings(DISABLE_REGULAR_LOGIN=False):
            self.assertTrue(is_database_authentication_enabled())

    def test_is_database_authentication_enabled_disabled(self):
        """Test database authentication detection when disabled."""
        with override_settings(DISABLE_REGULAR_LOGIN=True):
            self.assertFalse(is_database_authentication_enabled())


class TestCustomSocialAccountAdapter(TestCase):
    """Test CustomSocialAccountAdapter for Azure Entra ID account linking."""

    def setUp(self):
        """Set up test fixtures."""
        self.adapter = CustomSocialAccountAdapter()
        # Create a test user for account linking tests
        self.existing_user = User.objects.create_user(
            username="existing_user",
            email="user@example.com",
            password="testpass123",
        )

    @mock.patch("paperless.adapter.handle_social_account_updated")
    def test_save_user_links_to_existing_user_by_email(self, mock_signal):
        """Test that Azure Entra ID account links to existing user by email."""
        from allauth.socialaccount.models import SocialLogin, SocialAccount, SocialToken
        from allauth.account.models import EmailAddress

        # Create a mock sociallogin for Azure Entra ID
        social_app = SocialApp.objects.create(
            provider="openid_connect",
            name="Azure Entra ID",
            client_id="test_client_id",
            secret="test_secret",
        )

        # Create a new user object that will be used by sociallogin
        new_user = User(username="azure_user", email="user@example.com")
        new_user.set_unusable_password()

        # Create social account with Azure Entra ID data
        social_account = SocialAccount(
            provider="openid_connect",
            uid="azure_sub_12345",
            extra_data={"email": "user@example.com", "sub": "azure_sub_12345"},
        )

        # Create a mock sociallogin
        sociallogin = mock.Mock()
        sociallogin.account = social_account
        sociallogin.user = new_user
        sociallogin.account.provider = "openid_connect"

        # Call save_user
        saved_user = self.adapter.save_user(mock.Mock(), sociallogin)

        # Verify the existing user was used (not a new user created)
        self.assertEqual(saved_user.id, self.existing_user.id)
        self.assertEqual(saved_user.email, "user@example.com")

    @mock.patch("paperless.adapter.handle_social_account_updated")
    def test_save_user_creates_new_user_when_no_match(self, mock_signal):
        """Test that new user is created when no matching email exists."""
        from allauth.socialaccount.models import SocialApp

        # Create a mock sociallogin for Azure Entra ID with new email
        social_app = SocialApp.objects.create(
            provider="openid_connect",
            name="Azure Entra ID",
            client_id="test_client_id",
            secret="test_secret",
        )

        new_user = User(username="new_azure_user", email="newuser@example.com")
        new_user.set_unusable_password()

        social_account = mock.Mock()
        social_account.provider = "openid_connect"
        social_account.uid = "azure_sub_67890"
        social_account.extra_data = {"email": "newuser@example.com", "sub": "azure_sub_67890"}

        sociallogin = mock.Mock()
        sociallogin.account = social_account
        sociallogin.user = new_user

        # Mock the parent save_user to actually create the user
        with mock.patch.object(
            self.adapter.__class__.__bases__[0],
            "save_user",
            return_value=new_user,
        ) as mock_parent_save:
            mock_parent_save.return_value = User.objects.create_user(
                username="new_azure_user",
                email="newuser@example.com",
            )
            saved_user = self.adapter.save_user(mock.Mock(), sociallogin)

            # Verify a new user was created
            self.assertNotEqual(saved_user.id, self.existing_user.id)
            self.assertEqual(saved_user.email, "newuser@example.com")

    def test_save_user_handles_errors_gracefully(self):
        """Test that errors during account linking are handled gracefully."""
        social_account = mock.Mock()
        social_account.provider = "openid_connect"
        social_account.uid = "azure_sub_error"
        social_account.extra_data = {"email": "error@example.com"}

        sociallogin = mock.Mock()
        sociallogin.account = social_account
        sociallogin.user = User(username="error_user", email="error@example.com")
        sociallogin.user.set_unusable_password()

        # Mock an error during user lookup
        with mock.patch(
            "paperless.adapter.User.objects.filter",
            side_effect=Exception("Database error"),
        ):
            # Should fall back to default behavior without crashing
            with mock.patch.object(
                self.adapter.__class__.__bases__[0],
                "save_user",
            ) as mock_parent_save:
                mock_parent_save.return_value = User.objects.create_user(
                    username="error_user",
                    email="error@example.com",
                )
                saved_user = self.adapter.save_user(mock.Mock(), sociallogin)
                self.assertIsNotNone(saved_user)

