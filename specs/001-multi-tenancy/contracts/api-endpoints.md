# API Endpoints: Multi-Tenancy Support

**Feature**: Multi-Tenancy Support
**Date**: 2025-01-27
**Status**: API Version 10

## API Version

**Version**: 10 (new version required for multi-tenancy features)
**Base URL**: `/api/`
**Version Header**: `Accept: application/json; version=10`

## Authentication & Tenant Context

**Authentication**: Same as existing API (Basic, Session, Token, Remote User)

**Tenant Context**:
- **Required Header**: `X-Tenant-ID: <tenant_id>` for all authenticated requests
- **Validation**: Tenant ID must match user's tenant association (unless super admin)
- **Fallback**: If header not provided, uses user's default tenant from UserProfile
- **Error**: Returns 400/403 if tenant invalid or doesn't match user's association

## Tenant Management Endpoints (Super Admin Only)

**Base**: `/api/tenants/`

### List Tenants

**Endpoint**: `GET /api/tenants/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Query Parameters**:
- `is_active`: Filter by active status (true/false)
- `search`: Search by name or identifier
- `ordering`: Sort field (name, created_at, updated_at)
- `page`: Page number for pagination
- `page_size`: Items per page

**Response**: Paginated list of tenants

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "identifier": "acme-corp",
      "is_active": true,
      "deleted_at": null,
      "created_at": "2025-01-27T10:00:00Z",
      "updated_at": "2025-01-27T10:00:00Z"
    }
  ]
}
```

### Retrieve Tenant

**Endpoint**: `GET /api/tenants/{id}/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Response**: Single tenant object

### Create Tenant

**Endpoint**: `POST /api/tenants/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Request Body**:
```json
{
  "name": "New Tenant",
  "identifier": "new-tenant",
  "is_active": true
}
```

**Validation**:
- Name: Required, max 255 characters
- Identifier: Required, unique, URL-safe pattern `^[a-z0-9_-]+$`
- is_active: Optional, defaults to true

**Response**: Created tenant object (201 Created)

### Update Tenant

**Endpoint**: `PATCH /api/tenants/{id}/` or `PUT /api/tenants/{id}/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Request Body** (partial update):
```json
{
  "name": "Updated Tenant Name",
  "identifier": "updated-identifier",
  "is_active": false
}
```

**Response**: Updated tenant object (200 OK)

### Delete Tenant (Soft Delete)

**Endpoint**: `DELETE /api/tenants/{id}/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Behavior**: Soft deletes tenant (sets `deleted_at`, `is_active=False`)

**Response**: 204 No Content

### Activate Tenant

**Endpoint**: `POST /api/tenants/{id}/activate/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Response**: Updated tenant object with `is_active=True` (200 OK)

### Deactivate Tenant

**Endpoint**: `POST /api/tenants/{id}/deactivate/`

**Authentication**: Required (super admin only)

**Permissions**: `is_superuser=True` required

**Behavior**: Sets `is_active=False`, invalidates active user sessions

**Response**: Updated tenant object with `is_active=False` (200 OK)

## User Tenant Association Endpoints

### Get User's Tenants

**Endpoint**: `GET /api/users/{id}/tenants/`

**Authentication**: Required

**Permissions**: User can view own tenants, super admin can view any user's tenants

**Response**: List of tenants associated with user

```json
[
  {
    "id": 1,
    "name": "Acme Corporation",
    "identifier": "acme-corp",
    "is_active": true
  }
]
```

### Get Current User's Tenant

**Endpoint**: `GET /api/profile/tenant/`

**Authentication**: Required

**Response**: Current user's tenant (from UserProfile)

```json
{
  "id": 1,
  "name": "Acme Corporation",
  "identifier": "acme-corp",
  "is_active": true
}
```

## Modified Existing Endpoints (Version 10)

All existing endpoints in version 10 are tenant-scoped:

### Documents

**Base**: `/api/documents/`

- All queries automatically filtered by current tenant context
- X-Tenant-ID header required (or uses user's default tenant)
- Cross-tenant access denied (404 or 403)

### Tags, Correspondents, Document Types, etc.

**Base**: `/api/tags/`, `/api/correspondents/`, `/api/document_types/`, etc.

- All queries automatically filtered by current tenant context
- All create/update operations scoped to current tenant
- Cross-tenant access denied

## Error Responses

### Missing Tenant Context

**Status**: 400 Bad Request

**Response**:
```json
{
  "detail": "Tenant context not set. Include X-Tenant-ID header or ensure user has tenant association."
}
```

### Invalid Tenant ID

**Status**: 400 Bad Request

**Response**:
```json
{
  "detail": "Invalid tenant ID."
}
```

### Tenant Mismatch

**Status**: 403 Forbidden

**Response**:
```json
{
  "detail": "Tenant ID in header does not match your tenant association."
}
```

### Inactive Tenant

**Status**: 403 Forbidden

**Response**:
```json
{
  "detail": "Your tenant account is inactive."
}
```

### Super Admin Required

**Status**: 403 Forbidden

**Response**:
```json
{
  "detail": "Super admin access required for tenant management."
}
```

## Request/Response Examples

### Create Tenant (Super Admin)

```http
POST /api/tenants/ HTTP/1.1
Accept: application/json; version=10
Authorization: Token <super_admin_token>
Content-Type: application/json

{
  "name": "New Organization",
  "identifier": "new-org",
  "is_active": true
}
```

**Response**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 2,
  "name": "New Organization",
  "identifier": "new-org",
  "is_active": true,
  "deleted_at": null,
  "created_at": "2025-01-27T12:00:00Z",
  "updated_at": "2025-01-27T12:00:00Z"
}
```

### List Documents (Tenant-Scoped)

```http
GET /api/documents/?page=1&page_size=25 HTTP/1.1
Accept: application/json; version=10
Authorization: Token <user_token>
X-Tenant-ID: 1
```

**Response**: Only documents belonging to tenant 1 are returned

### Switch Tenant Context

```http
GET /api/documents/ HTTP/1.1
Accept: application/json; version=10
Authorization: Token <user_token>
X-Tenant-ID: 2
```

**Response**: Only documents belonging to tenant 2 are returned (if user has access to tenant 2)

## Backward Compatibility

**Versions 1-9**:
- No X-Tenant-ID header required
- No tenant filtering applied
- Maintains single-tenant behavior
- Existing API clients continue to work

**Version 10**:
- X-Tenant-ID header required (or uses user's default tenant)
- All responses tenant-scoped
- New tenant management endpoints available
- Multi-tenant deployments must use version 10

## Notes

- All tenant management endpoints require super admin access (`is_superuser=True`)
- Regular users can only view their associated tenant(s)
- Tenant activation/deactivation immediately affects user access
- Soft-deleted tenants are excluded from normal queries but visible to super admin
- All existing endpoints in version 10 automatically filter by tenant context

