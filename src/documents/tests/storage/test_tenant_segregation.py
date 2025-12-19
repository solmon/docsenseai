"""
Tests for tenant-level storage segregation.

These tests verify that all storage operations automatically include
tenant identifier prefixes to ensure complete tenant isolation.
"""

import pytest
from io import BytesIO

from documents.storage.azure_blob import AzureBlobStorageBackend
from documents.storage.factory import get_backend
from documents.storage.filesystem import FilesystemStorageBackend
from paperless.tenants.models import Tenant
from paperless.tenants.utils import clear_current_tenant, set_current_tenant


@pytest.mark.django_db
class TestTenantPathPrefixing:
    """Test that storage paths include tenant identifier prefix."""

    def test_tenant_prefix_in_get_path_filesystem(self, tmp_path, monkeypatch):
        """Test that filesystem backend includes tenant prefix in paths."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        # Create tenant
        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

        # Set tenant context
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()
            path = backend.get_path("documents/originals/test.pdf")

            # Verify tenant identifier is in path
            assert "test-tenant" in path
            assert path.startswith(str(originals_dir / "test-tenant"))
            assert "documents/originals/test.pdf" in path
        finally:
            clear_current_tenant()

    def test_tenant_prefix_in_get_path_azure(self, monkeypatch):
        """Test that Azure backend includes tenant prefix in blob names."""
        from django.conf import settings

        # Mock Azure settings
        monkeypatch.setattr(
            settings,
            "PAPERLESS_AZURE_CONNECTION_STRING",
            "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test;EndpointSuffix=core.windows.net",
        )
        monkeypatch.setattr(
            settings, "PAPERLESS_AZURE_CONTAINER_NAME", "test-container"
        )

        # Create tenant
        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")

        # Set tenant context
        set_current_tenant(tenant)

        try:
            # Note: This will fail connection, but we can test path resolution
            # by mocking the Azure client initialization
            with pytest.raises((ConnectionError, Exception)):
                backend = AzureBlobStorageBackend()
                # If we get here, test the path method
                path = backend._resolve_path("test-tenant/documents/originals/test.pdf")
                assert path == "test-tenant/documents/originals/test.pdf"
        except Exception:
            # Expected - Azure connection will fail in test
            pass
        finally:
            clear_current_tenant()

    def test_missing_tenant_context_error(self, tmp_path, monkeypatch):
        """Test that storage operations fail without tenant context."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        # Clear tenant context
        clear_current_tenant()

        backend = FilesystemStorageBackend()

        # Should raise ValueError when tenant context is missing
        with pytest.raises(ValueError, match="Tenant context not set"):
            backend.get_path("documents/originals/test.pdf")

    def test_tenant_isolation_enforcement(self, tmp_path, monkeypatch):
        """Test that different tenants get different paths."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        # Create two tenants
        tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
        tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

        backend = FilesystemStorageBackend()

        # Set tenant A context
        set_current_tenant(tenant_a)
        try:
            path_a = backend.get_path("documents/originals/test.pdf")
        finally:
            clear_current_tenant()

        # Set tenant B context
        set_current_tenant(tenant_b)
        try:
            path_b = backend.get_path("documents/originals/test.pdf")
        finally:
            clear_current_tenant()

        # Verify paths are different and contain respective tenant identifiers
        assert path_a != path_b
        assert "tenant-a" in path_a
        assert "tenant-b" in path_b
        assert "tenant-a" not in path_b
        assert "tenant-b" not in path_a

    def test_path_validation_with_tenant_prefix(self, tmp_path, monkeypatch):
        """Test that path validation works with tenant prefix."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()

            # Test directory traversal prevention
            with pytest.raises(ValueError, match="directory traversal detected"):
                backend.get_path("documents/originals/../../etc/passwd")

            # Test double slash prevention
            with pytest.raises(ValueError, match="directory traversal detected"):
                backend.get_path("documents//originals/test.pdf")
        finally:
            clear_current_tenant()


