# Research: Multi-Tenancy Implementation Decisions

**Feature**: Multi-Tenancy Support
**Date**: 2025-01-27
**Status**: Current Implementation Analysis

## Multi-Tenancy Architecture Decision

**Decision**: Shared database with logical data separation via tenant_id column (existing implementation).

**Rationale**:
- Leverages existing TenantModel infrastructure already in codebase
- Simpler than separate databases or schemas per tenant
- Good performance with proper indexing
- Easier backup and maintenance
- Supports 50+ tenants efficiently

**Alternatives Considered**:
- **Separate databases per tenant**: Best isolation but highest operational complexity, cost, and maintenance overhead
- **Separate schemas per tenant**: Better isolation but requires schema management, more complex migrations
- **Third-party libraries (django-tenants)**: Adds dependency, may not fit exact requirements, existing custom implementation is sufficient

## Tenant Context Management

**Decision**: Thread-local storage with middleware-based context setting (existing implementation).

**Rationale**:
- Thread-local storage ensures tenant context is isolated per request
- Middleware automatically sets context from X-Tenant-ID header or user's tenant
- Works seamlessly with Django's request/response cycle
- Clear separation of concerns

**Implementation**:
- `threading.local()` for thread-local storage
- `TenantMiddleware` sets context from request
- `TenantManager` automatically filters queries by current tenant
- Context cleared after request completion

**Alternatives Considered**:
- **Request attributes**: Less isolated, could leak between requests
- **Global variables**: Not thread-safe, would cause data leakage
- **Context variables (Python 3.7+)**: Similar to thread-local but less explicit

## Query Filtering Strategy

**Decision**: Automatic filtering via custom TenantManager (existing implementation).

**Rationale**:
- Prevents accidental cross-tenant data access
- Transparent to application code
- Consistent across all tenant-specific models
- Fails safely if tenant context not set

**Implementation**:
- `TenantModel` base class with `TenantManager`
- `TenantManager.get_queryset()` automatically filters by `get_current_tenant()`
- Raises error if tenant context not set (prevents data leakage)
- Explicit `for_tenant()` method for super admin cross-tenant access

**Alternatives Considered**:
- **Manual filtering in views**: Error-prone, easy to forget, inconsistent
- **Middleware query modification**: Too invasive, breaks ORM patterns
- **Database-level row security**: Database-specific, less portable

## Super Admin Role

**Decision**: Use Django's built-in `is_superuser` flag for super admin access.

**Rationale**:
- Leverages existing Django authentication system
- Already used throughout codebase for admin access
- No additional user model changes required
- Well-understood by Django developers

**Implementation**:
- Check `user.is_superuser` for tenant management access
- Super admin can access tenant management endpoints
- Super admin can view/manage all tenants
- Regular users restricted to their associated tenant(s)

**Alternatives Considered**:
- **Custom permission**: More flexible but adds complexity
- **Separate admin user model**: Unnecessary, Django User sufficient
- **Group-based permissions**: More complex, is_superuser is simpler for this use case

## Tenant Identification in API

**Decision**: X-Tenant-ID HTTP header for tenant identification in API requests.

**Rationale**:
- Standard HTTP header approach
- Works with all HTTP clients
- Can be set by frontend interceptor automatically
- Verified against user's tenant association for security

**Implementation**:
- Frontend includes `X-Tenant-ID: <tenant_id>` in all API requests
- Middleware extracts header and validates against user's tenant
- Falls back to user's default tenant if header not provided
- Rejects requests if tenant mismatch detected

**Alternatives Considered**:
- **URL path parameter** (`/api/tenants/{id}/documents/`): More RESTful but requires URL changes, breaks existing API structure
- **Query parameter** (`?tenant_id=123`): Easy to forget, less secure
- **JWT token claims**: More complex, requires token changes

## Frontend Tenant Context Management

**Decision**: Angular service-based tenant context with HTTP interceptor.

**Rationale**:
- Service provides centralized tenant state management
- Interceptor automatically adds header to all requests
- Reactive updates when tenant changes
- Follows Angular best practices

**Implementation**:
- `TenantContextService` manages current tenant selection
- `TenantInterceptor` adds X-Tenant-ID header to all HTTP requests
- Tenant selection persisted in session storage
- Service emits events when tenant changes

**Alternatives Considered**:
- **Global variable**: Not reactive, harder to test
- **Route parameter**: Requires URL changes, less flexible
- **Cookie-based**: Less secure, harder to manage

## Unique Constraint Strategy

**Decision**: Composite unique constraints including tenant_id (e.g., UNIQUE(tenant_id, name)).

