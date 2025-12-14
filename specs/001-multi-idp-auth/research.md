# Research: Multi-Identity Provider Authentication

**Feature**: Multi-Identity Provider Authentication
**Date**: 2025-12-10
**Phase**: 0 - Outline & Research

## Research Tasks

### 1. Azure Entra ID Integration Method

**Question**: Should we use django-allauth's Microsoft provider or the generic OIDC provider for Azure Entra ID?

**Research Findings**:
- django-allauth provides `allauth.socialaccount.providers.microsoft` for Microsoft/Azure AD authentication
- django-allauth also provides `allauth.socialaccount.providers.openid_connect` for generic OIDC providers
- Azure Entra ID (formerly Azure AD) supports both Microsoft-specific OAuth 2.0 and standard OIDC protocols
- The application already has OIDC provider support documented in `docs/advanced_usage.md`

**Decision**: Use `allauth.socialaccount.providers.openid_connect` for Azure Entra ID integration.

**Rationale**:
- The application already has OIDC provider infrastructure in place
- OIDC provider is more flexible and follows standard protocols
- Documentation already exists for OIDC setup
- Easier to support other OIDC-compliant providers in the future
- Azure Entra ID fully supports OIDC protocol via Microsoft identity platform v2.0 endpoints

**Alternatives Considered**:
- `allauth.socialaccount.providers.microsoft`: More Microsoft-specific but less flexible
- Custom OAuth 2.0 implementation: Unnecessary complexity when django-allauth handles it

**Configuration Example**:
```json
{
  "openid_connect": {
    "APPS": [{
      "provider_id": "azure_entra",
      "name": "Azure Entra ID",
      "client_id": "<AZURE_CLIENT_ID>",
      "secret": "<AZURE_CLIENT_SECRET>",
      "settings": {
        "server_url": "https://login.microsoftonline.com/<TENANT_ID>/.well-known/openid-configuration"
      }
    }]
  }
}
```

---

### 2. Account Linking Strategy

**Question**: How should we match Azure Entra ID users to existing local accounts?

**Research Findings**:
- django-allauth's `SocialAccount` model links external identities to local `User` accounts
- Email address is the most reliable matching attribute for account linking
- Azure Entra ID provides `email` and `sub` (subject/unique identifier) claims in ID tokens
- The application's `CustomSocialAccountAdapter` already handles social account creation

**Decision**: Use email address as primary matching attribute, with `sub` (unique identifier) as fallback.

**Rationale**:
- Email addresses are typically unique and stable across authentication methods
- Most users will have the same email in both systems
- `sub` claim provides a unique identifier if email matching fails
- django-allauth's `SocialAccount` model supports this linking pattern
- Existing `CustomSocialAccountAdapter.save_user()` can be extended to handle account linking

**Alternatives Considered**:
- Username matching: Less reliable, usernames may differ between systems
- Manual linking only: Poor user experience, requires admin intervention
- Always create new accounts: Breaks user experience continuity

**Implementation Approach**:
1. On Azure Entra ID authentication, extract `email` and `sub` from ID token
2. Check for existing `User` with matching email
3. If found, link `SocialAccount` to existing `User`
4. If not found and auto-signup enabled, create new `User` with email as username
5. Store `sub` in `SocialAccount.uid` for future matching

---

### 3. Session Management

**Question**: How do we ensure single session management across both authentication methods?

**Research Findings**:
- Django's session framework is authentication-method agnostic
- django-allauth creates standard Django user sessions for social accounts
- Existing session middleware (`django.contrib.auth.middleware.AuthenticationMiddleware`) handles both
- Session cookies and session storage work identically regardless of authentication source

**Decision**: Use Django's existing session framework - no changes needed.

**Rationale**:
- Django sessions are already authentication-method agnostic
- django-allauth integrates seamlessly with Django's authentication system
- Both database auth and social auth result in the same `request.user` object
- Existing session configuration (`SESSION_ENGINE`, `SESSION_COOKIE_AGE`) applies to both
- No additional session management code required

**Alternatives Considered**:
- Custom session management: Unnecessary complexity
- Separate session stores: Would break unified user experience

---

### 4. Token Refresh and SSO

**Question**: How do we handle token refresh and Single Sign-On (SSO) for Azure Entra ID?

**Research Findings**:
- django-allauth handles OAuth 2.0 token refresh automatically via `SocialToken` model
- Azure Entra ID supports refresh tokens for maintaining sessions
- SSO is handled by Azure Entra ID's session cookies, not application tokens
- django-allauth's `SocialAccount` stores tokens for automatic refresh

