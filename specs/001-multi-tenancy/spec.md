# Feature Specification: Multi-Tenancy Support

**Feature Branch**: `001-multi-tenancy`
**Created**: 2025-01-27
**Status**: Draft
**Input**: User description: "Update the current software specification to incorporate multi-tenancy features and related UI changes, building upon the existing completed one. The requested enhancements are as follows:

Project Setup: The project is intended for a fresh installation. Ensure the technical plan and documentation reflect this, and remove all previous migration paths or plans related to an initial database setup.

User Interface (UI) Updates: Modify the UI codebase located in the src-ui folder to include functionality for tenant selection and to maintain tenant context throughout the application. This includes:

A mechanism for users to select their tenant upon login or during their session.

Ensuring all subsequent data access and operations are scoped to the selected tenant ID.

Super Admin Functionality: Introduce a new screen accessible only to a super admin user role for comprehensive tenant management. This screen must support standard CRUD (Create, Read, Update, Delete) operations, specifically allowing the super admin to view, add, activate, and deactivate different tenants.

Data Isolation: The underlying architecture must support logical data isolation using a tenant_id to separate data within a shared database, as this is a multi-tenant application.

Please generate the updated specification, a revised technical plan, and a breakdown of tasks to implement these changes."

## User Scenarios & Testing

### User Story 1 - Tenant Selection and Context Management (Priority: P1)

Users can select their tenant upon login or during their session, and all subsequent data access and operations are automatically scoped to the selected tenant.

**Why this priority**: This is the foundation for multi-tenancy - without tenant selection and context management, data isolation cannot function properly.

**Independent Test**: Log in as a user associated with a tenant, select the tenant, verify all API requests include the tenant context and all data returned is scoped to that tenant.

**Acceptance Scenarios**:

1. **Given** a user is authenticated and associated with a tenant, **When** they log in, **Then** they see a tenant selection interface if multiple tenants are available, or are automatically assigned to their single tenant
2. **Given** a user has selected a tenant, **When** they navigate through the application, **Then** all API requests include the tenant ID in the request header
3. **Given** a user has selected a tenant, **When** they perform any data operation (view, create, update, delete), **Then** all operations are automatically scoped to the selected tenant
4. **Given** a user switches tenants during their session, **When** they select a different tenant, **Then** the tenant context is updated and all subsequent operations use the new tenant
5. **Given** a user is associated with only one tenant, **When** they log in, **Then** they are automatically assigned to that tenant without showing selection UI

---

### User Story 2 - Super Admin Tenant Management (Priority: P1)

Super admin users can manage tenants through a dedicated screen, performing CRUD operations to view, create, update, activate, and deactivate tenants.

**Why this priority**: Super admin functionality is essential for system administration and must be available alongside tenant selection to enable complete multi-tenancy management.

**Independent Test**: Log in as a super admin, access the tenant management screen, create a new tenant, verify it appears in the list, activate/deactivate it, and verify the changes take effect.

**Acceptance Scenarios**:

1. **Given** a user has super admin role, **When** they access the tenant management screen, **Then** they see a list of all tenants with their status (active/inactive)
2. **Given** a super admin is on the tenant management screen, **When** they create a new tenant with name and identifier, **Then** the tenant is created and appears in the list
3. **Given** a super admin views a tenant, **When** they update tenant details (name, identifier), **Then** the changes are saved and reflected in the list
4. **Given** a super admin views an active tenant, **When** they deactivate it, **Then** the tenant status changes to inactive and users cannot access it
5. **Given** a super admin views an inactive tenant, **When** they activate it, **Then** the tenant status changes to active and users can access it
6. **Given** a super admin attempts to delete a tenant, **When** they confirm deletion, **Then** the tenant is soft-deleted (marked as deleted, not permanently removed)
7. **Given** a non-super-admin user attempts to access tenant management, **When** they navigate to the screen, **Then** access is denied with appropriate error message

---

### User Story 3 - Data Isolation and Tenant Scoping (Priority: P1)

