"""
Storage backend abstraction for Paperless-ngx.

This module provides an abstract interface for storage backends, allowing
the application to use different storage systems (filesystem, Azure Blob Storage, etc.)
transparently.
"""

from documents.storage.factory import get_storage_backend

__all__ = ["get_storage_backend"]