**Rationale**:
- Allows same name/identifier across different tenants
- Maintains data integrity within each tenant
- Standard pattern for multi-tenant applications
- Database-level enforcement

**Implementation**:
- Update all unique constraints in tenant-specific models
- Migration adds composite unique indexes
- Application-level validation in model `clean()` methods
- Examples: `UNIQUE(tenant_id, checksum)`, `UNIQUE(tenant_id, name, owner)`

**Alternatives Considered**:
- **Global uniqueness**: Too restrictive, prevents tenant independence
- **Application-only validation**: Less reliable, database constraints are safer

## Celery Task Tenant Scoping

**Decision**: Explicit tenant_id parameter passed to all Celery tasks.

**Rationale**:
- Celery tasks run in separate processes, thread-local context doesn't work
- Explicit parameter ensures tenant context is clear
- Prevents accidental cross-tenant processing
- Makes task execution traceable

**Implementation**:
- All tenant-specific tasks accept `tenant_id` parameter
- Task sets tenant context at start using `set_current_tenant()`
- Tenant context cleared after task completion
- Tasks fail if tenant_id not provided

**Alternatives Considered**:
- **Thread-local in tasks**: Doesn't work across process boundaries
- **Task metadata**: Less explicit, harder to debug
- **Database lookup**: Adds overhead, explicit parameter is clearer

## Tenant Selection UI Flow

**Decision**: Tenant selector shown after login if user has multiple tenants, auto-assign if single tenant.

**Rationale**:
- Reduces friction for single-tenant users
- Clear selection interface for multi-tenant users
- Can switch tenants during session
- Follows common multi-tenant application patterns

**Implementation**:
- Check user's tenant associations after login
- If multiple tenants: Show tenant selector component
- If single tenant: Automatically set tenant context
- Allow tenant switching via user menu during session

**Alternatives Considered**:
- **Always show selector**: Unnecessary for single-tenant users
- **Require selection on every request**: Too cumbersome
- **URL-based tenant switching**: Less user-friendly

## Super Admin Tenant Management UI

**Decision**: Dedicated tenant management screen with standard CRUD operations.

**Rationale**:
- Clear separation of admin functionality
- Standard CRUD pattern is familiar
- Can reuse existing management list components
- Accessible only to super admin users

**Implementation**:
- New route `/settings/tenants` (or similar)
- Tenant management component with list view
- Create/edit tenant dialog/modal
- Activate/deactivate toggle
- Soft delete with confirmation

**Alternatives Considered**:
- **Django admin integration**: Less integrated with frontend UI
- **Inline editing**: Less clear for complex operations
- **Separate admin application**: Overkill for this feature

## Data Migration Strategy

**Decision**: Fresh installation only - no migration paths for existing data.

**Rationale**:
- User requirement explicitly states fresh installation
- Simplifies implementation (no complex migration logic)
- Reduces risk of data corruption
- Cleaner database schema from start

**Implementation**:
- All models created with tenant_id from initial migration
- No data migration scripts needed
- System starts with empty database
- First tenant created during initial setup

**Alternatives Considered**:
- **Migration from single-tenant**: Complex, error-prone, not required per user
- **Dual-mode operation**: Adds complexity, not needed for fresh install

## API Versioning Strategy

**Decision**: New API version 10 for multi-tenancy features, versions 1-9 remain unchanged.

**Rationale**:
- Per Constitution Principle I: Breaking changes require new API version
- Maintains backward compatibility for existing clients
- Single-tenant deployments can continue using versions 1-9
- Multi-tenant deployments use version 10

**Implementation**:
- Add version 10 to `ALLOWED_VERSIONS` in settings
- Version 10 requires X-Tenant-ID header
- Version 10 returns tenant-scoped data
- Versions 1-9 maintain single-tenant behavior (no tenant filtering)

**Alternatives Considered**:
- **Modify existing versions**: Would break backward compatibility
- **Feature flags**: More complex, versioning is cleaner
- **Separate API**: Unnecessary, versioning handles it

## Summary

All technology decisions leverage existing infrastructure where possible:
- TenantModel base class already exists
- TenantManager and thread-local context already implemented
- Django's is_superuser for admin access
- Standard Django/DRF patterns throughout

New components required:
- Frontend tenant selection UI
- Frontend tenant management screen
- Tenant API endpoints for super admin
- HTTP interceptor for X-Tenant-ID header
- Celery task tenant_id parameter updates

No major technology gaps identified. Implementation builds upon existing multi-tenancy infrastructure.