All tenant-specific data operations are automatically scoped to the current tenant context, ensuring complete logical data isolation within a shared database.

**Why this priority**: Data isolation is the core requirement for multi-tenancy - without proper isolation, tenants could access each other's data, which is a critical security and privacy issue.

**Independent Test**: Create documents in Tenant A, switch to Tenant B, verify Tenant B cannot see Tenant A's documents, and verify all queries automatically filter by tenant ID.

**Acceptance Scenarios**:

1. **Given** a user is operating in Tenant A context, **When** they query documents, **Then** only documents belonging to Tenant A are returned
2. **Given** a user creates a document in Tenant A context, **When** the document is saved, **Then** it is automatically associated with Tenant A
3. **Given** a user in Tenant A context attempts to access a document ID from Tenant B, **When** they request the document, **Then** access is denied (404 or 403 error)
4. **Given** multiple tenants exist with similar data, **When** users from different tenants perform identical operations, **Then** each tenant's data remains completely isolated
5. **Given** a user creates metadata (tags, correspondents, document types) in Tenant A, **When** they switch to Tenant B, **Then** Tenant B's metadata is separate and Tenant A's metadata is not visible
6. **Given** bulk operations are performed in Tenant A context, **When** documents are selected and modified, **Then** only Tenant A's documents are affected

---

### Edge Cases

- What happens when a user's tenant is deactivated while they are logged in? User session is invalidated, they are logged out, and must contact administrator.
- How does system handle tenant selection when user belongs to multiple tenants? User sees tenant selector and can switch between their associated tenants.
- What happens when a super admin deactivates a tenant that has active users? Active user sessions are invalidated, users are logged out, and cannot access until tenant is reactivated.
- How are tenant identifiers validated for uniqueness? System enforces unique identifier constraint at database and application level.
- What happens when tenant context is lost during a request? Request fails with appropriate error, tenant context must be re-established.
- How are Celery background tasks scoped to tenants? Tasks receive tenant_id as parameter and set tenant context before processing.
- What happens when a user tries to access a soft-deleted tenant? Access is denied, tenant appears as deleted in super admin view.
- How are unique constraints handled across tenants? Unique constraints include tenant_id (e.g., UNIQUE(tenant_id, name) instead of UNIQUE(name)).

## Requirements

### Functional Requirements

- **FR-001**: System MUST support tenant selection for users upon login or during their session
- **FR-002**: System MUST maintain tenant context throughout user session and include tenant ID in all API requests
- **FR-003**: System MUST automatically scope all data queries to the current tenant context
- **FR-004**: System MUST provide a super admin role with exclusive access to tenant management functionality
- **FR-005**: System MUST support CRUD operations for tenants (create, read, update, delete) for super admin users
- **FR-006**: System MUST support tenant activation and deactivation without permanent deletion
- **FR-007**: System MUST enforce logical data isolation using tenant_id for all tenant-specific entities
- **FR-008**: System MUST prevent users from accessing data belonging to other tenants
- **FR-009**: System MUST associate each user with at least one tenant
- **FR-010**: System MUST support users belonging to multiple tenants with ability to switch between them
- **FR-011**: System MUST validate tenant identifier uniqueness across all tenants
- **FR-012**: System MUST validate that tenant identifier is URL-safe (alphanumeric, hyphens, underscores only)
- **FR-013**: System MUST automatically assign tenant context when user has only one associated tenant
- **FR-014**: System MUST invalidate user sessions when their tenant is deactivated
- **FR-015**: System MUST scope all tenant-specific models (Document, Tag, Correspondent, DocumentType, StoragePath, CustomField, etc.) to tenant_id
- **FR-016**: System MUST update unique constraints to include tenant_id for tenant-specific models
- **FR-017**: System MUST pass tenant_id explicitly to Celery background tasks
- **FR-018**: System MUST set tenant context in Celery tasks before processing tenant-specific data
- **FR-019**: System MUST provide tenant selection UI component in frontend
- **FR-020**: System MUST maintain tenant selection in frontend state and include in all API requests
- **FR-021**: System MUST provide tenant management screen accessible only to super admin users
- **FR-022**: System MUST display tenant list with status (active/inactive) in super admin screen
- **FR-023**: System MUST support soft deletion of tenants (mark as deleted, retain data for configurable period)
- **FR-024**: System MUST prevent creation of documents or other tenant-specific data when tenant context is not set
- **FR-025**: System MUST validate that foreign key relationships maintain tenant consistency (e.g., Document.tenant must equal Correspondent.tenant)

