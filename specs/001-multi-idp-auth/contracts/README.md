# API Contracts: Multi-Identity Provider Authentication

**Feature**: Multi-Identity Provider Authentication
**Date**: 2025-12-10
**Phase**: 1 - Design & Contracts

## API Changes Summary

**No new API endpoints or modifications required.**

This feature extends existing authentication mechanisms without changing API contracts. All existing API authentication methods continue to work:

- **Basic Authentication**: Unchanged
- **Session Authentication**: Unchanged (works with both database and Azure Entra ID auth)
- **Token Authentication**: Unchanged
- **Remote User Authentication**: Unchanged

## Authentication Flow (Web UI)

The authentication flow occurs at the web UI level, not the API level:

1. User navigates to login page (`/accounts/login/`)
2. User selects authentication method (database or Azure Entra ID)
3. For Azure Entra ID:
   - User redirected to Azure Entra ID authorization endpoint
   - User authenticates with Azure Entra ID
   - Azure Entra ID redirects back to application callback URL
   - Application validates ID token and creates/links account
   - User session established
4. For database auth:
   - User enters username/password
   - Application validates credentials
   - User session established

## API Client Impact

**No impact on API clients.** API clients continue to authenticate using existing methods:

- Basic Auth: `Authorization: Basic <credentials>`
- Token Auth: `Authorization: Token <token>`
- Session Auth: Uses session cookie (automatically works with web login)

API clients are unaffected by whether web users authenticate via database or Azure Entra ID.

## OpenAPI Schema

No changes to OpenAPI schema required. Existing authentication endpoints remain unchanged:

- `/api/token/` - Token acquisition (unchanged)
- `/api/token/generate_auth_token/` - Token generation (unchanged)
- All other API endpoints - No authentication-related changes

## Backward Compatibility

✅ **100% backward compatible** - All existing API clients continue to work without modification.

