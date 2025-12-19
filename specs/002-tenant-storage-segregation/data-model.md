# Data Model: Tenant-Level Storage Segregation

**Feature**: Tenant-Level Storage Segregation
**Date**: 2025-01-27
**Status**: Design Phase

## Entity Relationship Overview

```
Tenant (existing)
    │
    └─── Tenant Storage Path (logical concept)
            ├─── Documents (originals)
            ├─── Archives
            └─── Thumbnails
```

## Core Entities

### Tenant Storage Path

**Purpose**: Represents the tenant-prefixed storage path structure that ensures tenant isolation at the storage layer.

**Key Attributes**:
- `tenant_identifier`: The tenant's unique identifier (from Tenant model)
- `logical_path`: The original logical path (e.g., "documents/originals/{filename}")
- `tenant_storage_path`: The complete tenant-prefixed path (e.g., "{tenant_identifier}/documents/originals/{filename}")

**Path Patterns**:
- **Original Documents**: `{tenant_identifier}/documents/originals/{filename}`
- **Archive Files**: `{tenant_identifier}/documents/archive/{filename}`
- **Thumbnails**: `{tenant_identifier}/documents/thumbnails/{filename}`

**Behavior**:
- Automatically constructed by storage backend `get_path()` method
- Tenant identifier derived from current tenant context via `get_current_tenant()`
- Logical path remains unchanged in database (backward compatibility)
- Tenant prefix added at storage layer during path resolution

**Validation Rules**:
- Tenant identifier must be available (from tenant context)
- Tenant identifier must be URL-safe (already validated at Tenant model level)
- Logical path must not contain directory traversal sequences ("..", "//")
- Tenant identifier cannot be empty or None

**Storage Backend Integration**:
- Filesystem: Resolves to `{ORIGINALS_DIR}/{tenant_identifier}/documents/originals/{filename}`
- Azure Blob: Resolves to blob name `{tenant_identifier}/documents/originals/{filename}`

### Tenant (Existing Entity - Referenced)

**Purpose**: Represents an organizational unit that owns and isolates data.

**Key Attributes** (relevant to storage):
- `id`: Primary key
- `identifier`: URL-safe identifier used in storage paths (e.g., "acme-corp", "contoso-ltd")
- `is_active`: Whether tenant is active
- `deleted_at`: Soft delete timestamp

**Storage Path Usage**:
- `identifier` field is used as the tenant prefix in storage paths
- Must be URL-safe (lowercase alphanumeric, hyphens, underscores only)
- Validated at model level with regex pattern: `^[a-z0-9_-]+$`

## Storage Backend Modifications

### StorageBackend (Abstract Base Class)

**Modified Methods**:
- `get_path(logical_path: str) -> str`: Now prepends tenant identifier to logical path
  - Retrieves tenant from context via `get_current_tenant()`
  - Validates tenant identifier is available
  - Constructs tenant-prefixed path: `{tenant_identifier}/{logical_path}`
  - Returns storage-specific path (filesystem absolute path or Azure blob name)

**New Behavior**:
- All storage operations (store, retrieve, delete, exists) automatically use tenant-prefixed paths
- Tenant context must be set before storage operations
- Raises `ValueError` if tenant context is unavailable

### FilesystemStorageBackend

**Modified Methods**:
- `get_path(logical_path: str) -> str`:
  - Adds tenant identifier prefix before resolving to filesystem path
  - Returns: `{ORIGINALS_DIR}/{tenant_identifier}/documents/originals/{filename}` (for originals)
  - Similar pattern for archives and thumbnails

**Directory Structure**:
```
{ORIGINALS_DIR}/
  ├── {tenant_identifier_1}/
  │   └── documents/
  │       ├── originals/
  │       ├── archive/
  │       └── thumbnails/
  └── {tenant_identifier_2}/
      └── documents/
          ├── originals/
          ├── archive/
          └── thumbnails/
```

### AzureBlobStorageBackend

**Modified Methods**:
- `get_path(logical_path: str) -> str`:
  - Adds tenant identifier prefix to blob name
  - Returns: `{tenant_identifier}/documents/originals/{filename}` (blob name)

**Blob Organization**:
- All blobs prefixed with tenant identifier
- Same container used for all tenants
- Tenant isolation via blob name prefix

## Data Flow

### Document Storage Flow

1. **Application Layer**: Document model generates logical path (e.g., `documents/originals/0000123.pdf`)
2. **Storage Backend**: `get_path()` called with logical path
3. **Tenant Context**: `get_current_tenant()` retrieves current tenant
4. **Path Construction**: Tenant identifier prepended: `{tenant_identifier}/documents/originals/0000123.pdf`
5. **Storage Resolution**: Backend resolves to storage-specific path (filesystem absolute path or Azure blob name)
6. **Storage Operation**: File stored at tenant-isolated path

### Document Retrieval Flow

1. **Application Layer**: Document model provides logical path
2. **Storage Backend**: `get_path()` called with logical path
3. **Tenant Context**: Current tenant retrieved
4. **Path Construction**: Tenant-prefixed path constructed
5. **Storage Resolution**: Backend resolves to storage-specific path
6. **Retrieval**: File retrieved from tenant-isolated path

## State Transitions

### Tenant Context Availability

**Normal Operation**:
- Tenant context set by middleware → Storage operations succeed
- Tenant context available → Paths include tenant prefix

**Error States**:
- Tenant context not set → `ValueError` raised
- Tenant identifier invalid → `ValueError` raised
- Path traversal detected → `ValueError` raised

## Validation Rules

### Path Validation

1. **Tenant Identifier Validation**:
   - Must not be None or empty
   - Must match URL-safe pattern (already validated at Tenant model)
   - Must not contain path separators

2. **Logical Path Validation**:
   - Must not contain ".." (directory traversal)
   - Must not contain "//" (path manipulation)
   - Must start with valid prefix ("documents/originals/", "documents/archive/", "documents/thumbnails/")

3. **Tenant Storage Path Construction**:
   - Format: `{tenant_identifier}/{logical_path}`
   - Tenant identifier and logical path joined with single "/"
   - No double slashes or trailing slashes (except for directory paths)

## Security Considerations

### Tenant Isolation Enforcement

- **Path-level isolation**: Each tenant's files stored under unique prefix
- **Context validation**: Tenant context required for all storage operations
- **Path traversal prevention**: Validation prevents ".." and "//" in paths
- **Tenant identifier validation**: URL-safe pattern prevents injection attacks

### Access Control

- **Normal users**: Can only access files under their tenant's prefix
- **Super admin**: Can access files across tenants by explicitly setting tenant context
- **Storage operations**: All operations respect tenant boundaries

## Migration Considerations

### Existing Data

- **Logical paths in database**: Remain unchanged (backward compatible)
- **Existing files**: May need migration to tenant-prefixed paths (handled separately)
- **Storage structure**: New files automatically use tenant-prefixed paths

### Backward Compatibility

- **Database schema**: No changes required
- **Logical paths**: Continue to work with tenant-aware storage layer
- **API contracts**: No changes (internal implementation detail)

