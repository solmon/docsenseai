"""
Filesystem storage backend implementation.

This backend maintains existing filesystem storage behavior for backward compatibility.
"""

import logging
import shutil
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from django.conf import settings

from documents.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class FilesystemStorageBackend(StorageBackend):
    """
    Filesystem storage backend implementation.

    Maintains existing file system behavior for backward compatibility.
    Uses existing Django settings: ORIGINALS_DIR, ARCHIVE_DIR, THUMBNAIL_DIR.
    """

    def __init__(self) -> None:
        """Initialize filesystem storage backend."""
        self.originals_dir = settings.ORIGINALS_DIR
        self.archive_dir = settings.ARCHIVE_DIR
        self.thumbnail_dir = settings.THUMBNAIL_DIR

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
        storage_path = self.get_path(path)
        file_path = Path(storage_path)

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        try:
            with file_path.open("wb") as f:
                shutil.copyfileobj(file_obj, f)
            logger.debug(
                f"[filesystem] Stored file: {path} -> {storage_path} "
                f"(tenant context applied)",
            )
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to store file {path}: {e}")
            raise

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
        storage_path = self.get_path(path)
        file_path = Path(storage_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with file_path.open("rb") as f:
                content = f.read()
            logger.debug(f"[filesystem] Retrieved file: {path} -> {storage_path}")
            return BytesIO(content)
        except OSError as e:
            logger.error(f"[filesystem] Failed to retrieve file {path}: {e}")
            raise

    def delete(self, path: str) -> None:
        """
        Delete a file at the specified logical path.

        Args:
            path: Logical path to delete

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If deletion operation fails
        """
        storage_path = self.get_path(path)
        file_path = Path(storage_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            file_path.unlink()
            logger.debug(f"[filesystem] Deleted file: {path} -> {storage_path}")
        except OSError as e:
            logger.error(f"[filesystem] Failed to delete file {path}: {e}")
            raise

    def exists(self, path: str) -> bool:
        """
        Check if a file exists at the specified logical path.

        Args:
            path: Logical path to check

        Returns:
            True if file exists, False otherwise
        """
        storage_path = self.get_path(path)
        file_path = Path(storage_path)
        return file_path.exists()

    def _resolve_path(self, tenant_path: str) -> str:
        """
        Resolve a tenant-prefixed path to a filesystem absolute path.

        Args:
            tenant_path: Tenant-prefixed path (e.g., 'acme-corp/documents/originals/0000123.pdf')

        Returns:
            Absolute filesystem path with tenant directory structure

        Note:
            The tenant_path already includes the tenant identifier prefix.
            This method extracts the tenant identifier and logical path, then
            resolves to the appropriate filesystem directory.
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
            return str(
                (
                    self.originals_dir
                    / tenant_id
                    / "documents"
                    / "originals"
                    / filename
                ).resolve(),
            )
        elif logical_path.startswith("documents/archive/"):
            filename = logical_path.replace("documents/archive/", "")
            return str(
                (
                    self.archive_dir / tenant_id / "documents" / "archive" / filename
                ).resolve(),
            )
        elif logical_path.startswith("documents/thumbnails/"):
            filename = logical_path.replace("documents/thumbnails/", "")
            return str(
                (
                    self.thumbnail_dir
                    / tenant_id
                    / "documents"
                    / "thumbnails"
                    / filename
                ).resolve(),
            )
        else:
            # Fallback: assume originals directory
            return str((self.originals_dir / tenant_id / logical_path).resolve())

    def initialize(self) -> None:
        """
        Initialize the storage backend.

        Creates directories if needed. Called at application startup.

        Raises:
            OSError: If initialization fails
        """
        try:
            self.originals_dir.mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[filesystem] Storage backend initialized")
        except OSError as e:
            logger.error(f"[filesystem] Failed to initialize storage backend: {e}")
            raise
