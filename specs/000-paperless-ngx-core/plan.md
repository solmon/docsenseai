# Implementation Plan: Paperless-ngx Core Document Management System

**Branch**: `dev` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/000-paperless-ngx-core/spec.md`

**Note**: This plan documents the current implementation structure of Paperless-ngx based on codebase analysis.

## Summary

Paperless-ngx is a comprehensive document management system that transforms physical documents into a searchable digital archive. The system supports multiple document ingestion channels (web UI, consumption folder, email, API), automatic OCR and text extraction, full-text search, metadata management, workflow automation, and multi-user access with fine-grained permissions. The implementation uses Django 5.2+ with Django REST Framework for the backend API, Angular/TypeScript for the frontend, Celery for async task processing, and Whoosh for full-text search indexing.

## Technical Context

**Language/Version**: Python 3.10-3.14 (minimum 3.10)
**Primary Dependencies**: Django 5.2+, Django REST Framework 3.16, Celery 5.5.1, Redis 5.2.1, Whoosh-reloaded 2.7.5+, Angular/TypeScript
**Storage**: PostgreSQL or MariaDB for database, file-based storage for documents (with optional GPG encryption)
**Testing**: pytest 8.4.1 with pytest-django, pytest-cov for coverage reporting
**Target Platform**: Linux server (Docker-based deployment recommended)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: Parallel document processing on multi-core systems, sub-second search response times, efficient bulk operations (100+ documents)
**Constraints**: Documents stored in clear text by default (security consideration), API versioning required for backward compatibility, minimum 1-year support for deprecated API versions
**Scale/Scope**: Multi-user document archive with support for thousands of documents, 9 concurrent API versions, comprehensive permission system

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Verify compliance with Paperless-ngx Constitution principles:

- **API Versioning (I)**: ✅ COMPLIANT - Current implementation supports API versions 1-9 with explicit versioning via Accept header. Default version 1 for legacy compatibility. New versions added to ALLOWED_VERSIONS array.
- **Testing & Code Quality (II)**: ✅ COMPLIANT - Tests organized by app in `src/*/tests/`, pytest with coverage reporting, ruff formatting (line length 88), mypy type checking configured.
- **Security & Privacy (III)**: ✅ COMPLIANT - Document storage security considerations documented, Django Guardian for permissions, access controls enforced at API level.
- **Community-Driven (IV)**: ✅ COMPLIANT - This is the existing implementation, already established through community development process.
- **Django/DRF Best Practices (V)**: ✅ COMPLIANT - Uses Django models, DRF viewsets, serializers, signals, middleware following established patterns. Migrations are backward-compatible.
- **Documentation (VI)**: ✅ COMPLIANT - DRF Spectacular (OpenAPI) for API documentation, comprehensive user documentation in `docs/`, API versioning documented in `docs/api.md`.

**Status**: All constitution checks pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/000-paperless-ngx-core/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entity relationships)
├── quickstart.md        # Phase 1 output (getting started guide)
└── contracts/           # Phase 1 output (API contracts)
    └── openapi.yaml     # OpenAPI 3.0 schema
```

### Source Code (repository root)

```text
src/
├── documents/           # Core document management app
│   ├── models.py        # Document, Tag, Correspondent, DocumentType, etc.
│   ├── views.py         # API viewsets and endpoints
│   ├── serialisers.py   # DRF serializers
│   ├── tasks.py          # Celery tasks (consume_file, train_classifier)
│   ├── consumer.py      # Document consumption plugins
│   ├── parsers.py        # Document parsers (PDF, images, Office)
│   ├── index.py          # Whoosh search index management
│   ├── classifier.py    # ML-based automatic matching
│   ├── matching.py      # Rule-based matching algorithms
│   ├── permissions.py    # Permission classes
│   ├── filters.py        # Query filtering and search
│   ├── plugins/          # Consumption task plugins
│   ├── signals/          # Django signal handlers
│   └── tests/           # Test suite
├── paperless/           # Core application config
│   ├── settings.py       # Django settings
│   ├── urls.py          # URL routing
│   └── views.py         # Application views
├── paperless_mail/      # Email processing app
│   ├── models.py        # MailAccount, MailRule
│   ├── views.py         # Mail API endpoints
│   └── tasks.py         # Email processing tasks
├── paperless_tesseract/ # OCR integration
├── paperless_text/      # Text extraction
└── paperless_tika/      # Apache Tika integration (optional)

src-ui/                  # Angular frontend
├── src/
│   ├── app/
│   │   ├── components/  # UI components
│   │   ├── services/     # API service clients
│   │   └── data/         # TypeScript interfaces
│   └── environments/     # Environment configuration
└── messages.xlf         # Translation strings

tests/                   # Integration tests (if any)
docker/                  # Docker configuration
docs/                    # User documentation
```

**Structure Decision**: Web application structure with Django backend (`src/`) and Angular frontend (`src-ui/`). Backend organized by Django apps (documents, paperless_mail, etc.). Frontend is a single-page Angular application. Tests co-located with source code in each app's `tests/` directory.

## Complexity Tracking

> **No violations** - Current implementation follows constitution principles. All complexity is justified by feature requirements.

## Phase 0: Research Complete ✅

**Status**: Completed 2025-01-27

All technology decisions documented in `research.md`:

- Backend framework: Django 5.2+ with DRF
- Task queue: Celery with Redis
- Search: Whoosh
- Frontend: Angular/TypeScript
- Database: PostgreSQL/MariaDB
- Permissions: Django Guardian
- Architecture patterns: Plugin-based consumption, API versioning, matching algorithms

No clarification needed - all decisions are based on existing implementation.

## Phase 1: Design Complete ✅

**Status**: Completed 2025-01-27

**Generated Artifacts**:

- ✅ `data-model.md`: Complete entity relationship documentation
- ✅ `contracts/api-endpoints.md`: API endpoint documentation
- ✅ `quickstart.md`: User guide for getting started

**Data Model**: Documented 20+ entities with relationships, attributes, validation rules, and constraints.

**API Contracts**: Documented all major API endpoints with authentication, versioning, and example requests.

**Quickstart**: Comprehensive user guide covering all major workflows and features.

## Next Steps

This plan documents the current implementation. For new feature development:

1. Use `/speckit.tasks` to break down implementation tasks
2. Use `/speckit.checklist` to create domain-specific checklists
3. Follow constitution principles for all changes
