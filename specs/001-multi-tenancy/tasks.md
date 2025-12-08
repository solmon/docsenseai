# Tasks: Multi-Tenancy Support

**Input**: Design documents from `/specs/001-multi-tenancy/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required per Constitution Principle II. All multi-tenancy changes must include comprehensive test coverage for data isolation, tenant context management, and super admin functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Django project**: `src/` at repository root
- **Angular frontend**: `src-ui/` at repository root
- **Models**: `src/[app]/models.py`
- **Migrations**: `src/[app]/migrations/`
- **Tests**: `src/[app]/tests/`
- **Frontend components**: `src-ui/src/app/components/`
- **Frontend services**: `src-ui/src/app/services/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and API version configuration

- [x] T001 Update API version configuration in `src/paperless/settings.py` to add version 10 to ALLOWED_VERSIONS
- [x] T002 [P] Update default API version to 10 in `src/paperless/settings.py` for fresh installations
- [x] T003 [P] Update frontend API version to 10 in `src-ui/src/environments/environment.prod.ts`
- [x] T004 [P] Update frontend API version to 10 in `src-ui/src/environments/environment.ts` (development)
- [x] T005 Verify TenantMiddleware is configured in MIDDLEWARE in `src/paperless/settings.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Tenant Infrastructure Verification

- [x] T006 Verify Tenant model exists and has all required fields in `src/paperless/tenants/models.py`
- [x] T007 Verify TenantModel abstract base class exists in `src/paperless/tenants/models.py`
- [x] T008 Verify TenantManager and TenantQuerySet exist in `src/paperless/tenants/managers.py`
- [x] T009 Verify thread-local tenant context utilities exist in `src/paperless/tenants/utils.py`
- [x] T010 Verify TenantMiddleware exists and handles X-Tenant-ID header in `src/paperless/tenants/middleware.py`
- [x] T011 Verify UserProfile model exists and associates users with tenants in `src/paperless/tenants/models.py`
- [x] T012 Verify all tenant-specific models (Document, Tag, Correspondent, etc.) extend TenantModel in `src/documents/models.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Tenant Selection and Context Management (Priority: P1) 🎯 MVP

**Goal**: Users can select their tenant upon login or during their session, and all subsequent data access and operations are automatically scoped to the selected tenant.

**Independent Test**: Log in as a user associated with a tenant, select the tenant, verify all API requests include the tenant context and all data returned is scoped to that tenant.

### Tests for User Story 1

- [x] T013 [P] [US1] Create unit test for TenantContextService in `src-ui/src/app/services/tenant-context.service.spec.ts`
- [x] T014 [P] [US1] Create unit test for TenantInterceptor in `src-ui/src/app/interceptors/tenant.interceptor.spec.ts`
- [x] T015 [P] [US1] Create unit test for TenantSelectorComponent in `src-ui/src/app/components/tenant-selector/tenant-selector.component.spec.ts`
- [x] T016 [P] [US1] Create integration test for tenant selection flow in `src-ui/src/app/components/tenant-selector/tenant-selector.integration.spec.ts`
- [x] T017 [P] [US1] Create backend test for tenant context in API requests in `src/paperless/tenants/tests/test_api_tenant_endpoints.py`

### Implementation for User Story 1

- [x] T018 [P] [US1] Create TenantContextService in `src-ui/src/app/services/tenant-context.service.ts` to manage current tenant selection
- [x] T019 [P] [US1] Create TenantInterceptor in `src-ui/src/app/interceptors/tenant.interceptor.ts` to add X-Tenant-ID header to all HTTP requests
- [x] T020 [P] [US1] Create TenantSelectorComponent in `src-ui/src/app/components/tenant-selector/tenant-selector.component.ts`
- [x] T021 [P] [US1] Create TenantSelectorComponent template in `src-ui/src/app/components/tenant-selector/tenant-selector.component.html`
- [x] T022 [P] [US1] Create TenantSelectorComponent styles in `src-ui/src/app/components/tenant-selector/tenant-selector.component.scss`
- [x] T023 [US1] Create TenantService in `src-ui/src/app/services/tenant.service.ts` to interact with tenant API endpoints
- [x] T024 [US1] Register TenantInterceptor in HTTP interceptor providers in `src-ui/src/app/app.config.ts` or `src-ui/src/app/app.module.ts`
- [x] T025 [US1] Integrate TenantSelectorComponent into login flow or app initialization in `src-ui/src/main.ts` (app initializer)
- [x] T026 [US1] Update TenantMiddleware to handle X-Tenant-ID header validation in `src/paperless/tenants/middleware.py` (already handles X-Tenant-ID header)
- [x] T027 [US1] Add endpoint to get current user's tenant in `src/paperless/views.py` (GET /api/profile/tenant/)
- [x] T028 [US1] Add endpoint to get user's associated tenants in `src/paperless/views.py` (GET /api/users/{id}/tenants/)
- [x] T029 [US1] Persist tenant selection in sessionStorage in TenantContextService
- [x] T030 [US1] Implement automatic tenant assignment when user has single tenant in TenantContextService
- [ ] T031 [US1] Add tenant selection to user menu/dropdown for switching tenants during session

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can select tenants and all API requests include tenant context.

