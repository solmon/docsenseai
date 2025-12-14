# Data Model: Multi-Identity Provider Authentication

**Feature**: Multi-Identity Provider Authentication
**Date**: 2025-12-10
**Phase**: 1 - Design & Contracts

## Overview

This feature leverages existing Django and django-allauth models. No new database models are required. The implementation extends existing models and adapters to support Azure Entra ID authentication alongside database authentication.

## Existing Models (No Changes Required)

### User (django.contrib.auth.models.User)

**Purpose**: Represents a user account in the system, regardless of authentication method.

**Key Attributes**:
- `username`: String, unique identifier (used for database auth)
- `email`: String, email address (used for account linking)
- `is_active`: Boolean, whether account is active
- `is_staff`: Boolean, staff/admin privileges
- `is_superuser`: Boolean, superuser privileges
- `date_joined`: DateTime, account creation timestamp
- `last_login`: DateTime, last login timestamp

**Relationships**:
- One-to-many with `SocialAccount` (django-allauth)
- Many-to-many with `Group` (Django permissions)
- One-to-many with `SocialToken` (django-allauth, for token storage)

**Usage in This Feature**:
- Same User model used for both database and Azure Entra ID authentication
- Email field used for account linking between Azure Entra ID and local accounts
- No schema changes required

### SocialAccount (allauth.socialaccount.models.SocialAccount)

**Purpose**: Links external identity provider accounts to local User accounts.

**Key Attributes**:
- `user`: ForeignKey to User, the linked local user account
- `provider`: String, identity provider identifier (e.g., "openid_connect")
- `uid`: String, unique identifier from the identity provider
- `extra_data`: JSONField, additional provider-specific data
- `date_joined`: DateTime, when account was linked

**Relationships**:
- Many-to-one with User
- One-to-many with SocialToken

**Usage in This Feature**:
- Stores Azure Entra ID account information
- `uid` field stores the `sub` (subject) claim from Azure Entra ID
- `extra_data` stores additional claims (email, name, etc.)
- Links Azure Entra ID identity to local User account

**Validation Rules**:
- `provider` + `uid` must be unique (enforced by django-allauth)
- `user` must reference a valid User instance

### SocialToken (allauth.socialaccount.models.SocialToken)

**Purpose**: Stores OAuth 2.0 tokens for social account providers.

**Key Attributes**:
- `app`: ForeignKey to SocialApp (provider configuration)
- `account`: ForeignKey to SocialAccount
- `token`: TextField, access token
- `token_secret`: TextField, refresh token (if applicable)
- `expires_at`: DateTime, token expiration time

**Usage in This Feature**:
- Stores Azure Entra ID access tokens and refresh tokens
- django-allauth automatically refreshes expired tokens using refresh tokens
- No schema changes required

### SocialApp (allauth.socialaccount.models.SocialApp)

**Purpose**: Configuration for social account providers.

**Key Attributes**:
- `provider`: String, provider identifier (e.g., "openid_connect")
- `name`: String, human-readable provider name
- `client_id`: String, OAuth client ID
- `secret`: String, OAuth client secret
- `key`: String, optional provider-specific key
- `settings`: JSONField, provider-specific settings

**Usage in This Feature**:
- Configured via `PAPERLESS_SOCIALACCOUNT_PROVIDERS` environment variable
- Stores Azure Entra ID OIDC configuration (client_id, secret, server_url)
- No schema changes required

## Data Flow

### Account Linking Flow

1. **User authenticates via Azure Entra ID**
   - Azure Entra ID returns ID token with claims (email, sub, name, etc.)
   - django-allauth creates/updates `SocialAccount` with provider="openid_connect", uid=sub

2. **Account Matching**
   - System extracts `email` claim from ID token
   - Queries `User` model for user with matching email
   - If found: Links `SocialAccount` to existing `User`
   - If not found and auto-signup enabled: Creates new `User` with email as username

3. **Token Storage**
   - django-allauth creates `SocialToken` linked to `SocialAccount`
   - Stores access token and refresh token
   - Automatically refreshes tokens when expired

### Session Management

- Django's session framework stores session data independently of authentication method
- `request.user` is populated from either:
  - Database authentication: `django.contrib.auth.backends.ModelBackend`
  - Azure Entra ID: `allauth.account.auth_backends.AuthenticationBackend`
- Session cookie and session storage work identically for both methods

## State Transitions

### User Account States

```
[No Account]
    ↓ (Azure Entra ID auth + auto-signup enabled)
[New User Account Created]
    ↓ (Account linking)
[Linked to Azure Entra ID]
    ↓ (Login via Azure Entra ID)
[Active Session]
    ↓ (Logout)
[No Active Session]
```

### Account Linking States

```
[Unlinked User Account]
    ↓ (First Azure Entra ID login with matching email)
[Linked Account]
    ↓ (Subsequent Azure Entra ID logins)
[Active Session with Linked Account]
```

## Validation Rules

### Account Linking

- Email matching: Case-insensitive comparison
- Unique constraint: One `SocialAccount` per provider + uid combination
- User must exist before linking (or be created during auto-signup)

### Token Management

- Access tokens must be validated before use
- Refresh tokens used automatically by django-allauth
- Expired tokens trigger automatic refresh or re-authentication

## Data Integrity

### Constraints

- `SocialAccount.provider` + `SocialAccount.uid` must be unique (enforced by django-allauth)
- `User.email` should be unique for reliable account linking (Django model constraint)
- `SocialToken.account` must reference valid `SocialAccount`

### Cascading Behavior

- If `User` is deleted: Related `SocialAccount` and `SocialToken` records are deleted (CASCADE)
- If `SocialAccount` is deleted: Related `SocialToken` records are deleted (CASCADE)

## Migration Strategy

**No database migrations required** - this feature uses existing django-allauth models and Django User model without schema changes.

## Performance Considerations

- Account linking queries: Index on `User.email` for fast email-based lookups
- SocialAccount queries: django-allauth provides indexes on `provider` and `uid`
- Token refresh: django-allauth handles token refresh asynchronously when possible

## Security Considerations

- Client secrets stored in `SocialApp.secret` (should be encrypted at rest in production)
- Tokens stored in `SocialToken` (should be encrypted at rest)
- Email addresses used for account linking should be validated
- ID token validation ensures tokens are from trusted Azure Entra ID tenant

