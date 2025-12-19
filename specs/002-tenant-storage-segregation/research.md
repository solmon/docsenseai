# Research: Tenant-Level Storage Segregation Implementation Decisions

**Feature**: Tenant-Level Storage Segregation
**Date**: 2025-01-27
**Status**: Implementation Decisions

## Tenant Path Prefixing Strategy

**Decision**: Add tenant identifier as top-level prefix in all storage paths using format `{tenant_identifier}/{logical_path}`.

**Rationale**:
- Ensures complete tenant isolation at storage layer
- Works consistently across filesystem and cloud storage backends
- Tenant identifier is already validated to be URL-safe (lowercase alphanumeric, hyphens, underscores)
- Minimal performance impact (only adds path prefix)
- Maintains backward compatibility with existing logical paths in database

**Alternatives Considered**:
- **Separate storage backends per tenant**: Too complex, requires dynamic backend creation and configuration management
- **Tenant ID in filename**: Doesn't provide directory-level isolation, harder to manage and migrate
- **Separate containers/buckets per tenant**: Works for cloud storage but not filesystem, inconsistent approach

## Implementation Location

**Decision**: Implement tenant path prefixing in the abstract `StorageBackend` base class and all backend implementations.

**Rationale**:
- Centralizes tenant segregation logic in one place
- Ensures all storage backends automatically get tenant isolation
- Future storage backends will inherit tenant segregation automatically
- Consistent behavior across all backends

**Alternatives Considered**:
- **Wrapper/decorator pattern**: Adds complexity, requires wrapping all backend instances
- **Middleware layer**: Doesn't fit Django middleware pattern for storage operations
- **Application-level path manipulation**: Would require changes in many places, error-prone

## Tenant Context Integration

**Decision**: Use existing `paperless.tenants.utils.get_current_tenant()` to retrieve tenant identifier during storage operations.

**Rationale**:
- Leverages existing tenant context infrastructure
- Thread-local storage ensures tenant context is isolated per request
- No additional infrastructure needed
- Consistent with existing multi-tenancy implementation

**Alternatives Considered**:
- **Pass tenant explicitly to storage methods**: Would require changing all storage method signatures, breaking abstraction
- **Store tenant in storage backend instance**: Not thread-safe, would cause cross-tenant contamination
- **New tenant context system**: Unnecessary, existing system works well

## Path Resolution Strategy

**Decision**: Modify `get_path()` method in all storage backends to prepend tenant identifier to logical paths before resolving to storage-specific paths.

**Rationale**:
- Single point of modification for path resolution
- All storage operations (store, retrieve, delete, exists) use `get_path()`, so they automatically get tenant segregation
- Maintains existing logical path format in database
- Clear separation of concerns: database stores logical paths, storage layer adds tenant context

**Alternatives Considered**:
- **Modify logical paths in database**: Would require migration, breaks backward compatibility
- **Add tenant prefix in each storage method**: Duplicates logic, error-prone
- **Separate tenant-aware path resolver**: Adds unnecessary abstraction layer

## Error Handling for Missing Tenant Context

**Decision**: Raise `ValueError` with clear error message when tenant context is unavailable during storage operations.

**Rationale**:
- Fails safely - prevents accidental cross-tenant access
- Clear error message helps diagnose configuration issues
- Consistent with existing error handling patterns
- Forces proper tenant context setup

**Alternatives Considered**:
- **Silently use default tenant**: Security risk, could cause data leakage
- **Use system/default tenant**: Not appropriate for multi-tenant system
- **Log warning and continue**: Security risk, could cause data corruption

## Filesystem Backend Implementation

**Decision**: For filesystem backend, create tenant directories under existing ORIGINALS_DIR, ARCHIVE_DIR, THUMBNAIL_DIR (e.g., `{ORIGINALS_DIR}/{tenant_identifier}/documents/originals/`).

**Rationale**:
- Maintains existing directory structure under tenant isolation
- Works with existing Django settings
- Easy to understand and manage
- Supports per-tenant storage quotas if needed in future

**Alternatives Considered**:
- **Separate base directory per tenant**: Would require new settings, more complex configuration
- **Tenant directories at media root**: Less organized, harder to manage

## Azure Blob Storage Backend Implementation

**Decision**: For Azure backend, use tenant identifier as blob name prefix (e.g., `{tenant_identifier}/documents/originals/{filename}`).

**Rationale**:
- Azure blob names support path-like prefixes
- Consistent with filesystem approach
- No container changes needed
- Works with existing Azure container configuration

**Alternatives Considered**:
- **Separate containers per tenant**: Would require dynamic container creation, more complex
- **Tenant in blob metadata**: Doesn't provide path-level isolation, harder to manage

## Super Admin Cross-Tenant Access

**Decision**: Super admin users can access files across tenants by explicitly setting tenant context, but normal operations maintain tenant isolation.

**Rationale**:
- Maintains security for normal operations
- Allows administrative access when needed
- Uses existing tenant context switching mechanism
- No special storage backend logic needed

**Alternatives Considered**:
- **Special storage backend methods for super admin**: Adds complexity, not needed
- **Bypass tenant segregation for super admin**: Security risk, could cause accidental cross-tenant access

## Validation and Security

**Decision**: Validate tenant identifier before use in paths, ensure no directory traversal, reuse existing path validation logic.

**Rationale**:
- Tenant identifiers are already validated at model level (URL-safe pattern)
- Additional validation provides defense in depth
- Prevents path traversal attacks
- Consistent with existing security practices

**Alternatives Considered**:
- **No additional validation**: Security risk, relies only on model validation
- **Complex path sanitization**: Unnecessary, tenant identifiers are already safe