---

## Phase 4: User Story 2 - Super Admin Tenant Management (Priority: P1)

**Goal**: Super admin users can manage tenants through a dedicated screen, performing CRUD operations to view, create, update, activate, and deactivate tenants.

**Independent Test**: Log in as a super admin, access the tenant management screen, create a new tenant, verify it appears in the list, activate/deactivate it, and verify the changes take effect.

### Tests for User Story 2

- [ ] T032 [P] [US2] Create unit test for TenantSerializer in `src/paperless/tenants/tests/test_serializers.py`
- [ ] T033 [P] [US2] Create unit test for TenantViewSet in `src/paperless/tenants/tests/test_views.py`
- [ ] T034 [P] [US2] Create unit test for SuperAdminPermission in `src/paperless/tenants/tests/test_permissions.py`
- [ ] T035 [P] [US2] Create API contract test for tenant management endpoints in `src/paperless/tenants/tests/test_api_contracts.py`
- [ ] T036 [P] [US2] Create unit test for TenantManagementComponent in `src-ui/src/app/components/tenant-management/tenant-management.component.spec.ts`
- [ ] T037 [P] [US2] Create integration test for tenant CRUD operations in `src-ui/src/app/components/tenant-management/tenant-management.integration.spec.ts`

### Implementation for User Story 2

