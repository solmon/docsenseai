# Data Model: Multiple Storage Backends

**Feature**: Multiple Storage Backends
**Date**: 2025-01-27
**Phase**: 1 - Design & Contracts

## Overview

This feature introduces a storage backend abstraction layer. The data model changes are minimal - the database schema remains unchanged. File paths stored in the database continue to be logical paths (relative paths), which are resolved by the storage backend to actual storage locations.

## Entities

### Storage Backend (Abstract Interface)

**Type**: Abstract Base Class (ABC) / Protocol
**Purpose**: Defines the contract that all storage backend implementations must follow.

**Interface Methods**:

- `store(path: str, file_obj: BinaryIO) -> None`
  - Stores a file at the specified logical path
  - `path`: Logical path (e.g., `documents/originals/0000123.pdf`)
  - `file_obj`: File-like object containing file data
  - Raises: `OSError`, `PermissionError` on failure

- `retrieve(path: str) -> BinaryIO`
  - Retrieves a file from the specified logical path
  - `path`: Logical path to retrieve
  - Returns: File-like object (BytesIO or file handle)
  - Raises: `FileNotFoundError` if file doesn't exist, `OSError` on other failures

- `delete(path: str) -> None`
  - Deletes a file at the specified logical path
  - `path`: Logical path to delete
  - Raises: `FileNotFoundError` if file doesn't exist, `OSError` on other failures

- `exists(path: str) -> bool`
  - Checks if a file exists at the specified logical path
  - `path`: Logical path to check
  - Returns: `True` if file exists, `False` otherwise

- `get_path(logical_path: str) -> str`
  - Resolves a logical path to a storage-specific path
  - `logical_path`: Logical path (e.g., `documents/originals/0000123.pdf`)
  - Returns: Storage-specific path (filesystem absolute path or Azure blob name)
  - Note: For filesystem, returns absolute path. For Azure, returns blob name.

- `initialize() -> None`
  - Initializes the storage backend (creates containers/directories if needed)
  - Called at application startup
  - Raises: `OSError`, `ConnectionError` if initialization fails

**State**: Stateless (each method is independent)
**Thread Safety**: All implementations must be thread-safe

---

### Filesystem Storage Backend

**Type**: Concrete implementation of Storage Backend
**Purpose**: Maintains existing filesystem storage behavior for backward compatibility.

**Configuration**:
- Uses existing Django settings: `ORIGINALS_DIR`, `ARCHIVE_DIR`, `THUMBNAIL_DIR`
- No additional configuration required

**Path Resolution**:
- Logical path: `documents/originals/0000123.pdf`
- Resolved path: `{MEDIA_ROOT}/documents/originals/0000123.pdf`
- Uses `pathlib.Path` for path operations

**Behavior**:
- Creates directories as needed (maintains existing `create_source_path_directory` behavior)
- Preserves file metadata (timestamps, permissions) where possible
- Handles concurrent access with file locks (existing `FileLock` mechanism)

---

### Azure Blob Storage Backend

**Type**: Concrete implementation of Storage Backend
**Purpose**: Stores documents in Azure Blob Storage containers.

**Configuration** (via environment variables):
- `PAPERLESS_AZURE_CONNECTION_STRING`: Azure Storage account connection string
- `PAPERLESS_AZURE_CONTAINER_NAME`: Container name for storing documents

**Path Resolution**:
- Logical path: `documents/originals/0000123.pdf`
- Resolved path (blob name): `documents/originals/0000123.pdf` (same, stored as blob name)
- Container structure mirrors logical path structure

**Behavior**:
- Creates container if it doesn't exist during initialization
- Uses Azure Blob Storage SDK (`azure-storage-blob`)
- Handles authentication via connection string (managed identity support as future enhancement)
- Implements retry logic via Azure SDK retry policies
- Streams large files for efficient memory usage

**Blob Organization**:
- Originals: `documents/originals/{filename}`
- Archives: `documents/archive/{filename}`
- Thumbnails: `documents/thumbnails/{filename}`

---

### Storage Configuration

**Type**: Django Settings / Environment Variables
**Purpose**: Configuration that determines which storage backend to use.

**Fields**:

- `PAPERLESS_STORAGE_BACKEND` (str, optional, default: 'filesystem')
  - Values: 'filesystem' or 'azure_blob'
  - Determines which storage backend implementation to use

- `PAPERLESS_AZURE_CONNECTION_STRING` (str, required if backend is 'azure_blob')
  - Azure Storage account connection string
  - Format: `DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=...`
  - Validated at application startup

- `PAPERLESS_AZURE_CONTAINER_NAME` (str, required if backend is 'azure_blob')
  - Name of Azure Blob Storage container
  - Container created automatically if it doesn't exist
  - Validated at application startup

