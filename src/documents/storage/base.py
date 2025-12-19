"""
Abstract base class for storage backends.

This module defines the interface that all storage backend implementations must follow.

To implement a new storage backend:
1. Create a class extending StorageBackend
2. Implement all abstract methods (store, retrieve, delete, exists, get_path, initialize)
3. Register the backend in documents.storage.factory using register_backend()
4. Add configuration settings in paperless.settings if needed
5. Update configuration validation in paperless.settings._validate_storage_backend_config()

Example:
    class MyStorageBackend(StorageBackend):
        def store(self, path: str, file_obj: BinaryIO) -> None:
            # Implementation
            pass
        # ... implement other methods
"""

import logging
from abc import ABC
from abc import abstractmethod
from typing import BinaryIO

from paperless.tenants.utils import get_current_tenant

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """
    Abstract base class for storage backend implementations.

    All storage backends must implement this interface to provide consistent
    file operations across different storage systems (filesystem, cloud storage, etc.).

    Thread Safety:
        All implementations must be thread-safe as storage operations may be
        called concurrently from multiple threads.

    Path Handling:
        - Logical paths are relative paths like 'documents/originals/0000123.pdf'
        - get_path() resolves logical paths to storage-specific paths with tenant prefix
        - Tenant prefix is automatically added: '{tenant_identifier}/{logical_path}'
        - For filesystem: returns absolute filesystem path with tenant directory
        - For cloud storage: returns blob/object name with tenant prefix
    """

    @abstractmethod
    def store(self, path: str, file_obj: BinaryIO) -> None:
        """
        Store a file at the specified logical path.

        Args:
            path: Logical path (e.g., 'documents/originals/0000123.pdf')
            file_obj: File-like object containing file data. The file pointer
                should be at the beginning of the file. The method may read
                from the file object but should not assume it can seek.

        Raises:
            OSError: If storage operation fails
            PermissionError: If access is denied

        Note:
            Implementations should create parent directories/containers as needed.
            For filesystem backends, this means creating directory structure.
            For cloud storage, this may mean ensuring containers/buckets exist.
        """

    @abstractmethod
    def retrieve(self, path: str) -> BinaryIO:
        """
        Retrieve a file from the specified logical path.

        Args:
            path: Logical path to retrieve

        Returns:
            File-like object (BytesIO) containing file data. The returned object
            should support read() and seek() operations. Caller is responsible
            for closing/cleaning up the returned object if needed.

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If retrieval operation fails

        Note:
            Implementations should return a BytesIO object or similar file-like
            object that can be read multiple times. The file pointer should be
            at the beginning of the file.
        """

    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Delete a file at the specified logical path.

        Args:
            path: Logical path to delete

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If deletion operation fails

        Note:
            Implementations should handle the case where the file doesn't exist
            gracefully (raise FileNotFoundError rather than silently succeeding).
        """

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a file exists at the specified logical path.

        Args:
            path: Logical path to check

        Returns:
            True if file exists, False otherwise

        Note:
            This method should not raise exceptions for non-existent files.
            It should return False if the file doesn't exist, and only raise
            exceptions for actual errors (e.g., connection failures).
        """

    def _get_tenant_prefix(self) -> str:
        """
        Get the tenant identifier prefix for the current tenant context.

        Returns:
            Tenant identifier string (e.g., 'acme-corp')

        Raises:
            ValueError: If tenant context is not available
        """
        tenant = get_current_tenant()
        if tenant is None:
            raise ValueError(
                "Tenant context not set. Cannot determine tenant for storage path. "
                "Ensure middleware is configured correctly and user has tenant association.",
            )

        if not tenant.identifier:
            raise ValueError(f"Tenant {tenant.id} has no identifier")

        return tenant.identifier

    def get_path(self, logical_path: str) -> str:
        """
        Resolve a logical path to a storage-specific path with tenant prefix.

        Args:
            logical_path: Logical path (e.g., 'documents/originals/0000123.pdf')

        Returns:
            Storage-specific path with tenant prefix:
            - For filesystem: absolute filesystem path with tenant directory
            - For cloud storage: blob/object name with tenant prefix

        Raises:
            ValueError: If tenant context is not available or path is invalid

        Note:
            This method automatically adds tenant identifier as prefix to ensure
            tenant isolation. The tenant prefix is added before calling _resolve_path()
            for backend-specific path resolution.
        """
        # Validate path to prevent directory traversal
        if ".." in logical_path or "//" in logical_path:
            raise ValueError(
                f"Invalid path: {logical_path} (directory traversal detected)",
            )

        # Get tenant identifier prefix
        tenant_identifier = self._get_tenant_prefix()

        # Construct tenant-prefixed path
        tenant_path = f"{tenant_identifier}/{logical_path}"

        # Log tenant context for debugging
        logger.debug(
            f"Resolving path with tenant context: tenant={tenant_identifier}, "
            f"logical_path={logical_path}",
        )

        # Delegate to backend-specific path resolution
        return self._resolve_path(tenant_path)

    @abstractmethod
    def _resolve_path(self, tenant_path: str) -> str:
        """
        Resolve a tenant-prefixed path to a storage-specific path.

        Args:
            tenant_path: Tenant-prefixed path (e.g., 'acme-corp/documents/originals/0000123.pdf')

        Returns:
            Storage-specific path:
            - For filesystem: absolute filesystem path (str)
            - For cloud storage: blob/object name (str)

        Note:
            This method is implemented by each storage backend to handle
            backend-specific path resolution. The tenant prefix is already
            included in the tenant_path parameter.
        """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the storage backend.

        Creates containers/directories if needed. Called at application startup
        after configuration validation.

        Raises:
            OSError: If initialization fails (e.g., cannot create directories)
            ConnectionError: If connection to storage fails (e.g., Azure connection)

        Note:
            This method is called once at application startup. It should:
            - Create necessary containers/directories if they don't exist
            - Verify connectivity to storage
            - Set up any required resources
            - Log initialization status
        """