- [x] T038 [P] [US2] Create TenantSerializer in `src/paperless/tenants/serializers.py` with fields: id, name, identifier, is_active, deleted_at, created_at, updated_at
- [x] T039 [P] [US2] Create SuperAdminPermission in `src/paperless/tenants/permissions.py` to check is_superuser flag
- [x] T040 [P] [US2] Create TenantViewSet in `src/paperless/tenants/views.py` with list, retrieve, create, update, destroy actions
- [x] T041 [US2] Add activate action to TenantViewSet in `src/paperless/tenants/views.py` (POST /api/tenants/{id}/activate/)
- [x] T042 [US2] Add deactivate action to TenantViewSet in `src/paperless/tenants/views.py` (POST /api/tenants/{id}/deactivate/)
- [x] T043 [US2] Add filtering and search to TenantViewSet in `src/paperless/tenants/views.py` (is_active, search by name/identifier)
- [x] T044 [US2] Add pagination to TenantViewSet in `src/paperless/tenants/views.py`
- [x] T045 [US2] Register tenant management routes in `src/paperless/urls.py` (api/tenants/)
- [x] T046 [P] [US2] Create TenantManagementComponent in `src-ui/src/app/components/tenant-management/tenant-management.component.ts`
- [x] T047 [P] [US2] Create TenantManagementComponent template in `src-ui/src/app/components/tenant-management/tenant-management.component.html`
- [x] T048 [P] [US2] Create TenantManagementComponent styles in `src-ui/src/app/components/tenant-management/tenant-management.component.scss`
- [x] T049 [US2] Create TenantFormComponent for create/edit tenant in `src-ui/src/app/components/tenant-management/tenant-edit-dialog.component.ts`
- [x] T050 [US2] Create TenantFormComponent template in `src-ui/src/app/components/tenant-management/tenant-edit-dialog.component.html`
- [x] T051 [US2] Add tenant list display with status (active/inactive) in TenantManagementComponent
- [x] T052 [US2] Add create tenant functionality in TenantManagementComponent
- [x] T053 [US2] Add edit tenant functionality in TenantManagementComponent
- [x] T054 [US2] Add activate/deactivate tenant functionality in TenantManagementComponent
- [x] T055 [US2] Add soft delete tenant functionality in TenantManagementComponent
- [x] T056 [US2] Create SuperAdminGuard in `src-ui/src/app/guards/super-admin.guard.ts` to protect tenant management routes
- [x] T057 [US2] Add route for tenant management screen in `src-ui/src/app/app-routing.module.ts`
- [ ] T058 [US2] Add navigation link to tenant management in settings menu (only visible to super admin)
- [x] T059 [US2] Update TenantService to include all CRUD methods in `src-ui/src/app/services/tenant.service.ts`
- [x] T060 [US2] Add session invalidation logic when tenant is deactivated in `src/paperless/tenants/views.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Super admin can manage tenants through the UI.

---

## Phase 5: User Story 3 - Data Isolation and Tenant Scoping (Priority: P1)

**Goal**: All tenant-specific data operations are automatically scoped to the current tenant context, ensuring complete logical data isolation within a shared database.

**Independent Test**: Create documents in Tenant A, switch to Tenant B, verify Tenant B cannot see Tenant A's documents, and verify all queries automatically filter by tenant ID.

### Tests for User Story 3

- [ ] T061 [P] [US3] Create test for data isolation in document queries in `src/documents/tests/test_tenant_isolation.py`
- [ ] T062 [P] [US3] Create test for data isolation in tag queries in `src/documents/tests/test_tenant_isolation.py`
- [ ] T063 [P] [US3] Create test for data isolation in correspondent queries in `src/documents/tests/test_tenant_isolation.py`
- [ ] T064 [P] [US3] Create test for cross-tenant access prevention in `src/documents/tests/test_tenant_isolation.py`
- [ ] T065 [P] [US3] Create test for bulk operations tenant scoping in `src/documents/tests/test_tenant_isolation.py`
- [ ] T066 [P] [US3] Create test for foreign key tenant consistency in `src/documents/tests/test_tenant_isolation.py`
- [ ] T067 [P] [US3] Create test for unique constraint tenant scoping in `src/documents/tests/test_tenant_isolation.py`

### Implementation for User Story 3

- [ ] T068 [US3] Verify all Celery tasks that process tenant-specific data accept tenant_id parameter in `src/documents/tasks.py`
- [ ] T069 [US3] Update index_reindex task to accept tenant_id parameter in `src/documents/tasks.py`
- [ ] T070 [US3] Update empty_trash task to accept tenant_id parameter in `src/documents/tasks.py`
- [ ] T071 [US3] Verify all task invocations pass tenant_id from current context in `src/documents/views.py` and related files
- [ ] T072 [US3] Add validation to prevent cross-tenant foreign key relationships in model clean() methods in `src/documents/models.py`
- [ ] T073 [US3] Verify all unique constraints include tenant_id in `src/documents/models.py` (Document, Tag, Correspondent, DocumentType, StoragePath, CustomField)
- [ ] T074 [US3] Add composite database indexes for tenant_id + commonly queried fields in migrations
- [ ] T075 [US3] Verify TenantManager raises error when tenant context not set in `src/paperless/tenants/managers.py`
- [ ] T076 [US3] Add logging for tenant context operations in `src/paperless/tenants/middleware.py`
- [ ] T077 [US3] Verify all API viewsets use TenantManager for tenant-specific models in `src/documents/views.py`
- [ ] T078 [US3] Add error handling for missing tenant context in API responses
- [ ] T079 [US3] Verify MailAccount and MailRule models extend TenantModel if tenant-scoped in `src/paperless_mail/models.py`
- [ ] T080 [US3] Add security test to verify zero cross-tenant data leakage in `src/paperless/tenants/tests/test_security.py`

**Checkpoint**: All user stories should now be independently functional. Data isolation is enforced with zero cross-tenant data leakage.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T081 [P] Documentation updates in `docs/` for multi-tenancy features (per Constitution Principle VI)
- [ ] T082 [P] API documentation updates (DRF Spectacular schema) for tenant management endpoints in `src/paperless/tenants/views.py`
- [ ] T083 Code cleanup and refactoring across tenant-related code
- [ ] T084 Run ruff formatter and fix formatting issues in `src/paperless/tenants/` (per Constitution Principle II)
- [ ] T085 Run ruff formatter and fix formatting issues in `src-ui/src/app/components/tenant-*` (per Constitution Principle II)
- [ ] T086 Run mypy type checking and fix type errors in `src/paperless/tenants/` (per Constitution Principle II)
- [ ] T087 Run mypy type checking and fix type errors in `src-ui/src/app/components/tenant-*` (per Constitution Principle II)
- [ ] T088 Run pytest with coverage reporting for all tenant-related tests (per Constitution Principle II)
- [ ] T089 Performance optimization for tenant filtering queries
- [ ] T090 [P] Additional unit tests in `src/paperless/tenants/tests/` for edge cases (required per Constitution Principle II)
- [ ] T091 [P] Additional unit tests in `src-ui/src/app/components/tenant-*/` for edge cases (required per Constitution Principle II)
- [ ] T092 Security review for tenant data isolation (per Constitution Principle III)
- [ ] T093 Run quickstart.md validation to ensure all steps work correctly
- [ ] T094 Add error messages and user feedback for tenant-related errors
- [ ] T095 Verify all API endpoints return appropriate error codes for tenant-related issues
- [ ] T096 Add monitoring/logging for tenant operations (tenant creation, activation, deactivation)
- [ ] T097 Update frontend translations for tenant-related UI text in `src-ui/messages.xlf`
- [ ] T098 Verify backward compatibility with API versions 1-9 (no tenant filtering applied)
- [ ] T099 Final review of all documentation for consistency
- [ ] T100 Final code review for adherence to Django/DRF best practices

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run in parallel with US1)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 for tenant context infrastructure, but can be partially implemented in parallel

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Services before components (frontend)
- Serializers before viewsets (backend)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational verification tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start in parallel
- All tests for a user story marked [P] can run in parallel
- Frontend and backend tasks within a story can run in parallel (different files)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create unit test for TenantContextService in src-ui/src/app/services/tenant-context.service.spec.ts"
Task: "Create unit test for TenantInterceptor in src-ui/src/app/interceptors/tenant.interceptor.spec.ts"
Task: "Create unit test for TenantSelectorComponent in src-ui/src/app/components/tenant-selector/tenant-selector.component.spec.ts"
Task: "Create backend test for tenant context in API requests in src/paperless/tenants/tests/test_middleware.py"

# Launch all frontend components for User Story 1 together:
Task: "Create TenantContextService in src-ui/src/app/services/tenant-context.service.ts"
Task: "Create TenantInterceptor in src-ui/src/app/interceptors/tenant.interceptor.ts"
Task: "Create TenantSelectorComponent in src-ui/src/app/components/tenant-selector/tenant-selector.component.ts"
Task: "Create TenantService in src-ui/src/app/services/tenant.service.ts"
```

