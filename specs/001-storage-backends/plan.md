# Implementation Plan: Multiple Storage Backends

**Branch**: `001-storage-backends` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-storage-backends/spec.md`

**Note**: This plan documents the implementation approach for adding multiple storage backend support to Paperless-ngx, starting with Azure Blob Storage.

## Summary

The document management application currently uses direct file system access for storing documents, archives, and thumbnails. This feature introduces an abstract storage interface that allows switching between storage backends (filesystem and Azure Blob Storage) via environment variable configuration. The implementation will maintain backward compatibility by defaulting to filesystem storage, while providing a clean abstraction layer that enables future storage backends (S3, Google Cloud Storage) to be added easily. All existing document operations (upload, retrieval, deletion, archiving, thumbnail generation) will work seamlessly across all storage backends.

## Technical Context

**Language/Version**: Python 3.10-3.14 (minimum 3.10, per constitution)
**Primary Dependencies**: Django 5.2+, Django REST Framework 3.16, Azure Blob Storage client library (azure-storage-blob), Path operations (pathlib)
**Storage**: PostgreSQL or MariaDB for database metadata, abstract storage layer for documents/archives/thumbnails (filesystem or Azure Blob Storage)
**Testing**: pytest 8.4.1 with pytest-django, pytest-cov for coverage, pytest-mock for mocking storage backends
**Target Platform**: Linux server (Docker-based deployment recommended, consistent with existing Paperless-ngx deployment)
**Project Type**: Web application (backend Django app, no frontend changes required)
**Performance Goals**: Document upload within 30 seconds for files up to 100MB, retrieval within 5 seconds for typical documents, ≥99% operation success rate (per SC-002, SC-003)
**Constraints**: Must maintain backward compatibility with existing filesystem storage, no API changes required (internal implementation detail), must handle Azure connection failures gracefully, configuration validation at startup within 5 seconds (per SC-007)
**Scale/Scope**: Supports existing document base plus new documents stored in Azure Blob Storage, all document operations (upload via API/UI, consumption from watch folder, retrieval, deletion, archiving, thumbnail generation), extensible to future storage backends

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Verify compliance with Paperless-ngx Constitution principles:

- **API Versioning (I)**: ✅ **PASS** - No new API version required. The storage backend abstraction is an internal implementation detail. All existing API endpoints maintain identical request/response formats, authentication, and behavior. The storage backend change is transparent to API consumers. Spec explicitly states "No API migration required" and "API clients do not need any changes."

- **Testing & Code Quality (II)**: ✅ **PASS** - Test requirements identified: Unit tests for abstract storage interface, unit tests for filesystem backend, unit tests for Azure Blob Storage backend, integration tests for document operations across backends, tests for configuration validation, tests for error handling. Code will follow ruff formatting (line length 88) and mypy type checking requirements. Tests will be organized in `src/documents/tests/storage/` following existing patterns. Success criteria SC-005 requires "All existing automated tests pass for both filesystem and Azure Blob Storage backends."

- **Security & Privacy (III)**: ✅ **PASS** - Security considerations documented: Azure Blob Storage connection strings must be securely stored (environment variables), authentication follows Azure security best practices (connection strings or managed identities), access controls leverage existing Django Guardian and permission system. Document data access patterns remain unchanged - only storage location changes. No new security exposure introduced.

- **Community-Driven (IV)**: ✅ **PASS** - Feature addresses common community request for cloud storage support (Azure Blob Storage, with extensibility for S3, GCS). Storage backend abstraction is a foundational capability that enables future cloud storage integrations requested by the community. Justification: Enterprise and cloud-native deployments require cloud storage options beyond local filesystem, and the abstraction layer enables multiple storage providers without code duplication.

- **Django/DRF Best Practices (V)**: ✅ **PASS** - Design follows Django/DRF conventions: Abstract base class pattern for storage backends, Django settings for configuration, no database migrations required (storage paths remain as logical references in database), efficient file operations using appropriate patterns. Storage backend selection via environment variables follows existing Paperless-ngx configuration patterns.

- **Documentation (VI)**: ✅ **PASS** - No API endpoint changes, so no API documentation updates required. User-facing configuration changes (environment variables) will require documentation updates in `docs/` explaining how to configure storage backends. Storage backend abstraction will be documented in code with clear interface definitions.

**Status**: All constitution checks pass. No violations requiring justification.

**Post-Phase 1 Re-evaluation**: ✅ **PASS** - After Phase 1 design:
- API Versioning (I): ✅ Confirmed - No API changes, fully backward compatible
- Testing & Code Quality (II): ✅ Confirmed - Test structure defined in data-model.md, follows existing patterns
- Security & Privacy (III): ✅ Confirmed - Security considerations documented in research.md and data-model.md
- Community-Driven (IV): ✅ Confirmed - Feature addresses cloud storage community requests
- Django/DRF Best Practices (V): ✅ Confirmed - Design follows Django patterns, ABC interface, factory pattern
- Documentation (VI): ✅ Confirmed - Quickstart guide created, API contracts documented (no changes), configuration docs planned

## Project Structure

### Documentation (this feature)

```text
specs/001-storage-backends/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── documents/
│   ├── storage/                    # New: Storage backend abstraction
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract storage interface
│   │   ├── filesystem.py           # Filesystem backend implementation
│   │   ├── azure_blob.py           # Azure Blob Storage backend implementation
│   │   └── factory.py               # Storage backend factory/registry
│   ├── models.py                    # Document model (modify source_path, archive_path, thumbnail_path properties)
│   ├── consumer.py                  # ConsumerPlugin (modify _write method to use storage backend)
│   ├── views.py                     # API views (no changes, transparent to API)
│   └── tests/
│       ├── storage/                 # New: Storage backend tests
│       │   ├── __init__.py
│       │   ├── test_base.py         # Abstract interface tests
│       │   ├── test_filesystem.py   # Filesystem backend tests
│       │   ├── test_azure_blob.py   # Azure Blob Storage backend tests
│       │   └── test_factory.py      # Factory/registry tests
│       └── test_consumer.py         # Update: Consumer tests with storage backend mocks
├── paperless/
│   └── settings.py                  # Add storage backend configuration settings
└── [other apps unchanged]

docs/
└── administration.md                 # Update: Add storage backend configuration documentation
```

**Structure Decision**: Single Django project structure. Storage backend abstraction is implemented as a new module within the `documents` app (`src/documents/storage/`), following existing app organization patterns. Tests are organized in `src/documents/tests/storage/` mirroring the source structure. No frontend changes required as storage backend is transparent to API consumers.

## Complexity Tracking

No violations - all constitution checks pass. The storage backend abstraction is a clean, maintainable design that follows Django patterns and enables future extensibility without adding unnecessary complexity.
