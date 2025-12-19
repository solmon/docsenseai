"""
Storage backend factory and registry.

This module provides a factory pattern for creating and managing storage backend instances.
"""

import logging
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from documents.storage.base import StorageBackend

logger = logging.getLogger(__name__)

# Registry of available storage backends
_BACKEND_REGISTRY: dict[str, type["StorageBackend"]] = {}
_STORAGE_BACKEND_INSTANCE: "StorageBackend | None" = None


def register_backend(backend_type: str, backend_class: type["StorageBackend"]) -> None:
    """
    Register a storage backend class.

    Args:
        backend_type: Backend type identifier (e.g., 'filesystem', 'azure_blob')
        backend_class: Storage backend class implementing StorageBackend interface
    """
    _BACKEND_REGISTRY[backend_type] = backend_class
    logger.debug(f"Registered storage backend: {backend_type}")


# Register built-in backends
from documents.storage.azure_blob import AzureBlobStorageBackend
from documents.storage.filesystem import FilesystemStorageBackend

register_backend("filesystem", FilesystemStorageBackend)
register_backend("azure_blob", AzureBlobStorageBackend)


def get_backend(backend_type: str | None = None) -> "StorageBackend":
    """
    Get a storage backend instance.

    Args:
        backend_type: Backend type identifier. If None, uses configured backend.

    Returns:
        Storage backend instance

    Raises:
        ValueError: If backend type is invalid or not registered
    """
    if backend_type is None:
        backend_type = getattr(settings, "PAPERLESS_STORAGE_BACKEND", "filesystem")

    if backend_type not in _BACKEND_REGISTRY:
        available = ", ".join(_BACKEND_REGISTRY.keys())
        raise ValueError(
            f"Invalid storage backend '{backend_type}'. "
            f"Available backends: {available}",
        )

    backend_class = _BACKEND_REGISTRY[backend_type]
    return backend_class()


def get_storage_backend() -> "StorageBackend":
    """
    Get the configured storage backend instance (singleton).

    Returns:
        Storage backend instance
    """
    global _STORAGE_BACKEND_INSTANCE

    if _STORAGE_BACKEND_INSTANCE is None:
        backend_type = getattr(settings, "PAPERLESS_STORAGE_BACKEND", "filesystem")
        _STORAGE_BACKEND_INSTANCE = get_backend(backend_type)
        logger.info(f"Initialized storage backend: {backend_type}")

    return _STORAGE_BACKEND_INSTANCE


def reset_storage_backend() -> None:
    """
    Reset the storage backend instance (useful for testing).
    """
    global _STORAGE_BACKEND_INSTANCE
    _STORAGE_BACKEND_INSTANCE = None

