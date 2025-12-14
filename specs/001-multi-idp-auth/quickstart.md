# Quick Start Guide: Multi-Identity Provider Authentication

**Feature**: Multi-Identity Provider Authentication
**Date**: 2025-12-10
**Phase**: 1 - Design & Contracts

## Overview

This guide provides step-by-step instructions for configuring Azure Entra ID (Microsoft Entra ID) authentication alongside existing database authentication in Paperless-ngx.

## Prerequisites

1. Azure Entra ID tenant with administrative access
2. Paperless-ngx installation with django-allauth already installed (included by default)
3. Network connectivity to Microsoft identity platform endpoints

## Step 1: Register Application in Azure Entra ID

1. Navigate to [Azure Portal](https://portal.azure.com/)
2. Go to **Microsoft Entra ID** > **App registrations**
3. Click **New registration**
4. Configure:
   - **Name**: Paperless-ngx (or your preferred name)
   - **Supported account types**: Accounts in this organizational directory only (or as needed)
   - **Redirect URI**:
     - Type: Web
     - URI: `https://your-paperless-domain.com/accounts/openid_connect/login/callback/`
5. Click **Register**
6. Note the **Application (client) ID** and **Directory (tenant) ID**

## Step 2: Configure Application in Azure Entra ID

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add description and expiration, then click **Add**
4. **Copy the secret value immediately** (it won't be shown again)
5. Go to **API permissions** and verify default permissions are sufficient
6. Go to **Authentication** and verify redirect URI is configured correctly

## Step 3: Configure Paperless-ngx

### Environment Variables

Add the following to your Paperless-ngx environment configuration:

```bash
# Enable OpenID Connect provider
PAPERLESS_APPS="allauth.socialaccount.providers.openid_connect"

# Configure Azure Entra ID OIDC provider
PAPERLESS_SOCIALACCOUNT_PROVIDERS='{
  "openid_connect": {
    "APPS": [{
      "provider_id": "azure_entra",
      "name": "Azure Entra ID",
      "client_id": "<YOUR_CLIENT_ID>",
      "secret": "<YOUR_CLIENT_SECRET>",
      "settings": {
        "server_url": "https://login.microsoftonline.com/<YOUR_TENANT_ID>/.well-known/openid-configuration"
      }
    }]
  }
}'

# Optional: Allow automatic account creation for new Azure Entra ID users
PAPERLESS_SOCIAL_AUTO_SIGNUP=yes

# Optional: Set default groups for new Azure Entra ID users
PAPERLESS_SOCIAL_ACCOUNT_DEFAULT_GROUPS="Users"

# Optional: Disable regular login (database auth) if you only want Azure Entra ID
# PAPERLESS_DISABLE_REGULAR_LOGIN=yes

# Optional: Automatically redirect to Azure Entra ID login
# PAPERLESS_REDIRECT_LOGIN_TO_SSO=yes
```

### Replace Placeholders

- `<YOUR_CLIENT_ID>`: Application (client) ID from Step 1
- `<YOUR_CLIENT_SECRET>`: Client secret value from Step 2
- `<YOUR_TENANT_ID>`: Directory (tenant) ID from Step 1

## Step 4: Restart Paperless-ngx

Restart your Paperless-ngx service to apply configuration changes:

```bash
# Docker Compose
docker-compose restart paperless-webserver

# Systemd
systemctl restart paperless-webserver
```

## Step 5: Test Authentication

1. Navigate to your Paperless-ngx login page
2. You should see both authentication options:
   - Database authentication (username/password)
   - Azure Entra ID (button/link)
3. Click the Azure Entra ID option
4. You should be redirected to Microsoft's login page
5. After successful authentication, you should be redirected back to Paperless-ngx and logged in

## Account Linking

### Automatic Linking

If a user's Azure Entra ID email matches an existing Paperless-ngx user email:
- The accounts are automatically linked
- The user retains all existing permissions and data access
- No duplicate account is created

### Manual Linking

Users can manually link accounts:
1. Log in with database credentials
2. Go to **My Profile** in the user dropdown
3. Click **Connect** next to Azure Entra ID
4. Complete Azure Entra ID authentication
5. Accounts are now linked

## Troubleshooting

### Issue: Redirect URI Mismatch

**Error**: "redirect_uri_mismatch"

**Solution**: Ensure the redirect URI in Azure Entra ID exactly matches:
```
https://your-paperless-domain.com/accounts/openid_connect/login/callback/
```

### Issue: Invalid Client Secret

**Error**: "invalid_client"

**Solution**:
- Verify client secret is correct
- Check if secret has expired (create new secret if needed)
- Ensure no extra spaces in environment variable

### Issue: Account Not Created

**Error**: User authenticates but account not created

**Solution**:
- Check `PAPERLESS_SOCIAL_AUTO_SIGNUP=yes` is set
- Verify `PAPERLESS_SOCIALACCOUNT_ALLOW_SIGNUPS=yes` (default is yes)
- Check application logs for errors

### Issue: Can't See Azure Entra ID Option

**Solution**:
- Verify `PAPERLESS_APPS` includes `allauth.socialaccount.providers.openid_connect`
- Check `PAPERLESS_SOCIALACCOUNT_PROVIDERS` JSON is valid
- Restart Paperless-ngx service
- Clear browser cache

## Advanced Configuration

### Custom Attribute Mapping

To customize which Azure Entra ID attributes are used:

```json
{
  "openid_connect": {
    "APPS": [{
      "provider_id": "azure_entra",
      "name": "Azure Entra ID",
      "client_id": "<CLIENT_ID>",
      "secret": "<CLIENT_SECRET>",
      "settings": {
        "server_url": "https://login.microsoftonline.com/<TENANT_ID>/.well-known/openid-configuration",
        "OAUTH_PKCE_ENABLED": true
      }
    }]
  }
}
```

### Multiple Tenants

To support multiple Azure Entra ID tenants, add multiple APPS entries with different `provider_id` values.

### SSO Configuration

For Single Sign-On (SSO) to work:
- Users must have active Azure Entra ID sessions in their browser
- Azure Entra ID must be configured to allow SSO
- Application must be configured in Azure Entra ID with appropriate SSO settings

## Security Considerations

1. **Client Secrets**: Store securely, never commit to version control
2. **HTTPS**: Always use HTTPS in production
3. **Token Validation**: django-allauth automatically validates ID tokens
4. **Session Security**: Follow Django session security best practices
5. **Audit Logging**: Authentication events are logged for security auditing

## Additional Resources

- [django-allauth OIDC Provider Documentation](https://docs.allauth.org/en/latest/socialaccount/providers/openid_connect.html)
- [Azure Entra ID OIDC Documentation](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc)
- [Paperless-ngx Configuration Documentation](../docs/configuration.md)

