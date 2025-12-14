# Implementation Plan: Multi-Identity Provider Authentication

**Branch**: `001-multi-idp-auth` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-idp-auth/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the existing Django-based authentication system to support Azure Entra ID (via OIDC/OAuth 2.0) alongside the existing database-driven authentication. The implementation will leverage django-allauth's existing social account infrastructure and OIDC provider support to integrate Azure Entra ID, while maintaining backward compatibility with existing database authentication. The solution will provide a unified login interface, automatic account linking, and seamless session management across both authentication methods.

**Implementation Approach**: Use `allauth.socialaccount.providers.openid_connect` for Azure Entra ID integration, leveraging existing OIDC infrastructure. Extend `CustomAccountAdapter` and `CustomSocialAccountAdapter` for account linking logic. No new database models required - uses existing django-allauth models (`SocialAccount`, `SocialToken`, `SocialApp`).

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10-3.14)
**Primary Dependencies**: Django ~5.2.5, django-allauth ~65.12.1 (with socialaccount and mfa), Django REST Framework ~3.16, drf-spectacular ~0.28
**Storage**: Existing Django database (PostgreSQL/MySQL/MariaDB/SQLite) - no new storage requirements
**Testing**: pytest with pytest-django, pytest-cov for coverage
**Target Platform**: Linux server (web application)
**Project Type**: Web application (Django backend + Angular frontend)
**Performance Goals**: Authentication requests complete within 5 seconds (per SC-001), 95% success rate for Azure Entra ID authentication (per SC-003)
**Constraints**: Must maintain backward compatibility with existing API authentication methods (Basic, Session, Token, Remote User). Must not break existing database authentication. Must handle Azure Entra ID unavailability gracefully without affecting database authentication.
**Scale/Scope**: Supports existing user base plus new Azure Entra ID users. No specific user limit - scales with Django's user model and session management.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Verify compliance with Paperless-ngx Constitution principles:

- **API Versioning (I)**: ✅ **PASS** - No new API version required. The feature extends existing session-based authentication mechanisms without changing API contracts. All existing API authentication methods (Basic, Session, Token, Remote User) remain fully functional. Azure Entra ID authentication integrates with the existing session-based authentication system, making it transparent to API clients.

- **Testing & Code Quality (II)**: ✅ **PASS** - Test requirements identified: Unit tests for authentication flows, integration tests for OIDC/OAuth 2.0 flows, tests for account linking logic, tests for error handling scenarios. Code will follow ruff formatting (line length 88) and mypy type checking requirements. Tests will be organized in `src/paperless/tests/` following existing patterns.

- **Security & Privacy (III)**: ✅ **PASS** - Security considerations documented: Token validation, secure storage of client secrets, HTTPS requirements, authentication event logging. Access controls leverage existing Django Guardian and permission system. No document data exposure - authentication only affects user identity, not document access patterns.

- **Community-Driven (IV)**: ✅ **PASS** - Feature leverages existing OIDC infrastructure already documented in `docs/advanced_usage.md`. The application already supports OIDC via django-allauth, and this feature extends that capability specifically for Azure Entra ID. Justification: Enterprise users require Azure Entra ID integration for organizational SSO, and the infrastructure (django-allauth OIDC provider) is already in place, making this a natural extension of existing capabilities.

- **Django/DRF Best Practices (V)**: ✅ **PASS** - Design follows django-allauth conventions and patterns. Uses existing `CustomAccountAdapter` and `CustomSocialAccountAdapter`. Leverages django-allauth's OIDC provider support. Database migrations will be backward-compatible (additive only - new fields/models, no breaking changes).

- **Documentation (VI)**: ✅ **PASS** - Configuration documentation required for Azure Entra ID setup. User-facing documentation updates needed for login interface changes. API documentation remains unchanged (no API changes). Will update `docs/configuration.md` and `docs/advanced_usage.md` with Azure Entra ID configuration examples.

Any violations must be justified in the Complexity Tracking section below.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── paperless/
│   ├── adapter.py              # Extend CustomAccountAdapter, CustomSocialAccountAdapter
│   ├── auth.py                 # May add Azure Entra ID-specific auth helpers
│   ├── settings.py             # Add Azure Entra ID configuration settings
│   ├── signals.py              # May add signals for account linking events
│   ├── urls.py                 # No changes (uses allauth URL patterns)
│   └── tests/
│       └── test_auth_azure.py  # New tests for Azure Entra ID authentication
│
src-ui/                          # Angular frontend
└── src/
    └── app/
        └── components/
            └── login/          # May update login component to show Azure option

docs/
├── configuration.md             # Add Azure Entra ID configuration section
└── advanced_usage.md           # Update OIDC section with Azure Entra ID example
```

**Structure Decision**: Django web application with existing django-allauth infrastructure. Changes are primarily configuration and adapter extensions rather than new modules. Frontend changes minimal (login UI updates). No new database models required - leverages django-allauth's SocialAccount model for account linking.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution principles are satisfied.

## Phase Completion Status

### Phase 0: Outline & Research ✅ COMPLETE

- **research.md**: Generated with all technical clarifications resolved
- **Key Decisions**:
  - Use `allauth.socialaccount.providers.openid_connect` for Azure Entra ID
  - Email-based account linking with `sub` claim fallback
  - Leverage Django's existing session framework
  - Use django-allauth's built-in token refresh
  - Follow existing configuration patterns

### Phase 1: Design & Contracts ✅ COMPLETE

- **data-model.md**: Generated documenting existing models (no schema changes)
- **contracts/README.md**: Generated documenting no API changes required
- **quickstart.md**: Generated with step-by-step configuration guide
- **Agent Context**: Updated via `update-agent-context.sh`

### Phase 2: Task Breakdown

**Status**: Pending `/speckit.tasks` command

This phase will break down the implementation into specific development tasks.
