# Implementation Plan: Multi-Tenancy Support

**Branch**: `001-multi-tenancy` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-tenancy/spec.md`

## Summary

Add multi-tenancy support to Paperless-ngx with logical data isolation using tenant_id, tenant selection UI, and super admin tenant management. The system will support multiple tenants in a shared database, with all tenant-specific data automatically scoped to the current tenant context. Users can select their tenant upon login or during their session, and super admin users can manage tenants through a dedicated interface. This is a fresh installation feature - no migration paths for existing data are required.

## Technical Context

**Language/Version**: Python 3.10-3.14 (minimum 3.10) - existing
**Primary Dependencies**: Django 5.2+, Django REST Framework 3.16, Celery 5.5.1, Redis 5.2.1, Angular/TypeScript - existing
**Storage**: PostgreSQL or MariaDB for database - existing
**Testing**: pytest 8.4.1 with pytest-django, pytest-cov for coverage reporting - existing
**Target Platform**: Linux server (Docker-based deployment recommended) - existing
**Project Type**: Web application (backend + frontend) - existing

**Multi-Tenancy Approach**: Shared database with logical separation via tenant_id column
**Tenant Identification**: X-Tenant-ID request header (verified against user's tenant association)
**Query Filtering**: Automatic tenant filtering via TenantManager with thread-local context
**Super Admin Role**: Django's is_superuser flag for tenant management access
**Fresh Installation**: No migration paths required - system starts with empty database

**Performance Goals**:
- Query performance within 10% of single-tenant baseline
- Support at least 50 concurrent tenants with isolated operations
- Tenant selection UI loads within 2 seconds
- Zero cross-tenant data leakage

**Constraints**:
- Fresh installation only (no existing data migration)
- All tenant-specific models must include tenant_id
- Unique constraints must include tenant_id
- Celery tasks must receive tenant_id explicitly
- API version 10 required for multi-tenancy features

**Scale/Scope**:
- Support for 50+ concurrent tenants
- All existing tenant-specific models (Document, Tag, Correspondent, DocumentType, StoragePath, CustomField, etc.)
- Frontend tenant selection and management UI
- Super admin tenant management screen

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Paperless-ngx Constitution principles:

- **API Versioning (I)**: ✅ COMPLIANT - New API version 10 required for multi-tenancy features. Versions 1-9 remain unchanged for backward compatibility. Version 10 introduces X-Tenant-ID header requirement and tenant-scoped responses. Existing single-tenant deployments can continue using versions 1-9.

- **Testing & Code Quality (II)**: ✅ COMPLIANT - Comprehensive tests required for data isolation, tenant context management, and super admin functionality. Tests must verify zero cross-tenant data leakage. Code must pass ruff formatting and mypy type checking.

- **Security & Privacy (III)**: ✅ COMPLIANT - Data isolation is critical security requirement. All tenant-specific data access must be scoped to tenant context. Super admin access must be properly restricted. Security considerations documented in requirements.

- **Community-Driven (IV)**: ✅ COMPLIANT - This feature extends the core system with multi-tenancy capabilities. Implementation follows established patterns and builds upon existing infrastructure.

- **Django/DRF Best Practices (V)**: ✅ COMPLIANT - Uses Django models with TenantModel base class, DRF viewsets for tenant management, middleware for tenant context, and Django's is_superuser for admin access. Follows established Django patterns for multi-tenancy.

- **Documentation (VI)**: ✅ COMPLIANT - API endpoints documented via DRF Spectacular. Tenant management endpoints documented. User-facing changes (tenant selection UI, super admin screen) require documentation updates.

**Status**: All constitution checks pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-tenancy/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entity relationships)
├── quickstart.md        # Phase 1 output (getting started guide)
└── contracts/           # Phase 1 output (API contracts)
    └── api-endpoints.md # Tenant management API endpoints
```

### Source Code (repository root)

```text
src/
├── paperless/
│   ├── tenants/         # Tenant management app (existing, to be enhanced)
│   │   ├── models.py    # Tenant, TenantModel, UserProfile (existing)
│   │   ├── managers.py # TenantManager, TenantQuerySet (existing)
│   │   ├── utils.py     # Thread-local tenant context (existing)
│   │   ├── middleware.py # TenantMiddleware (existing, may need updates)
│   │   ├── views.py     # TenantViewSet for super admin (NEW)
│   │   ├── serialisers.py # TenantSerializer (NEW)
│   │   └── permissions.py # SuperAdminPermission (NEW)
│   ├── settings.py      # Add tenant app, update API versioning
│   └── urls.py          # Add tenant management routes
├── documents/           # Core document management app
│   ├── models.py        # All models extend TenantModel (existing)
│   ├── views.py         # Update to ensure tenant context (verify)
│   └── tasks.py         # Update Celery tasks to accept tenant_id (NEW)
└── paperless_mail/      # Email processing app
    └── models.py        # MailAccount, MailRule extend TenantModel (verify)

src-ui/                  # Angular frontend
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── tenant-selector/  # NEW: Tenant selection component
│   │   │   └── tenant-management/ # NEW: Super admin tenant management
│   │   ├── services/
│   │   │   ├── tenant.service.ts  # NEW: Tenant API service
│   │   │   └── tenant-context.service.ts # NEW: Tenant context management
│   │   ├── interceptors/
│   │   │   └── tenant.interceptor.ts # NEW: Add X-Tenant-ID header
│   │   └── guards/
│   │       └── super-admin.guard.ts # NEW: Super admin route guard
│   └── environments/
│       └── environment.prod.ts # Update API version to 10
```

**Structure Decision**: Web application structure with Django backend (`src/`) and Angular frontend (`src-ui/`). Tenant management functionality extends existing `paperless.tenants` app. Frontend adds new components and services for tenant selection and management. All existing tenant-specific models already extend TenantModel (from existing implementation).

## Complexity Tracking

> **No violations** - Implementation follows constitution principles and builds upon existing tenant infrastructure. All complexity is justified by multi-tenancy requirements.

## Phase 0: Research Complete ✅

**Status**: Completed 2025-01-27

All technology decisions documented in `research.md`:
- Multi-tenancy architecture: Shared database with logical separation (existing)
- Tenant context: Thread-local storage with middleware (existing)
- Query filtering: Automatic via TenantManager (existing)
- Super admin: Django's is_superuser flag
- API tenant identification: X-Tenant-ID header
- Frontend context: Angular service with HTTP interceptor
- Unique constraints: Composite with tenant_id
- Celery tasks: Explicit tenant_id parameter
- Fresh installation: No migration paths required

All decisions leverage existing infrastructure. No clarification needed.

## Phase 1: Design Complete ✅

**Status**: Completed 2025-01-27

**Generated Artifacts**:
- ✅ `data-model.md`: Complete tenant entity relationships and data isolation rules
- ✅ `contracts/api-endpoints.md`: Tenant management API endpoints documentation
- ✅ `quickstart.md`: Fresh installation and user workflow guide

**Data Model**: Documented Tenant, UserProfile, TenantContext, and TenantModel with relationships, validation rules, and data isolation mechanisms.

**API Contracts**: Documented tenant management endpoints (CRUD, activate/deactivate) and modified existing endpoints for version 10.

**Quickstart**: Comprehensive guide for fresh installation, tenant creation, user workflows, and troubleshooting.

## Next Steps

This plan is ready for task breakdown:
1. Use `/speckit.tasks` to break down implementation tasks
2. Follow constitution principles for all changes
3. Build upon existing tenant infrastructure
