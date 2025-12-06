<!--
Sync Impact Report:
Version change: N/A → 1.0.0 (initial constitution)
Modified principles: N/A (all new)
Added sections: Core Principles, Technology Stack Requirements, Security & Privacy, Development Workflow, Governance
Removed sections: N/A
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section updated
  ✅ .specify/templates/spec-template.md - Aligned with testing and API versioning principles
  ✅ .specify/templates/tasks-template.md - Aligned with testing requirements
Follow-up TODOs: None
-->

# Paperless-ngx Constitution

## Core Principles

### I. API Versioning & Backward Compatibility (NON-NEGOTIABLE)

All REST API changes MUST maintain backward compatibility through explicit versioning. API versions are specified via HTTP `Accept` header (`application/json; version=N`). New API versions MUST be added to `ALLOWED_VERSIONS` in settings, with the most recent version appearing last. Older API versions MUST be supported for at least one year after a new version is released. Breaking changes require a new API version; existing versions MUST continue to serve compatible data even if the underlying model changes. Default version (when none specified) is version 1 for legacy client compatibility.

**Rationale**: Paperless-ngx serves as a document management system with external API clients. Breaking changes would disrupt user workflows and integrations. Versioning ensures long-term stability while allowing evolution.

### II. Testing & Code Quality (NON-NEGOTIABLE)

All code changes MUST include appropriate tests. Tests are executed via `pytest` in the `src/` directory with coverage reporting (HTML and XML). Code MUST pass automated formatting checks via `ruff` (line length 88, target Python 3.10+). Type checking via `mypy` with strict settings (disallow_untyped_defs, check_untyped_defs). All tests MUST pass before PR merge. Coverage reports help identify untested code paths.

**Rationale**: Paperless-ngx handles sensitive documents and complex document processing workflows. Comprehensive testing prevents regressions and ensures reliability. Automated quality checks maintain code consistency across the community-driven project.

### III. Security & Privacy Awareness

All code MUST acknowledge that Paperless-ngx stores sensitive documents (tax records, invoices, personal information) in clear text without encryption by default. Security considerations MUST be documented in code and PRs when handling document data. Features that expose document content MUST include appropriate access controls and permission checks. Security vulnerabilities MUST be reported via GitHub Security Advisory system.

**Rationale**: The README explicitly warns users about security implications. Code must reflect this awareness and prioritize secure handling of sensitive document data.

### IV. Community-Driven Feature Development

New features or enhancements MUST target existing feature requests with evidence of community interest and discussion (GitHub Discussions). PRs implementing features without this requirement may not be merged. Non-trivial PRs (features, large changes, breaking changes) require review by at least two team members from the appropriate team (backend, frontend, etc.). Changes MUST consider whether the majority of users will benefit; changes that only benefit a small subset should consider forking instead.

**Rationale**: Paperless-ngx is a community project with distributed responsibility. This process balances feature development with maintenance burden and ensures community alignment.

### V. Django & DRF Best Practices

Code MUST follow Django and Django REST Framework conventions and patterns. Use Django's built-in features (signals, middleware, model methods) appropriately. DRF serializers, viewsets, and permissions MUST follow established patterns. Database migrations MUST be backward-compatible when possible. Use Django's ORM efficiently (select_related, prefetch_related) to avoid N+1 queries.

**Rationale**: Consistency with Django/DRF patterns improves maintainability, leverages framework optimizations, and makes the codebase accessible to Django developers.

### VI. Documentation & API Specification

API endpoints MUST be documented via DRF Spectacular (OpenAPI schema). User-facing features MUST include documentation updates. Breaking API changes MUST be documented in `docs/api.md` with version changelog entries. Complex features SHOULD include inline documentation explaining design decisions.

**Rationale**: Comprehensive documentation supports community contributions and API client development. OpenAPI schema enables automated API client generation and testing.

## Technology Stack Requirements

**Python**: Minimum Python 3.10, supports 3.10-3.14. Code MUST be compatible with the supported Python versions.

**Dependencies**: Use `pyproject.toml` for dependency management via `uv`. Django version constraints MUST respect Django's non-semver policy (only patch versions guaranteed non-breaking). Optional dependencies (mariadb, postgres, webserver) MUST be clearly separated.

**Frontend**: Angular/TypeScript frontend in `src-ui/`. Frontend API version MUST match backend default API version in environment configuration.

**Testing**: pytest with pytest-django, pytest-cov for coverage. Tests MUST be organized by app (`src/documents/tests/`, `src/paperless_mail/tests/`, etc.).

**Code Formatting**: ruff for formatting and linting. Line length 88 characters. Force single-line imports via isort configuration.

## Security & Privacy

**Document Storage**: Documents are stored in clear text by default. Optional GPG encryption available but not default. This MUST be clearly communicated in documentation and code comments where relevant.

**Access Control**: Django Guardian used for object-level permissions. All document access MUST respect ownership and permission settings. API endpoints MUST enforce authentication and appropriate permissions.

**Security Reporting**: Security vulnerabilities MUST be reported via GitHub Security Advisory system, not public issues.

**Deployment Guidance**: Documentation MUST emphasize that Paperless-ngx should run on trusted hosts, preferably local servers with backups.

## Development Workflow

**Branching Strategy**: `main` branch reflects latest release with no functional changes between releases (documentation/README only). `dev` branch contains changes for next release. `feature-X` branches for experimental work. All PRs target `dev` branch.

**Code Review**: Automated checks (formatting, linting, tests) MUST pass. Non-trivial PRs require manual review by at least two team members from appropriate team. Reviewers check code quality, functionality completeness, and absence of side effects.

**Testing Workflow**: Run `pytest` in `src/` directory before submitting PR. Coverage reports generated automatically. HTML coverage reports available for inspection.

**Translation**: Frontend translations via Crowdin (`src-ui/messages.xlf`). Django admin translations via `django.po`. Translation changes automatically synced from Crowdin.

## Governance

This constitution supersedes all other development practices and guidelines. All PRs and code reviews MUST verify compliance with these principles. Amendments to this constitution require:

1. Documentation of the proposed change and rationale
2. Review and approval by project maintainers
3. Update to version number following semantic versioning:
   - **MAJOR**: Backward-incompatible governance changes or principle removals
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, wording improvements, typo fixes

Complexity that violates principles MUST be justified in PR descriptions with explanation of why simpler alternatives were insufficient.

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