---

## Parallel Example: User Story 2

```bash
# Launch all backend tests for User Story 2 together:
Task: "Create unit test for TenantSerializer in src/paperless/tenants/tests/test_serializers.py"
Task: "Create unit test for TenantViewSet in src/paperless/tenants/tests/test_views.py"
Task: "Create unit test for SuperAdminPermission in src/paperless/tenants/tests/test_permissions.py"

# Launch all backend implementation for User Story 2 together:
Task: "Create TenantSerializer in src/paperless/tenants/serializers.py"
Task: "Create SuperAdminPermission in src/paperless/tenants/permissions.py"
Task: "Create TenantViewSet in src/paperless/tenants/views.py"

# Launch all frontend components for User Story 2 together:
Task: "Create TenantManagementComponent in src-ui/src/app/components/tenant-management/tenant-management.component.ts"
Task: "Create TenantFormComponent for create/edit tenant in src-ui/src/app/components/tenant-management/tenant-form.component.ts"
Task: "Create SuperAdminGuard in src-ui/src/app/guards/super-admin.guard.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Frontend focus)
   - Developer B: User Story 2 (Backend + Frontend)
   - Developer C: User Story 3 (Backend verification + tests)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All existing tenant infrastructure (TenantModel, TenantManager, middleware) is already in place
- Focus on frontend UI, backend API endpoints, and verification/updates to existing infrastructure
- Fresh installation - no migration tasks needed

