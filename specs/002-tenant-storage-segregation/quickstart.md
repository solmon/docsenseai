# Quickstart: Implementing Tenant-Level Storage Segregation

**Feature**: Tenant-Level Storage Segregation
**Date**: 2025-01-27

## Overview

This guide provides step-by-step instructions for implementing tenant-level storage segregation in the storage backend system. The implementation adds tenant identifier prefixes to all storage paths to ensure complete tenant isolation.

## Prerequisites

- Existing storage backend abstraction (feature 001-storage-backends)
- Multi-tenancy infrastructure (feature 001-multi-tenancy)
- Tenant context system (`paperless.tenants.utils.get_current_tenant()`)

## Implementation Steps

### Step 1: Modify StorageBackend Base Class

**File**: `src/documents/storage/base.py`

1. Import tenant utilities:
   ```python
   from paperless.tenants.utils import get_current_tenant
   ```

2. Modify `get_path()` method to add tenant prefix:
   ```python
   def get_path(self, logical_path: str) -> str:
       """
       Resolve a logical path to a storage-specific path with tenant prefix.

       Args:
           logical_path: Logical path (e.g., 'documents/originals/0000123.pdf')

       Returns:
           Storage-specific path with tenant prefix

       Raises:
           ValueError: If tenant context is not available
       """
       # Get current tenant
       tenant = get_current_tenant()
       if tenant is None:
           raise ValueError(
               "Tenant context not set. Cannot determine tenant for storage path."
           )

       # Validate tenant identifier
       if not tenant.identifier:
           raise ValueError(f"Tenant {tenant.id} has no identifier")

       # Validate logical path (prevent directory traversal)
       if ".." in logical_path or "//" in logical_path:
           raise ValueError(
               f"Invalid path: {logical_path} (directory traversal detected)"
           )

       # Construct tenant-prefixed path
       tenant_path = f"{tenant.identifier}/{logical_path}"

       # Call implementation-specific path resolution
       return self._resolve_path(tenant_path)

   @abstractmethod
   def _resolve_path(self, tenant_path: str) -> str:
       """
       Resolve tenant-prefixed path to storage-specific path.

       Subclasses implement this to handle backend-specific path resolution.
       """
       pass
   ```

### Step 2: Update FilesystemStorageBackend

**File**: `src/documents/storage/filesystem.py`

1. Implement `_resolve_path()` method:
   ```python
   def _resolve_path(self, tenant_path: str) -> str:
       """
       Resolve tenant-prefixed path to filesystem absolute path.

       Args:
           tenant_path: Tenant-prefixed path (e.g., 'acme-corp/documents/originals/0000123.pdf')

       Returns:
           Absolute filesystem path
       """
       # Extract tenant identifier and logical path
       parts = tenant_path.split("/", 1)
       if len(parts) != 2:
           # Fallback: assume originals directory
           return str((self.originals_dir / tenant_path).resolve())

       tenant_id, logical_path = parts

       # Determine directory based on logical path
       if logical_path.startswith("documents/originals/"):
           filename = logical_path.replace("documents/originals/", "")
           return str((self.originals_dir / tenant_id / "documents" / "originals" / filename).resolve())
       elif logical_path.startswith("documents/archive/"):
           filename = logical_path.replace("documents/archive/", "")
           return str((self.archive_dir / tenant_id / "documents" / "archive" / filename).resolve())
       elif logical_path.startswith("documents/thumbnails/"):
           filename = logical_path.replace("documents/thumbnails/", "")
           return str((self.thumbnail_dir / tenant_id / "documents" / "thumbnails" / filename).resolve())
       else:
           # Fallback: assume originals directory
           return str((self.originals_dir / tenant_id / logical_path).resolve())
   ```

2. Remove old `get_path()` implementation (replaced by base class)

3. Update `initialize()` to create tenant directories:
   ```python
   def initialize(self) -> None:
       """
       Initialize the storage backend.

       Creates base directories. Tenant-specific directories created on-demand.
       """
       try:
           self.originals_dir.mkdir(parents=True, exist_ok=True)
           self.archive_dir.mkdir(parents=True, exist_ok=True)
           self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
           logger.info("[filesystem] Storage backend initialized")
       except OSError as e:
           logger.error(f"[filesystem] Failed to initialize storage backend: {e}")
           raise
   ```

