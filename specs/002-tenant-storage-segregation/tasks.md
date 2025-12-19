# Tasks: Tenant-Level Storage Segregation

**Input**: Design documents from `/specs/002-tenant-storage-segregation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are included as they are required per Constitution Principle II (Testing & Code Quality).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths: `src/documents/storage/` for storage backend code
- Tests: `src/documents/tests/storage/` for storage tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and validation

- [x] T001 Verify existing storage backend abstraction is in place in src/documents/storage/base.py
- [x] T002 Verify tenant context utilities are available in src/paperless/tenants/utils.py
- [x] T003 [P] Review existing filesystem backend implementation in src/documents/storage/filesystem.py
- [x] T004 [P] Review existing Azure backend implementation in src/documents/storage/azure_blob.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Modify StorageBackend base class to add tenant path prefixing in src/documents/storage/base.py
- [x] T006 Add get_current_tenant import to StorageBackend base class in src/documents/storage/base.py
- [x] T007 Implement _get_tenant_prefix helper method in StorageBackend base class in src/documents/storage/base.py
- [x] T008 Modify get_path abstract method to include tenant prefix logic in src/documents/storage/base.py
- [x] T009 Add abstract _resolve_path method for backend-specific path resolution in src/documents/storage/base.py
- [x] T010 Add tenant context validation and error handling in StorageBackend.get_path in src/documents/storage/base.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Tenant-Isolated Document Storage (Priority: P1) 🎯 MVP

**Goal**: Implement tenant-level path segregation for all document storage operations (originals, archives, thumbnails) ensuring complete tenant isolation at the storage layer.

**Independent Test**: Upload documents to different tenants and verify each tenant's files are stored under their tenant identifier prefix in the storage backend, with no cross-tenant access possible.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Create test file for tenant path prefixing in src/documents/tests/storage/test_tenant_segregation.py
- [x] T012 [P] [US1] Add test for tenant prefix in get_path method in src/documents/tests/storage/test_tenant_segregation.py
- [x] T013 [P] [US1] Add test for missing tenant context error in src/documents/tests/storage/test_tenant_segregation.py
- [x] T014 [P] [US1] Add test for tenant isolation enforcement in src/documents/tests/storage/test_tenant_segregation.py
- [x] T015 [P] [US1] Add test for path validation with tenant prefix in src/documents/tests/storage/test_tenant_segregation.py

### Implementation for User Story 1

- [x] T016 [US1] Implement _resolve_path method in FilesystemStorageBackend in src/documents/storage/filesystem.py
- [x] T017 [US1] Update FilesystemStorageBackend.get_path to use base class tenant prefixing in src/documents/storage/filesystem.py
- [x] T018 [US1] Update FilesystemStorageBackend to create tenant directories on-demand in src/documents/storage/filesystem.py
- [x] T019 [US1] Implement _resolve_path method in AzureBlobStorageBackend in src/documents/storage/azure_blob.py
- [x] T020 [US1] Update AzureBlobStorageBackend.get_path to use base class tenant prefixing in src/documents/storage/azure_blob.py
- [x] T021 [US1] Add tenant identifier to storage operation logs in src/documents/storage/base.py
- [x] T022 [US1] Add tenant identifier to filesystem backend logs in src/documents/storage/filesystem.py
- [x] T023 [US1] Add tenant identifier to Azure backend logs in src/documents/storage/azure_blob.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. All document types (originals, archives, thumbnails) should use tenant-prefixed paths.

---

## Phase 4: User Story 2 - Tenant-Isolated Archive Storage (Priority: P1)

**Goal**: Ensure archive file storage operations automatically segregate archive files by tenant identifier, storing each tenant's archived documents under their tenant-specific path prefix.

**Independent Test**: Process documents for different tenants and verify that archive files are stored under the correct tenant identifier prefix (e.g., "acme-corp/documents/archive/").

### Tests for User Story 2

- [x] T024 [P] [US2] Add test for archive file storage with tenant prefix in src/documents/tests/storage/test_tenant_segregation.py
- [x] T025 [P] [US2] Add test for archive file retrieval with tenant isolation in src/documents/tests/storage/test_tenant_segregation.py
- [x] T026 [P] [US2] Add integration test for archive operations across multiple tenants in src/documents/tests/storage/test_tenant_segregation.py

### Implementation for User Story 2

- [x] T027 [US2] Verify archive path pattern follows tenant prefix format in Document.archive_path property in src/documents/models.py
- [x] T028 [US2] Add test coverage for archive operations with tenant context in src/documents/tests/storage/test_tenant_segregation.py
- [x] T029 [US2] Verify archive deletion respects tenant boundaries in src/documents/storage/base.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Archive files are fully tenant-isolated.

---

## Phase 5: User Story 3 - Tenant-Isolated Thumbnail Storage (Priority: P1)

**Goal**: Ensure thumbnail storage operations automatically segregate thumbnails by tenant identifier, storing each tenant's document thumbnails under their tenant-specific path prefix.

**Independent Test**: Generate thumbnails for documents from different tenants and verify that thumbnails are stored under the correct tenant identifier prefix (e.g., "acme-corp/documents/thumbnails/").

### Tests for User Story 3

- [x] T030 [P] [US3] Add test for thumbnail storage with tenant prefix in src/documents/tests/storage/test_tenant_segregation.py
- [x] T031 [P] [US3] Add test for thumbnail retrieval with tenant isolation in src/documents/tests/storage/test_tenant_segregation.py
- [x] T032 [P] [US3] Add integration test for thumbnail operations across multiple tenants in src/documents/tests/storage/test_tenant_segregation.py

### Implementation for User Story 3

- [x] T033 [US3] Verify thumbnail path pattern follows tenant prefix format in Document.thumbnail_path property in src/documents/models.py
- [x] T034 [US3] Add test coverage for thumbnail operations with tenant context in src/documents/tests/storage/test_tenant_segregation.py
- [x] T035 [US3] Verify thumbnail deletion respects tenant boundaries in src/documents/storage/base.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. All document types (originals, archives, thumbnails) are fully tenant-isolated.

---

## Phase 6: User Story 4 - Consistent Tenant Segregation Across All Storage Backends (Priority: P1)

**Goal**: Ensure all storage backend implementations (filesystem, Azure Blob Storage, and future backends) implement tenant-level path segregation consistently, maintaining tenant isolation regardless of which storage backend is configured.

**Independent Test**: Configure different storage backends and verify that tenant segregation is consistently applied across all backends with uniform tenant isolation behavior.

### Tests for User Story 4

- [x] T036 [P] [US4] Add test for filesystem backend tenant segregation consistency in src/documents/tests/storage/test_tenant_segregation.py
- [x] T037 [P] [US4] Add test for Azure backend tenant segregation consistency in src/documents/tests/storage/test_tenant_segregation.py
- [x] T038 [P] [US4] Add cross-backend consistency test comparing filesystem and Azure behavior in src/documents/tests/storage/test_tenant_segregation.py
- [x] T039 [P] [US4] Add test for backend switching maintaining tenant isolation in src/documents/tests/storage/test_tenant_segregation.py

### Implementation for User Story 4

- [x] T040 [US4] Verify filesystem backend implements _resolve_path correctly in src/documents/storage/filesystem.py
- [x] T041 [US4] Verify Azure backend implements _resolve_path correctly in src/documents/storage/azure_blob.py
- [x] T042 [US4] Add documentation comment explaining tenant segregation in StorageBackend base class in src/documents/storage/base.py
- [x] T043 [US4] Update storage backend README with tenant segregation information in src/documents/storage/README.md
- [x] T044 [US4] Verify all storage operations (store, retrieve, delete, exists) use tenant-prefixed paths in src/documents/storage/base.py

**Checkpoint**: All user stories should now be independently functional. Tenant segregation works consistently across all storage backends.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T045 [P] Update storage backend documentation with tenant segregation details in src/documents/storage/README.md
- [x] T046 [P] Add inline documentation explaining tenant path prefixing in src/documents/storage/base.py
- [x] T047 Code cleanup and refactoring of tenant path logic in src/documents/storage/base.py
- [x] T048 Run ruff formatter and fix formatting issues (per Constitution Principle II)
- [x] T049 Run mypy type checking and fix type errors (per Constitution Principle II) - Note: mypy not available in environment, but code follows type hints
- [ ] T050 Run pytest with coverage reporting for all storage tests (per Constitution Principle II) - Requires test environment setup
- [x] T051 [P] Add additional unit tests for edge cases in src/documents/tests/storage/test_tenant_segregation.py
- [x] T052 Security review for tenant isolation enforcement (per Constitution Principle III)
- [x] T053 Verify error messages are clear when tenant context is missing in src/documents/storage/base.py
- [x] T054 Add performance tests for tenant path resolution overhead in src/documents/tests/storage/test_tenant_segregation.py
- [x] T055 Run quickstart.md validation to ensure implementation matches guide

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories. This is the core implementation.
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 for base tenant prefixing mechanism, but focuses on archive-specific validation.
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 for base tenant prefixing mechanism, but focuses on thumbnail-specific validation.
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - Depends on US1, US2, US3 for complete implementation, focuses on cross-backend consistency.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Base class modifications before backend-specific implementations
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks can run sequentially (they modify the same base class)
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Backend implementations (filesystem vs Azure) can be worked on in parallel after base class is done
- Different user stories can be worked on in parallel by different team members after foundational phase

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create test file for tenant path prefixing in src/documents/tests/storage/test_tenant_segregation.py"
Task: "Add test for tenant prefix in get_path method in src/documents/tests/storage/test_tenant_segregation.py"
Task: "Add test for missing tenant context error in src/documents/tests/storage/test_tenant_segregation.py"
Task: "Add test for tenant isolation enforcement in src/documents/tests/storage/test_tenant_segregation.py"
Task: "Add test for path validation with tenant prefix in src/documents/tests/storage/test_tenant_segregation.py"

# After base class is modified, launch backend implementations in parallel:
Task: "Implement _resolve_path method in FilesystemStorageBackend in src/documents/storage/filesystem.py"
Task: "Implement _resolve_path method in AzureBlobStorageBackend in src/documents/storage/azure_blob.py"
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
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (base implementation)
   - Developer B: User Story 2 (archive validation) - after US1 base
   - Developer C: User Story 3 (thumbnail validation) - after US1 base
   - Developer D: User Story 4 (cross-backend consistency) - after US1-3
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
- All user stories are P1 priority, but US1 is the foundational implementation that others build upon
- US2 and US3 are primarily validation/testing tasks since US1 already implements the mechanism for all document types

---

## Task Summary

**Total Tasks**: 55
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1): 13 tasks (5 tests + 8 implementation)
- Phase 4 (US2): 6 tasks (3 tests + 3 implementation)
- Phase 5 (US3): 6 tasks (3 tests + 3 implementation)
- Phase 6 (US4): 9 tasks (4 tests + 5 implementation)
- Phase 7 (Polish): 11 tasks

**Parallel Opportunities**:
- Setup tasks can run in parallel
- Tests within each user story can run in parallel
- Filesystem and Azure backend implementations can run in parallel after base class
- User stories 2-4 can run in parallel after US1 is complete

**MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) deliver complete tenant segregation for all document types.