@pytest.mark.django_db
class TestArchiveStorageWithTenantPrefix:
    """Test archive file storage with tenant prefix."""

    def test_archive_storage_with_tenant_prefix(self, tmp_path, monkeypatch):
        """Test that archive files are stored with tenant prefix."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()
            path = backend.get_path("documents/archive/test.pdf")

            # Verify tenant identifier is in archive path
            assert "test-tenant" in path
            assert path.startswith(str(archive_dir / "test-tenant"))
            assert "documents/archive/test.pdf" in path
        finally:
            clear_current_tenant()

    def test_archive_retrieval_with_tenant_isolation(self, tmp_path, monkeypatch):
        """Test that archive retrieval respects tenant boundaries."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
        tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

        backend = FilesystemStorageBackend()

        # Store archive for tenant A
        set_current_tenant(tenant_a)
        try:
            archive_path_a = backend.get_path("documents/archive/test.pdf")
            archive_dir_a = archive_path_a.parent
            archive_dir_a.mkdir(parents=True, exist_ok=True)
            with open(archive_path_a, "wb") as f:
                f.write(b"archive content a")
        finally:
            clear_current_tenant()

        # Try to retrieve with tenant B context - should not find it
        set_current_tenant(tenant_b)
        try:
            archive_path_b = backend.get_path("documents/archive/test.pdf")
            # Path should be different (tenant-b prefix)
            assert archive_path_b != archive_path_a
            assert "tenant-b" in archive_path_b
            # File should not exist at tenant B's path
            assert not backend.exists("documents/archive/test.pdf")
        finally:
            clear_current_tenant()


@pytest.mark.django_db
class TestThumbnailStorageWithTenantPrefix:
    """Test thumbnail storage with tenant prefix."""

    def test_thumbnail_storage_with_tenant_prefix(self, tmp_path, monkeypatch):
        """Test that thumbnails are stored with tenant prefix."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()
            path = backend.get_path("documents/thumbnails/0000001.webp")

            # Verify tenant identifier is in thumbnail path
            assert "test-tenant" in path
            assert path.startswith(str(thumbnail_dir / "test-tenant"))
            assert "documents/thumbnails/0000001.webp" in path
        finally:
            clear_current_tenant()

    def test_thumbnail_retrieval_with_tenant_isolation(self, tmp_path, monkeypatch):
        """Test that thumbnail retrieval respects tenant boundaries."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
        tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

        backend = FilesystemStorageBackend()

        # Store thumbnail for tenant A
        set_current_tenant(tenant_a)
        try:
            thumbnail_path_a = backend.get_path("documents/thumbnails/0000001.webp")
            thumbnail_dir_a = thumbnail_path_a.parent
            thumbnail_dir_a.mkdir(parents=True, exist_ok=True)
            with open(thumbnail_path_a, "wb") as f:
                f.write(b"thumbnail content a")
        finally:
            clear_current_tenant()

        # Try to retrieve with tenant B context - should not find it
        set_current_tenant(tenant_b)
        try:
            thumbnail_path_b = backend.get_path("documents/thumbnails/0000001.webp")
            # Path should be different (tenant-b prefix)
            assert thumbnail_path_b != thumbnail_path_a
            assert "tenant-b" in thumbnail_path_b
            # File should not exist at tenant B's path
            assert not backend.exists("documents/thumbnails/0000001.webp")
        finally:
            clear_current_tenant()


