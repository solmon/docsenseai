"""
Example storage backend implementation.

This is a template/stub for implementing a new storage backend.
This file is for documentation purposes only and is not used by the application.

To implement a new storage backend:
1. Copy this file and rename it (e.g., s3_backend.py)
2. Replace ExampleStorageBackend with your backend class name
3. Implement all abstract methods from StorageBackend
4. Register your backend in factory.py
5. Add configuration settings in settings.py
6. Update configuration validation in settings.py
"""

from io import BytesIO
from typing import BinaryIO

from documents.storage.base import StorageBackend


class ExampleStorageBackend(StorageBackend):
    """
    Example storage backend implementation.

    This demonstrates the structure required for a new storage backend.
    Replace this with your actual implementation.
    """

    def __init__(self) -> None:
        """Initialize the storage backend."""
        # Add your initialization code here
        # e.g., create clients, verify credentials, etc.
        pass

    def store(self, path: str, file_obj: BinaryIO) -> None:
        """
        Store a file at the specified logical path.

        Implementation example:
        - Resolve logical path to storage-specific path using get_path()
        - Write file_obj content to storage
        - Handle errors appropriately
        """
        storage_path = self.get_path(path)
        # Implement storage logic here
        # Example: write file_obj to storage_path
        raise NotImplementedError("Implement store() method")

    def retrieve(self, path: str) -> BinaryIO:
        """
        Retrieve a file from the specified logical path.

        Implementation example:
        - Resolve logical path to storage-specific path
        - Read file content from storage
        - Return BytesIO object with file content
        """
        storage_path = self.get_path(path)
        # Implement retrieval logic here
        # Example: read from storage_path and return BytesIO
        raise NotImplementedError("Implement retrieve() method")

    def delete(self, path: str) -> None:
        """
        Delete a file at the specified logical path.

        Implementation example:
        - Resolve logical path to storage-specific path
        - Delete file from storage
        - Raise FileNotFoundError if file doesn't exist
        """
        storage_path = self.get_path(path)
        # Implement deletion logic here
        raise NotImplementedError("Implement delete() method")

    def exists(self, path: str) -> bool:
        """
        Check if a file exists at the specified logical path.

        Implementation example:
        - Resolve logical path to storage-specific path
        - Check if file exists in storage
        - Return True/False (don't raise exceptions for non-existent files)
        """
        storage_path = self.get_path(path)
        # Implement existence check here
        raise NotImplementedError("Implement exists() method")

    def get_path(self, logical_path: str) -> str:
        """
        Resolve a logical path to a storage-specific path.

        Implementation example:
        - For filesystem: return absolute filesystem path
        - For cloud storage: return blob/object name (may be same as logical_path)
        - Validate path to prevent directory traversal attacks
        """
        # Validate path to prevent directory traversal
        if ".." in logical_path or "//" in logical_path:
            raise ValueError(f"Invalid path: {logical_path} (directory traversal detected)")

        # Implement path resolution here
        # Example: return logical_path for cloud storage, or resolve to absolute path for filesystem
        raise NotImplementedError("Implement get_path() method")

    def initialize(self) -> None:
        """
        Initialize the storage backend.

        Implementation example:
        - Create containers/buckets/directories if needed
        - Verify connectivity to storage
        - Set up any required resources
        - Log initialization status
        """
        # Implement initialization logic here
        # Example: create container, verify connection, etc.
        raise NotImplementedError("Implement initialize() method")

