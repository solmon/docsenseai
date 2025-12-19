# Research: Multiple Storage Backends

**Feature**: Multiple Storage Backends
**Date**: 2025-01-27
**Phase**: 0 - Research & Technology Decisions

## Research Questions

### 1. Azure Blob Storage Python SDK Selection

**Question**: Which Azure Blob Storage Python library should be used, and what are the best practices for integration?

**Research Findings**:

- **Decision**: Use `azure-storage-blob` (official Azure SDK for Python, part of `azure-storage-blob` package)
- **Rationale**:
  - Official Microsoft-maintained library with active development
  - Comprehensive feature set (blob operations, container management, authentication)
  - Well-documented with examples
  - Supports connection strings and managed identity authentication
  - Compatible with Python 3.10+ (matches Paperless-ngx requirements)
  - Widely used in Python ecosystem
- **Alternatives Considered**:
  - `azure-storage-blob` (chosen) - Official SDK, most comprehensive
  - `azure-storage` (legacy) - Deprecated, replaced by azure-storage-blob
  - Direct REST API calls - Too low-level, requires manual authentication handling
- **Best Practices**:
  - Use `BlobServiceClient` for service-level operations
  - Use `ContainerClient` for container-level operations
  - Use `BlobClient` for individual blob operations
  - Connection strings should be stored in environment variables (not in code)
  - Support managed identity for Azure-hosted deployments (future enhancement)
  - Handle `BlobNotFoundError` for existence checks
  - Use streaming uploads/downloads for large files
  - Implement retry logic for transient failures (Azure SDK includes retry policies)

**References**:
- Azure SDK for Python: https://github.com/Azure/azure-sdk-for-python
- azure-storage-blob documentation: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/

---

### 2. Abstract Storage Interface Design Pattern

**Question**: How should the abstract storage interface be designed to support multiple backends while maintaining clean separation of concerns?

**Research Findings**:

- **Decision**: Use Abstract Base Class (ABC) pattern with Protocol for type checking
- **Rationale**:
  - Python's `abc.ABC` provides clear interface contracts
  - `typing.Protocol` enables structural typing for better type checking
  - Follows Python best practices for interface design
  - Easy to mock for testing
  - Clear method signatures for implementers
- **Interface Methods Required**:
  - `store(path: str, file_obj: BinaryIO) -> None` - Store file at path
  - `retrieve(path: str) -> BinaryIO` - Retrieve file as file-like object
  - `delete(path: str) -> None` - Delete file at path
  - `exists(path: str) -> bool` - Check if file exists
  - `get_path(logical_path: str) -> str` - Resolve logical path to storage-specific path
  - `initialize() -> None` - Initialize storage backend (create containers/directories if needed)
- **Alternatives Considered**:
  - ABC pattern (chosen) - Clear, Pythonic, type-checkable
  - Duck typing only - Less explicit, harder to document
  - Plugin system - Over-engineered for this use case
- **Best Practices**:
  - All methods should raise appropriate exceptions (FileNotFoundError, PermissionError, etc.)
  - Use context managers for file operations where possible
  - Return file-like objects (BytesIO, file handles) for consistency
  - Log all storage operations with backend type for debugging
  - Handle path normalization (forward slashes, path separators)

**References**:
- Python ABC documentation: https://docs.python.org/3/library/abc.html
- typing.Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol

---

### 3. File Path Handling Strategy

**Question**: How should file paths be stored in the database to work with both filesystem and cloud storage backends?

**Research Findings**:

- **Decision**: Store logical paths (relative paths) in database, let storage backend resolve to actual storage paths
- **Rationale**:
  - Database stores logical paths like `documents/originals/0000123.pdf` (relative, backend-agnostic)
  - Filesystem backend resolves to `MEDIA_ROOT/documents/originals/0000123.pdf`
  - Azure backend resolves to blob name `documents/originals/0000123.pdf` in container
  - Maintains database schema compatibility (no migration needed)
  - Storage backend abstraction handles path resolution
- **Path Structure**:
  - Originals: `documents/originals/{filename}`
  - Archives: `documents/archive/{filename}`
  - Thumbnails: `documents/thumbnails/{filename}`
  - Use forward slashes as path separator (works for both filesystem and cloud)
- **Alternatives Considered**:
  - Logical paths (chosen) - Backend-agnostic, no schema changes
  - Absolute paths - Would require different formats per backend, breaks abstraction
  - Storage backend ID + path - Over-engineered, adds unnecessary complexity
- **Best Practices**:
  - Normalize paths to use forward slashes
  - Validate path components to prevent directory traversal
  - Use `pathlib.Path` for filesystem operations, convert to string for cloud storage
  - Store paths relative to storage root (not absolute)

**References**:
- Django FileField path handling: https://docs.djangoproject.com/en/5.2/ref/models/fields/#filefield
- Azure Blob Storage naming: https://learn.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata

---

### 4. Error Handling and Resilience Patterns

**Question**: How should storage backend errors be handled, and what resilience patterns should be implemented?

**Research Findings**:

- **Decision**: Raise standard Python exceptions, implement retry logic for transient failures, log all errors with context
- **Rationale**:
  - Use standard exceptions (FileNotFoundError, PermissionError, OSError) for consistency
  - Azure SDK provides retry policies for transient failures
  - Filesystem operations may need retry for concurrent access
  - Clear error messages help diagnose issues
