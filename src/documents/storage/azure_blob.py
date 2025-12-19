"""
Azure Blob Storage backend implementation.

This backend stores documents in Azure Blob Storage containers.
"""

import logging
from io import BytesIO
from typing import BinaryIO

from azure.core.exceptions import AzureError
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from django.conf import settings

from documents.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class AzureBlobStorageBackend(StorageBackend):
    """
    Azure Blob Storage backend implementation.

    Stores documents in Azure Blob Storage containers.
    Uses connection string and container name from settings.
    """

    def __init__(self) -> None:
        """Initialize Azure Blob Storage backend."""
        self.connection_string = settings.PAPERLESS_AZURE_CONNECTION_STRING
        self.container_name = settings.PAPERLESS_AZURE_CONTAINER_NAME

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string,
            )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name,
            )
        except Exception as e:
            logger.error(f"[azure_blob] Failed to create Azure clients: {e}")
            raise ConnectionError(f"Azure connection failed: {e}") from e

    def store(self, path: str, file_obj: BinaryIO) -> None:
        """
        Store a file at the specified logical path.

        Args:
            path: Logical path (e.g., 'documents/originals/0000123.pdf')
            file_obj: File-like object containing file data

        Raises:
            OSError: If storage operation fails
            PermissionError: If access is denied
        """
        blob_name = self.get_path(path)
        blob_client = self.container_client.get_blob_client(blob_name)

        try:
            # Reset file pointer to beginning
            file_obj.seek(0)
            blob_client.upload_blob(file_obj, overwrite=True)
            logger.debug(
                f"[azure_blob] Stored file: {path} -> {blob_name} "
                f"(tenant context applied)",
            )
        except AzureError as e:
            logger.error(f"[azure_blob] Failed to store file {path}: {e}")
            raise OSError(f"Azure storage operation failed: {e}") from e

    def retrieve(self, path: str) -> BinaryIO:
        """
        Retrieve a file from the specified logical path.

        Args:
            path: Logical path to retrieve

        Returns:
            File-like object (BytesIO) containing file data

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If retrieval operation fails
        """
        blob_name = self.get_path(path)
        blob_client = self.container_client.get_blob_client(blob_name)

        try:
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            logger.debug(f"[azure_blob] Retrieved file: {path} -> {blob_name}")
            return BytesIO(content)
        except ResourceNotFoundError:
            raise FileNotFoundError(f"File not found in Azure: {path}")
        except AzureError as e:
            logger.error(f"[azure_blob] Failed to retrieve file {path}: {e}")
            raise OSError(f"Azure retrieval operation failed: {e}") from e

    def delete(self, path: str) -> None:
        """
        Delete a file at the specified logical path.

        Args:
            path: Logical path to delete

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If deletion operation fails
        """
        blob_name = self.get_path(path)
        blob_client = self.container_client.get_blob_client(blob_name)

        try:
            blob_client.delete_blob()
            logger.debug(f"[azure_blob] Deleted file: {path} -> {blob_name}")
        except ResourceNotFoundError:
            raise FileNotFoundError(f"File not found in Azure: {path}")
        except AzureError as e:
            logger.error(f"[azure_blob] Failed to delete file {path}: {e}")
            raise OSError(f"Azure deletion operation failed: {e}") from e

    def exists(self, path: str) -> bool:
        """
        Check if a file exists at the specified logical path.

        Args:
            path: Logical path to check

        Returns:
            True if file exists, False otherwise
        """
        blob_name = self.get_path(path)
        blob_client = self.container_client.get_blob_client(blob_name)

        try:
            return blob_client.exists()
        except AzureError as e:
            logger.error(f"[azure_blob] Failed to check existence of {path}: {e}")
            return False

    def _resolve_path(self, tenant_path: str) -> str:
        """
        Resolve a tenant-prefixed path to an Azure blob name.

        Args:
            tenant_path: Tenant-prefixed path (e.g., 'acme-corp/documents/originals/0000123.pdf')

        Returns:
            Azure blob name (same as tenant_path for Azure)

        Note:
            The tenant_path already includes the tenant identifier prefix.
            For Azure Blob Storage, the blob name is the tenant-prefixed path.
            Validates path to prevent directory traversal attacks.
        """
        # Validate path to prevent directory traversal
        if ".." in tenant_path or "//" in tenant_path:
            raise ValueError(
                f"Invalid path: {tenant_path} (directory traversal detected)",
            )

        # For Azure, blob name is the tenant-prefixed path
        return tenant_path

    def initialize(self) -> None:
        """
        Initialize the storage backend.

        Creates container if it doesn't exist. Called at application startup.

        Raises:
            OSError: If initialization fails
            ConnectionError: If connection to Azure fails
        """
        try:
            # Check if container exists, create if not
            if not self.container_client.exists():
                self.container_client.create_container()
                logger.info(f"[azure_blob] Created container: {self.container_name}")
            else:
                logger.info(
                    f"[azure_blob] Container already exists: {self.container_name}"
                )
            logger.info("[azure_blob] Storage backend initialized")
        except AzureError as e:
            logger.error(f"[azure_blob] Failed to initialize storage backend: {e}")
            raise ConnectionError(f"Azure connection failed: {e}") from e
