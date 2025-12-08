# Data Model: Multi-Tenancy Entities

**Feature**: Multi-Tenancy Support
**Date**: 2025-01-27
**Status**: Current Implementation

## Entity Relationship Overview

```
Tenant (organizational unit)
    │
    ├─── UserProfile (user-tenant association)
    │       └─── User (Django User model)
    │
    └─── All Tenant-Specific Models (via TenantModel)
            ├─── Document
            ├─── Tag
            ├─── Correspondent
            ├─── DocumentType
            ├─── StoragePath
            ├─── CustomField
            ├─── CustomFieldInstance
            ├─── SavedView
            ├─── ShareLink
            ├─── Note
            └─── Workflow (if tenant-scoped)
```

## Core Entities

### Tenant

**Purpose**: Represents an organizational unit that owns and isolates data. Each tenant operates independently with complete data separation.

**Key Attributes**:
- `id`: Primary key
- `name`: Human-readable tenant name (max 255 chars)
- `identifier`: URL-safe identifier, unique globally (max 255 chars, lowercase alphanumeric, hyphens, underscores only)
- `is_active`: Boolean, whether tenant is active (default: True)
- `deleted_at`: Soft delete timestamp (nullable)
- `created_at`: Creation timestamp (auto)
- `updated_at`: Last update timestamp (auto)

**Relationships**:
- One-to-many: UserProfile (via user.tenant)
- One-to-many: All tenant-specific models (Document, Tag, Correspondent, etc.)

**Validation Rules**:
- Name cannot be empty
- Identifier must be unique across all tenants
- Identifier must match pattern: `^[a-z0-9_-]+$` (lowercase letters, numbers, hyphens, underscores)
- Identifier validation enforced at database and application level

**State Transitions**:
- Active → Inactive: Set `is_active=False` (via deactivate action)
- Inactive → Active: Set `is_active=True` (via activate action)
- Active/Inactive → Soft Deleted: Set `deleted_at=now()`, `is_active=False` (via delete action)
- Soft Deleted → Hard Deleted: Permanently remove (via hard_delete method, after retention period)

**Operations**:
- Create: Super admin creates new tenant with name and identifier
- Read: Super admin views all tenants, users view their associated tenant(s)
- Update: Super admin updates tenant name and identifier
- Delete: Super admin soft-deletes tenant (marks as deleted, retains data)

### UserProfile

**Purpose**: Extends Django User model to associate users with tenants. Each user belongs to at least one tenant.

**Key Attributes**:
- `id`: Primary key
- `user`: OneToOne relationship with Django User (required)
- `tenant`: ForeignKey to Tenant (nullable, but typically required)

**Relationships**:
- Belongs to: User (OneToOne)
- Belongs to: Tenant (ForeignKey)

**Validation Rules**:
- Each user has exactly one UserProfile
- User must be associated with at least one tenant (enforced at application level)
- Tenant must be active and not deleted for user to access system

**Note**: Future enhancement may support multiple tenant associations per user (many-to-many relationship), but current implementation uses single tenant per user.

### TenantContext (Thread-Local)

**Purpose**: Maintains tenant context for current request/operation. Not a database entity - runtime context only.

**Implementation**:
- Uses `threading.local()` for thread-local storage
- Set by `TenantMiddleware` at request start
- Set by Celery tasks from explicit `tenant_id` parameter
- Cleared after request/task completion

**Functions**:
- `set_current_tenant(tenant)`: Set tenant for current thread
- `get_current_tenant()`: Get current tenant (returns None if not set)
- `clear_current_tenant()`: Clear tenant context

**Lifecycle**:
- Set: Middleware sets from X-Tenant-ID header or user's tenant
- Used: TenantManager filters queries by current tenant
- Cleared: After request completion or task completion

### TenantModel (Abstract Base Class)

**Purpose**: Abstract base class for all tenant-specific models. Provides automatic tenant filtering and assignment.

**Key Attributes**:
- `tenant`: ForeignKey to Tenant (required, indexed)

**Behavior**:
- All queries automatically filtered by current tenant (via TenantManager)
- Tenant auto-assigned from context on save if not explicitly set
- Raises error if tenant context not set and tenant not provided
- Provides `for_tenant(tenant)` method for explicit tenant filtering (super admin use)

**Used By** (existing models):
- Document
- Tag
- Correspondent
- DocumentType
- StoragePath
- CustomField
- CustomFieldInstance
- SavedView
- ShareLink
- Note

**Future Models** (if tenant-scoped):
- Workflow (may be global or tenant-scoped)
- MailAccount (if tenant-scoped)
- MailRule (if tenant-scoped)

## Data Isolation Rules

### Query Filtering

**Automatic Filtering**:
- All `TenantModel` queries automatically filtered by `get_current_tenant()`
- Applied via `TenantManager.get_queryset()`
- Prevents accidental cross-tenant data access
- Fails safely if tenant context not set

**Explicit Filtering** (Super Admin):
- `Model.objects.for_tenant(tenant)` for cross-tenant access
- Only available to super admin users
- Used for tenant management operations

### Unique Constraints

**Pattern**: All unique constraints include tenant_id