**Validation Rules**:
- `PAPERLESS_STORAGE_BACKEND` must be 'filesystem' or 'azure_blob'
- If `PAPERLESS_STORAGE_BACKEND='azure_blob'`, both Azure environment variables must be present
- Connection string format validated (basic format check)
- Container name validated (Azure naming rules)

---

### Document Model (Modified Properties)

**Type**: Django Model (existing `Document` model)
**Changes**: Properties `source_path`, `archive_path`, `thumbnail_path` now use storage backend

**Existing Fields** (unchanged):
- `filename`: Original filename (string)
- `archive_filename`: Archive filename (string, nullable)
- All other fields remain unchanged

**Modified Properties**:

- `source_path` (property)
  - **Before**: Returned `Path` object pointing to filesystem location
  - **After**: Returns logical path string, resolved by storage backend
  - Usage: `document.source_path` returns logical path, storage backend resolves to actual location

- `archive_path` (property)
  - **Before**: Returned `Path` object pointing to filesystem location
  - **After**: Returns logical path string, resolved by storage backend
  - Usage: `document.archive_path` returns logical path, storage backend resolves to actual location

- `thumbnail_path` (property)
  - **Before**: Returned `Path` object pointing to filesystem location
  - **After**: Returns logical path string, resolved by storage backend
  - Usage: `document.thumbnail_path` returns logical path, storage backend resolves to actual location

**Modified Methods**:

- `source_file` (property)
  - **Before**: Opened file using `Path(source_path).open("rb")`
  - **After**: Uses storage backend `retrieve()` method
  - Returns: File-like object from storage backend

- `archive_file` (property)
  - **Before**: Opened file using `Path(archive_path).open("rb")`
  - **After**: Uses storage backend `retrieve()` method
  - Returns: File-like object from storage backend

- `thumbnail_file` (property)
  - **Before**: Opened file using `Path(thumbnail_path).open("rb")`
  - **After**: Uses storage backend `retrieve()` method
  - Returns: File-like object from storage backend

**Database Schema**: No changes - paths stored as strings in existing fields

---

## Relationships

### Storage Backend → Document Operations

- **One-to-Many**: One storage backend instance handles all document operations
- **Singleton Pattern**: Single storage backend instance per application
- **Access Pattern**: Documents access storage backend via `get_storage_backend()` function

### Storage Configuration → Storage Backend

- **One-to-One**: Configuration determines which backend implementation to instantiate
- **Factory Pattern**: Storage backend factory creates appropriate backend based on configuration

---

## State Transitions

### Storage Backend Initialization

1. **Application Startup**
   - Read `PAPERLESS_STORAGE_BACKEND` from environment
   - Validate configuration (required variables present, valid values)
   - Instantiate appropriate storage backend via factory
   - Call `backend.initialize()` to set up storage (create containers/directories)
   - Store backend instance (singleton)

2. **Backend Ready**
   - Backend instance available via `get_storage_backend()`
   - All document operations use this backend instance

### Document Storage Operations

1. **Upload/Store**
   - Generate logical path (e.g., `documents/originals/0000123.pdf`)
   - Call `backend.store(logical_path, file_obj)`
   - Backend resolves logical path to storage-specific path
   - File stored in appropriate location (filesystem or Azure)

2. **Retrieve**
   - Use logical path from database
   - Call `backend.retrieve(logical_path)`
   - Backend resolves logical path and retrieves file
   - Return file-like object to caller

3. **Delete**
   - Use logical path from database
   - Call `backend.delete(logical_path)`
   - Backend resolves logical path and deletes file

---

## Validation Rules

### Path Validation

- Logical paths must use forward slashes as separators
- Paths must be relative (not absolute)
- Path components must not contain directory traversal sequences (`..`, `//`)
- Paths must match expected structure: `documents/{type}/{filename}`

### Configuration Validation

- `PAPERLESS_STORAGE_BACKEND` must be one of: 'filesystem', 'azure_blob'
- Azure connection string must be valid format (basic validation)
- Azure container name must comply with Azure naming rules (lowercase, alphanumeric, hyphens)

---

## Data Migration

**No database migrations required**. The database schema remains unchanged. File paths continue to be stored as strings in existing fields (`filename`, `archive_filename`). The storage backend abstraction handles path resolution transparently.

**Existing Data Compatibility**:
- Existing documents with filesystem paths continue to work
- Logical paths are backward-compatible with existing path strings
- No data migration needed when switching storage backends

---

## Notes

- All storage operations are logged with backend type for debugging
- Storage backend is thread-safe (required for concurrent document operations)
- Path normalization ensures cross-platform and cross-backend compatibility
- Error handling uses standard Python exceptions for consistency
- Storage backend abstraction is transparent to API consumers (no API changes)