### Step 3: Update AzureBlobStorageBackend

**File**: `src/documents/storage/azure_blob.py`

1. Implement `_resolve_path()` method:
   ```python
   def _resolve_path(self, tenant_path: str) -> str:
       """
       Resolve tenant-prefixed path to Azure blob name.

       Args:
           tenant_path: Tenant-prefixed path (e.g., 'acme-corp/documents/originals/0000123.pdf')

       Returns:
           Azure blob name (same as tenant_path for Azure)
       """
       # For Azure, blob name is the tenant-prefixed path
       # Validate path to prevent directory traversal
       if ".." in tenant_path or "//" in tenant_path:
           raise ValueError(
               f"Invalid path: {tenant_path} (directory traversal detected)"
           )
       return tenant_path
   ```

2. Remove old `get_path()` implementation (replaced by base class)

### Step 4: Add Tests

**File**: `src/documents/tests/storage/test_tenant_segregation.py`

Create comprehensive tests for:
- Tenant path prefixing in base class
- Filesystem backend tenant segregation
- Azure backend tenant segregation
- Error handling when tenant context missing
- Path validation and security checks
- Cross-tenant isolation enforcement

**Example test structure**:
```python
import pytest
from documents.storage.factory import get_backend
from paperless.tenants.models import Tenant
from paperless.tenants.utils import set_current_tenant, clear_current_tenant

@pytest.mark.django_db
def test_tenant_path_prefixing():
    """Test that storage paths include tenant identifier."""
    tenant = Tenant.objects.create(
        name="Test Tenant",
        identifier="test-tenant"
    )
    set_current_tenant(tenant)

    try:
        backend = get_backend("filesystem")
        path = backend.get_path("documents/originals/test.pdf")
        assert "test-tenant" in path
        assert path.startswith(str(settings.ORIGINALS_DIR / "test-tenant"))
    finally:
        clear_current_tenant()

@pytest.mark.django_db
def test_missing_tenant_context():
    """Test that storage operations fail without tenant context."""
    clear_current_tenant()

    backend = get_backend("filesystem")
    with pytest.raises(ValueError, match="Tenant context not set"):
        backend.get_path("documents/originals/test.pdf")
```

### Step 5: Update Logging

Add tenant identifier to storage operation logs:

```python
logger.debug(
    f"[{backend_type}] Tenant: {tenant.identifier}, "
    f"Operation: {operation}, Path: {path}"
)
```

## Verification

### Manual Testing

1. **Set up test tenants**:
   ```python
   tenant1 = Tenant.objects.create(name="Tenant 1", identifier="tenant-1")
   tenant2 = Tenant.objects.create(name="Tenant 2", identifier="tenant-2")
   ```

2. **Test document storage**:
   - Set tenant context for tenant1
   - Upload document
   - Verify file stored at `{ORIGINALS_DIR}/tenant-1/documents/originals/...`
   - Set tenant context for tenant2
   - Upload document
   - Verify file stored at `{ORIGINALS_DIR}/tenant-2/documents/originals/...`

3. **Test tenant isolation**:
   - Set tenant context for tenant1
   - Attempt to access tenant2's document path
   - Verify access is prevented or file not found

### Automated Testing

Run test suite:
```bash
pytest src/documents/tests/storage/ -v
```

Check coverage:
```bash
pytest src/documents/tests/storage/ --cov=documents.storage --cov-report=html
```

## Common Issues

### Issue: "Tenant context not set" errors

**Solution**: Ensure tenant middleware is configured and user has tenant association. Check that `get_current_tenant()` returns a tenant object.

### Issue: Files stored without tenant prefix

**Solution**: Verify that `get_path()` method is using base class implementation and calling `_resolve_path()` with tenant-prefixed path.

### Issue: Path traversal vulnerabilities

**Solution**: Ensure path validation checks for ".." and "//" in both base class and backend implementations.

## Next Steps

After implementation:
1. Run full test suite to ensure no regressions
2. Update documentation for storage backends
3. Consider migration strategy for existing files (if needed)
4. Monitor logs for tenant context issues in production