### Key Entities

- **Tenant**: Organizational unit that owns and isolates data. Attributes: id, name, identifier (unique, URL-safe), is_active (boolean), deleted_at (soft delete timestamp), created_at, updated_at. Relationships: one-to-many with User (via UserProfile), one-to-many with all tenant-specific models.

- **UserProfile**: Extension of Django User model to associate users with tenants. Attributes: user (OneToOne with User), tenant (ForeignKey to Tenant, nullable). Relationships: belongs to User and Tenant.

- **TenantContext**: Thread-local storage maintaining current tenant for request/operation. Set by middleware from X-Tenant-ID header or user's tenant association. Used by TenantManager to automatically filter queries.

- **TenantModel**: Abstract base class for all tenant-specific models. Attributes: tenant (ForeignKey to Tenant, required). Provides automatic tenant filtering via TenantManager and auto-assignment of tenant from context on save.

### Assumptions

- Fresh installation: No existing data migration required - system starts with empty database
- Shared database architecture: All tenants share the same database with logical separation via tenant_id
- Single tenant per user by default: Users typically belong to one tenant, but system supports multiple tenant associations
- Super admin role: A special user role exists that bypasses normal tenant restrictions for management operations
- Tenant identifier format: URL-safe identifiers using lowercase letters, numbers, hyphens, and underscores
- Soft deletion: Tenants are soft-deleted (marked as deleted) rather than permanently removed to allow data recovery
- Session-based tenant context: Tenant selection persists for the duration of user session
- Header-based tenant identification: Frontend includes X-Tenant-ID header in all API requests

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can select their tenant within 2 seconds of login when multiple tenants are available
- **SC-002**: All API requests include tenant context with 100% consistency (no requests missing tenant ID)
- **SC-003**: Data isolation is enforced with zero cross-tenant data leakage (verified through security testing)
- **SC-004**: Super admin can create a new tenant in under 30 seconds
- **SC-005**: Tenant activation/deactivation takes effect immediately (within 1 second) for all affected users
- **SC-006**: System supports at least 50 concurrent tenants with isolated operations
- **SC-007**: Query performance remains within 10% of single-tenant baseline (tenant filtering adds minimal overhead)
- **SC-008**: 100% of tenant-specific database queries automatically include tenant_id filter
- **SC-009**: Users successfully complete tenant selection on first attempt 95% of the time
- **SC-010**: Super admin can manage (view, create, update, activate/deactivate) tenants without errors

## API Considerations

- **API Version**: New API version 10 required due to breaking changes:
  - New required X-Tenant-ID header for authenticated requests
  - Tenant-scoped responses (all data filtered by tenant)
  - New tenant management endpoints for super admin
  - Modified unique constraint behavior (tenant-aware)

- **Backward Compatibility**:
  - Versions 1-9 remain unchanged and continue to work for single-tenant deployments
  - Version 10 introduces multi-tenancy features
  - Existing API clients using versions 1-9 will not receive tenant-scoped data (maintains single-tenant behavior)
  - New clients must use version 10 and include X-Tenant-ID header

- **Migration Notes**:
  - Fresh installations use version 10 by default
  - Existing single-tenant deployments can continue using versions 1-9
  - Multi-tenant deployments must use version 10
  - API clients must be updated to include X-Tenant-ID header when using version 10
  - Tenant management endpoints (`/api/tenants/`) are only available in version 10