**Examples**:
- Document: `UNIQUE(tenant_id, checksum)` instead of `UNIQUE(checksum)`
- Tag: `UNIQUE(tenant_id, name, owner)` instead of `UNIQUE(name, owner)`
- Correspondent: `UNIQUE(tenant_id, name, owner)` instead of `UNIQUE(name, owner)`
- DocumentType: `UNIQUE(tenant_id, name, owner)` instead of `UNIQUE(name, owner)`
- StoragePath: `UNIQUE(tenant_id, name, owner)` instead of `UNIQUE(name, owner)`
- CustomField: `UNIQUE(tenant_id, name)` instead of `UNIQUE(name)`

**Rationale**: Allows same name/identifier across different tenants while maintaining uniqueness within each tenant.

### Foreign Key Consistency

**Rule**: If Model A has ForeignKey to Model B, and both are tenant-specific:
- Model A.tenant MUST equal Model B.tenant
- Enforced at application level in model `clean()` methods
- Database constraints where supported

**Examples**:
- Document.correspondent: Document.tenant must equal Correspondent.tenant
- Document.tags: All tags in ManyToMany must have same tenant as document
- Document.document_type: Document.tenant must equal DocumentType.tenant
- Note.document: Note.tenant must equal Document.tenant
- CustomFieldInstance.field: CustomFieldInstance.tenant must equal CustomField.tenant

### Many-to-Many Relationships

**Rule**: All objects in ManyToMany relationships must belong to same tenant

**Examples**:
- Document.tags: All tags must have same tenant as document
- Workflow.triggers: All triggers must have same tenant as workflow (if tenant-scoped)
- Workflow.actions: All actions must have same tenant as workflow (if tenant-scoped)

**Enforcement**: Application-level validation in model `clean()` methods and serializer validation.

## Database Indexes

### Composite Indexes

All tenant-specific models require composite indexes for performance:

**Pattern**: `(tenant_id, commonly_queried_field)`

**Common Indexes**:
- `(tenant_id, created)` - For date-based queries
- `(tenant_id, modified)` - For recent items
- `(tenant_id, name)` - For name lookups
- `(tenant_id, checksum)` - For uniqueness checks
- `(tenant_id, owner_id)` - For owner-based queries

**Migration Strategy**:
- Indexes created in initial migrations (fresh installation)
- Use `CREATE INDEX CONCURRENTLY` for production (PostgreSQL)
- Monitor query performance and add indexes as needed

## Super Admin Access Model

**Super Admin Role**: Django's `is_superuser` flag

**Access Patterns**:
- Super admin can access tenant management endpoints
- Super admin can view/manage all tenants (not restricted to their tenant)
- Super admin can use `for_tenant()` method for cross-tenant queries
- Regular users restricted to their associated tenant(s)

**Tenant Management Operations**:
- List all tenants (including inactive and soft-deleted)
- Create new tenants
- Update tenant details
- Activate/deactivate tenants
- Soft delete tenants
- View tenant statistics (if implemented)

## User-Tenant Association

**Current Implementation**: One tenant per user (via UserProfile.tenant)

**Future Enhancement**: Support multiple tenant associations per user

**Current Behavior**:
- User has one UserProfile with one tenant
- User automatically assigned to their tenant on login
- No tenant selection needed if user has single tenant

**Future Behavior** (if implemented):
- UserProfile replaced with UserTenantAssociation (many-to-many)
- User can belong to multiple tenants
- User selects tenant on login or switches during session
- All operations scoped to selected tenant

## Celery Task Tenant Scoping

**Pattern**: Explicit tenant_id parameter

**Implementation**:
- All tenant-specific Celery tasks accept `tenant_id` parameter
- Task sets tenant context at start: `set_current_tenant(tenant)`
- Task processes data using tenant context
- Task clears tenant context at completion: `clear_current_tenant()`

**Examples**:
- `consume_file(tenant_id, input_doc, ...)`: Document consumption task
- `train_classifier(tenant_id, ...)`: Classifier training task
- `process_mail_accounts(tenant_id, account_ids, ...)`: Email processing task

**Rationale**: Celery tasks run in separate processes, thread-local context doesn't work across process boundaries.

## Frontend Tenant Context

**Implementation**: Angular service with HTTP interceptor

**Components**:
- `TenantContextService`: Manages current tenant selection
- `TenantInterceptor`: Adds X-Tenant-ID header to all HTTP requests
- Session storage: Persists tenant selection across page reloads

**State Management**:
- Current tenant stored in service
- Tenant selection persisted in sessionStorage
- Tenant change emits event for UI updates
- All HTTP requests include X-Tenant-ID header

## Data Integrity Summary

**Isolation Mechanisms**:
1. Database-level: Composite unique constraints with tenant_id
2. Application-level: TenantManager automatic query filtering
3. Validation-level: Model clean() methods enforce tenant consistency
4. Middleware-level: Tenant context set and verified per request
5. Task-level: Explicit tenant_id parameter for background tasks

**Security Guarantees**:
- Zero cross-tenant data access via automatic filtering
- Tenant context required for all tenant-specific operations
- Super admin access properly restricted and auditable
- Foreign key relationships maintain tenant consistency