- **Exception Mapping**:
  - `FileNotFoundError` - File doesn't exist (retrieve, delete operations)
  - `PermissionError` - Access denied
  - `OSError` - General I/O errors
  - `ConnectionError` - Network failures (Azure)
  - `TimeoutError` - Operation timeout
  - Custom `StorageBackendError` for backend-specific errors
- **Retry Strategy**:
  - Azure SDK: Use built-in retry policies (exponential backoff)
  - Filesystem: Retry for concurrent access (existing pattern in consumer)
  - Configuration: Retry count and timeout configurable via settings
- **Alternatives Considered**:
  - Standard exceptions (chosen) - Pythonic, familiar to developers
  - Custom exception hierarchy - Unnecessary complexity
  - Silent failures - Dangerous, makes debugging difficult
- **Best Practices**:
  - Log all storage operations with backend type, operation, and path
  - Include error context in log messages
  - Fail fast on configuration errors (startup validation)
  - Handle transient failures gracefully with retries
  - Provide clear error messages to users/administrators

**References**:
- Azure SDK retry policies: https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.pipeline.policies.retrypolicy
- Python exception hierarchy: https://docs.python.org/3/library/exceptions.html

---

### 5. Configuration Validation Patterns

**Question**: How should storage backend configuration be validated at application startup?

**Research Findings**:

- **Decision**: Validate configuration in Django settings/apps.py startup, fail fast with clear error messages
- **Rationale**:
  - Catch configuration errors before application starts processing requests
  - Clear error messages help administrators fix configuration quickly
  - Follows Django pattern of settings validation
  - Per SC-007: Configuration errors reported within 5 seconds of startup
- **Validation Steps**:
  1. Validate `PAPERLESS_STORAGE_BACKEND` is valid value ('filesystem' or 'azure_blob')
  2. If Azure backend: Validate `PAPERLESS_AZURE_CONNECTION_STRING` is present and valid format
  3. If Azure backend: Validate `PAPERLESS_AZURE_CONTAINER_NAME` is present
  4. Test connection to storage backend (optional, can be lazy)
  5. Verify container/directory exists or can be created
- **Error Messages**:
  - "Invalid storage backend '{value}'. Must be 'filesystem' or 'azure_blob'."
  - "Azure Blob Storage backend requires PAPERLESS_AZURE_CONNECTION_STRING environment variable."
  - "Azure Blob Storage backend requires PAPERLESS_AZURE_CONTAINER_NAME environment variable."
  - "Failed to connect to Azure Blob Storage: {error details}"
- **Alternatives Considered**:
  - Startup validation (chosen) - Fail fast, clear errors
  - Lazy validation - Errors discovered during first operation, harder to debug
  - Runtime validation only - Poor user experience, errors occur during operations
- **Best Practices**:
  - Validate all required environment variables at startup
  - Test connectivity if possible (with timeout)
  - Provide actionable error messages
  - Log configuration (without sensitive data like connection strings)

**References**:
- Django AppConfig.ready(): https://docs.djangoproject.com/en/5.2/ref/applications/#django.apps.AppConfig.ready
- Django settings validation: https://docs.djangoproject.com/en/5.2/topics/settings/#custom-default-settings

---

### 6. Storage Backend Factory/Registry Pattern

**Question**: How should storage backends be instantiated and registered?

**Research Findings**:

- **Decision**: Use factory pattern with registry, instantiate backend in Django settings based on configuration
- **Rationale**:
  - Single source of truth for backend selection (settings)
  - Easy to add new backends (register in factory)
  - Lazy initialization possible if needed
  - Clear separation between configuration and implementation
- **Factory Implementation**:
  - `StorageBackendFactory.get_backend(backend_type: str) -> StorageBackend`
  - Registry pattern: `{backend_type: backend_class}`
  - Backend classes register themselves or are registered explicitly
- **Initialization**:
  - Create backend instance in Django settings or app ready()
  - Store instance in settings or module-level variable
  - Access via `get_storage_backend()` function
- **Alternatives Considered**:
  - Factory pattern (chosen) - Clean, extensible, follows design patterns
  - Direct instantiation - Less flexible, harder to extend
  - Plugin system - Over-engineered for current needs
- **Best Practices**:
  - Register backends explicitly (not auto-discovery) for clarity
  - Validate backend type before instantiation
  - Cache backend instance (singleton pattern)
  - Support lazy initialization for optional dependencies

**References**:
- Factory pattern: https://refactoring.guru/design-patterns/factory-method
- Python singleton pattern: https://python-patterns.guide/gang-of-four/singleton/

---

## Technology Decisions Summary

| Decision | Choice | Rationale |
|---------|--------|-----------|
| Azure SDK | `azure-storage-blob` | Official, well-maintained, comprehensive |
| Interface Pattern | ABC + Protocol | Pythonic, type-checkable, clear contracts |
| Path Storage | Logical paths in DB | Backend-agnostic, no schema changes |
| Error Handling | Standard exceptions + retries | Pythonic, Azure SDK retry policies |
| Configuration Validation | Startup validation | Fail fast, clear error messages |
| Backend Factory | Factory + Registry | Clean, extensible, follows patterns |

## Dependencies to Add

- `azure-storage-blob>=12.19.0` - Azure Blob Storage SDK (add to `pyproject.toml` dependencies)
- No other new dependencies required (uses existing pathlib, typing, abc)

## Implementation Notes

- All storage operations should be logged with backend type for debugging
- Storage backend should be thread-safe (Azure SDK is thread-safe)
- Consider connection pooling for Azure (SDK handles this automatically)
- Filesystem backend maintains existing behavior (backward compatibility)
- Path normalization ensures cross-platform compatibility

