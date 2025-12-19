# Storage Backend Implementation Guide

This guide explains how to implement a new storage backend for Paperless-ngx.

## Overview

The storage backend abstraction allows Paperless-ngx to use different storage systems (filesystem, Azure Blob Storage, S3, Google Cloud Storage, etc.) transparently. All storage backends implement the same interface, making it easy to switch between storage providers.

## Interface Requirements

All storage backends must implement the `StorageBackend` abstract base class, which defines the following methods:

### Required Methods

1. **`store(path: str, file_obj: BinaryIO) -> None`**
   - Store a file at the specified logical path
   - Create parent directories/containers as needed
   - Handle file-like objects (may not support seek)

2. **`retrieve(path: str) -> BinaryIO`**
   - Retrieve a file from the specified logical path
   - Return a BytesIO object or similar file-like object
   - File pointer should be at the beginning

3. **`delete(path: str) -> None`**
   - Delete a file at the specified logical path
   - Raise FileNotFoundError if file doesn't exist

4. **`exists(path: str) -> bool`**
   - Check if a file exists
   - Return False (not raise exception) if file doesn't exist

5. **`get_path(logical_path: str) -> str`**
   - Resolve logical path to storage-specific path with tenant prefix
   - Automatically adds tenant identifier prefix: `{tenant_identifier}/{logical_path}`
   - For filesystem: return absolute path with tenant directory
   - For cloud storage: return blob/object name with tenant prefix
   - Raises ValueError if tenant context is not available

6. **`_resolve_path(tenant_path: str) -> str`** (abstract method)
   - Resolve tenant-prefixed path to storage-specific path
   - Implemented by each backend for backend-specific path resolution
   - The tenant prefix is already included in the tenant_path parameter

7. **`initialize() -> None`**
   - Initialize storage backend (create containers/directories)
   - Called at application startup
   - Verify connectivity

## Implementation Steps

### 1. Create Backend Class

Create a new file `src/documents/storage/your_backend.py`:

```python
from documents.storage.base import StorageBackend

class YourStorageBackend(StorageBackend):
    def __init__(self):
        # Initialize your backend (connection, credentials, etc.)
        pass

    def _resolve_path(self, tenant_path: str) -> str:
        """
        Resolve tenant-prefixed path to storage-specific path.

        Args:
            tenant_path: Tenant-prefixed path (e.g., 'acme-corp/documents/originals/file.pdf')

        Returns:
            Storage-specific path (blob name, object key, etc.)
        """
        # The tenant_path already includes tenant identifier
        # Implement backend-specific path resolution here
        return tenant_path  # Example: use as-is for cloud storage

    def store(self, path: str, file_obj: BinaryIO) -> None:
        # Implementation
        # Note: path parameter is already tenant-prefixed by base class
        pass

    # ... implement other methods
```

### 2. Register Backend

In `src/documents/storage/factory.py`, register your backend:

```python
from documents.storage.your_backend import YourStorageBackend

register_backend("your_backend", YourStorageBackend)
```

### 3. Add Configuration

In `src/paperless/settings.py`, add configuration settings:

```python
PAPERLESS_YOUR_BACKEND_SETTING = os.getenv("PAPERLESS_YOUR_BACKEND_SETTING", "")
```

### 4. Update Configuration Validation

In `src/paperless/settings.py`, update `_validate_storage_backend_config()`:

```python
valid_backends = {"filesystem", "azure_blob", "your_backend"}

if backend == "your_backend":
    if not PAPERLESS_YOUR_BACKEND_SETTING:
        raise ValueError("Your backend requires PAPERLESS_YOUR_BACKEND_SETTING")
```

## Path Handling

### Logical Paths

Logical paths are relative paths stored in the database:
- Originals: `documents/originals/{filename}`
- Archives: `documents/archive/{filename}`
- Thumbnails: `documents/thumbnails/{filename}`

### Tenant-Level Segregation

All storage paths are automatically prefixed with the tenant identifier to ensure complete tenant isolation:
- Format: `{tenant_identifier}/{logical_path}`
- Example: `acme-corp/documents/originals/0000123.pdf`

The tenant identifier is derived from the current tenant context (set by middleware) and is automatically added by the `StorageBackend.get_path()` method. This ensures:
- Complete tenant isolation at the storage layer
- No cross-tenant data access possible
- Consistent behavior across all storage backends
- Thumbnails: `documents/thumbnails/{filename}`

### Storage-Specific Paths

The `get_path()` method converts logical paths to storage-specific paths:
- **Filesystem**: `{MEDIA_ROOT}/documents/originals/{filename}` (absolute path)
- **Azure Blob**: `documents/originals/{filename}` (blob name, same as logical path)
- **S3**: `documents/originals/{filename}` (object key, same as logical path)

## Error Handling

### Standard Exceptions

Use standard Python exceptions:
- `FileNotFoundError`: File doesn't exist
- `OSError`: General I/O errors
- `PermissionError`: Access denied
- `ConnectionError`: Network/connection failures

### Logging

Log all operations with backend type:

```python
logger.debug(f"Stored file in YourBackend: {path}")
logger.error(f"Failed to store file {path}: {e}")
```

## Thread Safety

All storage backend implementations must be thread-safe. Storage operations may be called concurrently from multiple threads.

## Testing

Create tests in `src/documents/tests/storage/test_your_backend.py`:

```python
def test_store_and_retrieve():
    backend = YourStorageBackend()
    backend.initialize()

    test_data = b"test content"
    backend.store("test/path.txt", BytesIO(test_data))

    retrieved = backend.retrieve("test/path.txt")
    assert retrieved.read() == test_data
```

## Examples

See existing implementations:
- `src/documents/storage/filesystem.py` - Filesystem backend
- `src/documents/storage/azure_blob.py` - Azure Blob Storage backend

## Best Practices

1. **Error Messages**: Provide clear, actionable error messages
2. **Logging**: Log all operations with sufficient detail for debugging
3. **Retry Logic**: Implement retry logic for transient failures (cloud storage)
4. **Streaming**: Use streaming for large files to avoid memory issues
5. **Connection Pooling**: Reuse connections where possible (cloud storage)
6. **Path Validation**: Validate paths to prevent directory traversal attacks

## Questions?

Refer to the abstract base class documentation in `src/documents/storage/base.py` for detailed method signatures and requirements.