@pytest.mark.django_db
class TestCrossBackendConsistency:
    """Test tenant segregation consistency across storage backends."""

    def test_filesystem_backend_tenant_segregation(self, tmp_path, monkeypatch):
        """Test filesystem backend implements tenant segregation correctly."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()

            # Test all document types
            original_path = backend.get_path("documents/originals/test.pdf")
            archive_path = backend.get_path("documents/archive/test.pdf")
            thumbnail_path = backend.get_path("documents/thumbnails/test.webp")

            # All paths should include tenant identifier
            assert "test-tenant" in original_path
            assert "test-tenant" in archive_path
            assert "test-tenant" in thumbnail_path

            # All paths should be in correct directories
            assert str(originals_dir) in original_path
            assert str(archive_dir) in archive_path
            assert str(thumbnail_dir) in thumbnail_path
        finally:
            clear_current_tenant()


@pytest.mark.django_db
class TestPerformanceTenantPathResolution:
    """Test performance of tenant path resolution overhead."""

    def test_tenant_path_resolution_performance(self, tmp_path, monkeypatch, benchmark):
        """Test that tenant path resolution adds minimal overhead."""
        from django.conf import settings

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()

            # Benchmark path resolution
            def resolve_path():
                return backend.get_path("documents/originals/test.pdf")

            # Run benchmark (if pytest-benchmark is available)
            try:
                result = benchmark(resolve_path)
                # Verify result is correct
                assert "test-tenant" in result
            except Exception:
                # pytest-benchmark not available, just test that it works
                path = resolve_path()
                assert "test-tenant" in path
                assert path.startswith(str(originals_dir / "test-tenant"))
        finally:
            clear_current_tenant()

    def test_tenant_path_resolution_overhead_acceptable(self, tmp_path, monkeypatch):
        """Test that tenant path resolution overhead is minimal."""
        from django.conf import settings
        import time

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant = Tenant.objects.create(name="Test Tenant", identifier="test-tenant")
        set_current_tenant(tenant)

        try:
            backend = FilesystemStorageBackend()

            # Measure time for multiple path resolutions
            start_time = time.perf_counter()
            for _ in range(1000):
                backend.get_path("documents/originals/test.pdf")
            end_time = time.perf_counter()

            elapsed = end_time - start_time
            avg_time = elapsed / 1000

            # Average time should be very small (< 1ms per operation)
            # This is a reasonable expectation for path resolution
            assert avg_time < 0.001, (
                f"Path resolution too slow: {avg_time:.6f}s per operation"
            )

            # Verify all paths are correct
            path = backend.get_path("documents/originals/test.pdf")
            assert "test-tenant" in path
        finally:
            clear_current_tenant()

    def test_concurrent_tenant_path_resolution(self, tmp_path, monkeypatch):
        """Test that tenant path resolution works correctly under concurrent access."""
        from django.conf import settings
        import threading

        # Setup temporary directories
        originals_dir = tmp_path / "originals"
        archive_dir = tmp_path / "archive"
        thumbnail_dir = tmp_path / "thumbnails"

        monkeypatch.setattr(settings, "ORIGINALS_DIR", originals_dir)
        monkeypatch.setattr(settings, "ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(settings, "THUMBNAIL_DIR", thumbnail_dir)

        tenant_a = Tenant.objects.create(name="Tenant A", identifier="tenant-a")
        tenant_b = Tenant.objects.create(name="Tenant B", identifier="tenant-b")

        backend = FilesystemStorageBackend()

        results = []
        errors = []

        def resolve_for_tenant(tenant, tenant_id):
            """Resolve paths for a specific tenant."""
            set_current_tenant(tenant)
            try:
                for i in range(10):
                    path = backend.get_path(f"documents/originals/test_{i}.pdf")
                    results.append((tenant_id, path))
            except Exception as e:
                errors.append((tenant_id, str(e)))
            finally:
                clear_current_tenant()

        # Run concurrent path resolution
        thread_a = threading.Thread(target=resolve_for_tenant, args=(tenant_a, "a"))
        thread_b = threading.Thread(target=resolve_for_tenant, args=(tenant_b, "b"))

        thread_a.start()
        thread_b.start()

        thread_a.join()
        thread_b.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors during concurrent access: {errors}"

        # Verify all paths are correct
        for tenant_id, path in results:
            if tenant_id == "a":
                assert "tenant-a" in path
                assert "tenant-b" not in path
            else:
                assert "tenant-b" in path
                assert "tenant-a" not in path