**Decision**: Rely on django-allauth's built-in token refresh mechanism and Azure Entra ID's SSO.

**Rationale**:
- django-allauth automatically refreshes expired access tokens using refresh tokens
- Azure Entra ID maintains its own session cookies for SSO
- When user has active Azure Entra ID session, they're automatically authenticated
- No custom token refresh logic needed

**Alternatives Considered**:
- Custom token refresh implementation: Unnecessary when django-allauth handles it
- Manual token management: More error-prone and complex

---

### 5. Error Handling and Fallback

**Question**: How do we handle Azure Entra ID unavailability without breaking database authentication?

**Research Findings**:
- django-allauth's authentication backends are tried in order
- If social auth fails, Django falls back to next backend in `AUTHENTICATION_BACKENDS`
- Database authentication backend (`django.contrib.auth.backends.ModelBackend`) is always available
- Login page can conditionally show/hide authentication options based on configuration

**Decision**: Use Django's authentication backend fallback mechanism and conditional UI display.

**Rationale**:
- Django's authentication system naturally supports multiple backends with fallback
- If Azure Entra ID is unavailable, users can still use database authentication
- Login UI can check configuration to show/hide Azure Entra ID option
- Error handling in `CustomSocialAccountAdapter` can gracefully handle provider failures

**Alternatives Considered**:
- Disable database auth when Azure Entra ID fails: Poor user experience
- Custom error handling middleware: Unnecessary complexity

---

### 6. Configuration Management

**Question**: How should Azure Entra ID configuration be managed?

**Research Findings**:
- Application uses environment variables for configuration (`PAPERLESS_*` prefix)
- Existing `SOCIALACCOUNT_PROVIDERS` setting uses JSON environment variable
- Configuration is parsed in `settings.py` using `json.loads()`
- Documentation pattern exists in `docs/configuration.md`

**Decision**: Follow existing pattern using `PAPERLESS_SOCIALACCOUNT_PROVIDERS` environment variable.

**Rationale**:
- Consistent with existing social account provider configuration
- No new configuration mechanism needed
- Follows established patterns in the codebase
- Easy for administrators to configure

**Configuration Variables**:
- `PAPERLESS_APPS`: Add `"allauth.socialaccount.providers.openid_connect"` if not already present
- `PAPERLESS_SOCIALACCOUNT_PROVIDERS`: JSON configuration for Azure Entra ID OIDC provider
- `PAPERLESS_DISABLE_REGULAR_LOGIN`: Optional - can disable database auth if desired
- `PAPERLESS_REDIRECT_LOGIN_TO_SSO`: Optional - can auto-redirect to Azure Entra ID

---

### 7. Testing Strategy

**Question**: How do we test Azure Entra ID authentication without actual Azure tenant?

**Research Findings**:
- django-allauth provides test utilities and mocks for social account providers
- OIDC provider can be tested using mock OIDC server or test fixtures
- Existing test patterns in `src/paperless/tests/` use pytest and Django test client
- Integration tests can mock OIDC token responses

**Decision**: Use django-allauth's test utilities and mock OIDC responses for testing.

**Rationale**:
- django-allauth provides `SocialAccountFactory` and test utilities
- Can mock OIDC token responses to test authentication flows
- Unit tests for account linking logic using test fixtures
- Integration tests with mock OIDC provider endpoints
- Follows existing test patterns in the codebase

**Test Coverage Areas**:
1. Azure Entra ID authentication flow (mocked)
2. Account linking by email address
3. Account creation for new users
4. Error handling for provider unavailability
5. Session management across authentication methods
6. Token refresh (mocked)

---

## Summary of Decisions

1. **Integration Method**: Use `allauth.socialaccount.providers.openid_connect` for Azure Entra ID
2. **Account Linking**: Email address as primary, `sub` claim as fallback
3. **Session Management**: Use Django's existing session framework (no changes)
4. **Token Refresh/SSO**: Rely on django-allauth's built-in mechanisms
5. **Error Handling**: Use Django's authentication backend fallback
6. **Configuration**: Follow existing `PAPERLESS_SOCIALACCOUNT_PROVIDERS` pattern
7. **Testing**: Use django-allauth test utilities and mock OIDC responses

## Remaining Clarifications

All technical clarifications have been resolved through research. The implementation approach is clear and follows established patterns in the codebase.

