# Tasks: Multiple Storage Backends

**Input**: Design documents from `/specs/001-storage-backends/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are not included. Tests should be added during implementation per Constitution Principle II.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `src/` for Django backend
- Paths shown below follow the Django web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration setup

- [x] T001 Add azure-storage-blob dependency to pyproject.toml
- [x] T002 [P] Review existing file storage patterns in src/documents/models.py
- [x] T003 [P] Review existing file operations in src/documents/consumer.py
- [x] T004 [P] Review existing path handling in src/documents/models.py (source_path, archive_path, thumbnail_path properties)
- [x] T005 [P] Review existing settings configuration in src/paperless/settings.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create storage backend module directory structure: src/documents/storage/
- [x] T007 [P] Create abstract storage interface base class in src/documents/storage/base.py with methods: store(), retrieve(), delete(), exists(), get_path(), initialize()
- [x] T008 [P] Create storage backend factory/registry in src/documents/storage/factory.py with get_backend() function
- [x] T009 [P] Add storage backend configuration settings to src/paperless/settings.py (PAPERLESS_STORAGE_BACKEND, PAPERLESS_AZURE_CONNECTION_STRING, PAPERLESS_AZURE_CONTAINER_NAME)
- [x] T010 [P] Add storage backend configuration validation function in src/paperless/settings.py
- [x] T011 Add storage backend initialization in Django app ready() or settings module
- [x] T012 [P] Create get_storage_backend() helper function in src/documents/storage/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Configure Storage Backend via Environment Variables (Priority: P1) 🎯 MVP

**Goal**: Enable administrators to configure the document storage backend by setting environment variables, allowing selection between filesystem and Azure Blob Storage without modifying application code.

**Independent Test**: Set environment variables, restart the application, and verify that documents are stored and retrieved from the configured backend. This delivers the core value of storage backend selection.

### Implementation for User Story 1

- [x] T013 [US1] Implement filesystem storage backend class in src/documents/storage/filesystem.py extending base interface
- [x] T014 [US1] Implement filesystem backend store() method in src/documents/storage/filesystem.py
- [x] T015 [US1] Implement filesystem backend retrieve() method in src/documents/storage/filesystem.py
- [x] T016 [US1] Implement filesystem backend delete() method in src/documents/storage/filesystem.py
- [x] T017 [US1] Implement filesystem backend exists() method in src/documents/storage/filesystem.py
- [x] T018 [US1] Implement filesystem backend get_path() method in src/documents/storage/filesystem.py
- [x] T019 [US1] Implement filesystem backend initialize() method in src/documents/storage/filesystem.py
- [x] T020 [US1] Register filesystem backend in storage factory in src/documents/storage/factory.py
- [x] T021 [US1] Implement configuration validation for PAPERLESS_STORAGE_BACKEND in src/paperless/settings.py (valid values: 'filesystem', 'azure_blob')
- [x] T022 [US1] Implement default storage backend fallback to 'filesystem' when not specified in src/paperless/settings.py
- [x] T023 [US1] Add error handling for invalid storage backend configuration values in src/paperless/settings.py
- [x] T024 [US1] Update storage backend factory to instantiate filesystem backend based on configuration in src/documents/storage/factory.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Administrators can configure storage backend via environment variables, and filesystem backend is operational.

---

## Phase 4: User Story 2 - Configure Azure Blob Storage Connection (Priority: P1) 🎯 MVP

**Goal**: Enable administrators to provide connection strings and container names for Azure Blob Storage account, allowing secure connection to and use of Azure Blob Storage for document storage.

**Independent Test**: Provide Azure connection string and container name via environment variables, restart the application, and verify successful connection to Azure Blob Storage. This delivers secure access to cloud storage.

### Implementation for User Story 2

- [x] T025 [US2] Implement Azure Blob Storage backend class in src/documents/storage/azure_blob.py extending base interface
- [x] T026 [US2] Implement Azure backend initialization with connection string parsing in src/documents/storage/azure_blob.py
- [x] T027 [US2] Implement Azure backend store() method using BlobClient in src/documents/storage/azure_blob.py
- [x] T028 [US2] Implement Azure backend retrieve() method using BlobClient in src/documents/storage/azure_blob.py
- [x] T029 [US2] Implement Azure backend delete() method using BlobClient in src/documents/storage/azure_blob.py
- [x] T030 [US2] Implement Azure backend exists() method using BlobClient in src/documents/storage/azure_blob.py
- [x] T031 [US2] Implement Azure backend get_path() method (returns blob name) in src/documents/storage/azure_blob.py
- [x] T032 [US2] Implement Azure backend initialize() method with container creation if needed in src/documents/storage/azure_blob.py
- [x] T033 [US2] Add configuration validation for PAPERLESS_AZURE_CONNECTION_STRING in src/paperless/settings.py
- [x] T034 [US2] Add configuration validation for PAPERLESS_AZURE_CONTAINER_NAME in src/paperless/settings.py
- [x] T035 [US2] Implement error handling for missing Azure configuration when backend is 'azure_blob' in src/paperless/settings.py
- [x] T036 [US2] Implement error handling for invalid Azure connection string format in src/paperless/settings.py
- [x] T037 [US2] Implement error handling for Azure connection failures in src/documents/storage/azure_blob.py
- [x] T038 [US2] Register Azure Blob Storage backend in storage factory in src/documents/storage/factory.py
- [x] T039 [US2] Add logging for Azure Blob Storage operations in src/documents/storage/azure_blob.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Both filesystem and Azure Blob Storage backends are functional and configurable.

---

## Phase 5: User Story 3 - Seamless Document Operations Across Storage Backends (Priority: P1) 🎯 MVP

**Goal**: Ensure all existing document operations (upload, retrieval, deletion, archiving, thumbnail generation) function seamlessly regardless of the chosen storage backend, so users experience no difference in functionality when switching between storage backends.

**Independent Test**: Perform all document operations (upload, view, download, delete, archive, view thumbnails) with both filesystem and Azure Blob Storage backends, and verify identical behavior. This delivers functional parity across storage backends.

### Implementation for User Story 3

- [x] T040 [US3] Update Document.source_path property to return logical path string in src/documents/models.py
- [x] T041 [US3] Update Document.archive_path property to return logical path string in src/documents/models.py
- [x] T042 [US3] Update Document.thumbnail_path property to return logical path string in src/documents/models.py
- [x] T043 [US3] Update Document.source_file property to use storage backend retrieve() in src/documents/models.py
- [x] T044 [US3] Update Document.archive_file property to use storage backend retrieve() in src/documents/models.py
- [x] T045 [US3] Update Document.thumbnail_file property to use storage backend retrieve() in src/documents/models.py
- [x] T046 [US3] Update ConsumerPlugin._write() method to use storage backend store() in src/documents/consumer.py
- [x] T047 [US3] Update document upload operations to use storage backend in src/documents/consumer.py
- [x] T048 [US3] Update document deletion operations to use storage backend delete() in src/documents/views.py or appropriate deletion handler
- [x] T049 [US3] Update archive file storage to use storage backend store() in src/documents/consumer.py
- [x] T050 [US3] Update thumbnail storage to use storage backend store() in src/documents/consumer.py
- [x] T051 [US3] Update document retrieval operations to use storage backend retrieve() in src/documents/views.py
- [x] T052 [US3] Update thumbnail retrieval operations to use storage backend retrieve() in src/documents/views.py
- [x] T053 [US3] Update archive retrieval operations to use storage backend retrieve() in src/documents/views.py
- [x] T054 [US3] Update bulk operations to use storage backend for all affected documents in src/documents/bulk_edit.py
- [x] T055 [US3] Ensure path generation functions create logical paths (not absolute paths) in src/documents/models.py
- [x] T056 [US3] Update create_source_path_directory() calls to use storage backend initialize() if needed

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work together. All document operations work seamlessly across both storage backends.

---

## Phase 6: User Story 4 - Extensible Storage Backend Architecture (Priority: P2)

**Goal**: Ensure the storage backend architecture is abstract enough to allow for easy addition of other storage backends (e.g., S3, Google Cloud Storage) in the future, without major refactoring.

**Independent Test**: Create a new storage backend implementation following the abstract interface, configure it via environment variables, and verify all document operations work. This delivers architectural flexibility for future storage backends.

### Implementation for User Story 4

- [x] T057 [US4] Add comprehensive docstrings to abstract storage interface in src/documents/storage/base.py
- [x] T058 [US4] Add type hints to all abstract storage interface methods in src/documents/storage/base.py
- [x] T059 [US4] Create storage backend implementation guide/documentation in src/documents/storage/README.md
- [x] T060 [US4] Ensure factory pattern supports easy registration of new backends in src/documents/storage/factory.py
- [x] T061 [US4] Add example/stub for future storage backend implementation in src/documents/storage/example_backend.py (optional, for documentation)
- [x] T062 [US4] Verify all storage backends implement required interface methods correctly
- [x] T063 [US4] Add validation to ensure new backends conform to interface contract in src/documents/storage/factory.py

**Checkpoint**: At this point, all user stories are complete. The architecture is extensible and ready for future storage backend implementations.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final polish, error handling, logging, and documentation

- [x] T064 Add comprehensive error handling for storage backend failures across all operations
- [x] T065 Add logging for all storage backend operations with backend type identification in src/documents/storage/base.py
- [x] T066 Add error messages for storage quota limits and storage full scenarios
- [x] T067 Add error handling for network failures and timeouts in Azure backend in src/documents/storage/azure_blob.py
- [x] T068 Add retry logic for transient storage failures (leverage Azure SDK retry policies)
- [x] T069 Update documentation in docs/administration.md with storage backend configuration instructions
- [x] T070 Add inline code documentation explaining storage backend abstraction design decisions
- [x] T071 Verify all storage operations are thread-safe
- [x] T072 Add path validation to prevent directory traversal attacks in storage backends
- [x] T073 Ensure storage backend operations handle large files efficiently (streaming for Azure)
- [x] T074 Add monitoring/logging for storage backend health and performance

---

## Dependencies

### User Story Completion Order

1. **Phase 1 (Setup)**: Must complete before all other phases
2. **Phase 2 (Foundational)**: Must complete before any user story phases
3. **Phase 3 (US1)**: Can be implemented independently after Phase 2
4. **Phase 4 (US2)**: Requires Phase 2, can be implemented in parallel with Phase 3 after Phase 2
5. **Phase 5 (US3)**: Requires Phase 2, Phase 3, and Phase 4 (needs both backends implemented)
6. **Phase 6 (US4)**: Requires Phase 2, Phase 3, Phase 4, and Phase 5 (needs working system)
7. **Phase 7 (Polish)**: Requires all previous phases

### Parallel Execution Opportunities

**After Phase 2 completes**:
- Phase 3 (US1 - Filesystem backend) and Phase 4 (US2 - Azure backend) can be developed in parallel
- T013-T024 (filesystem implementation) can run in parallel with T025-T039 (Azure implementation)

**Within Phase 3**:
- T013-T019 (filesystem backend methods) can be implemented in parallel
- T020-T024 (configuration and factory) can be implemented in parallel with backend methods

**Within Phase 4**:
- T025-T032 (Azure backend methods) can be implemented in parallel
- T033-T039 (configuration and error handling) can be implemented in parallel with backend methods

**Within Phase 5**:
- T040-T045 (Document model property updates) can be implemented in parallel
- T046-T056 (Consumer and view updates) can be implemented in parallel after model updates

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Suggested MVP**: Phase 1 + Phase 2 + Phase 3 (US1 - Filesystem backend configuration)

This delivers:
- Storage backend abstraction infrastructure
- Filesystem backend implementation
- Configuration via environment variables
- Backward compatibility (defaults to filesystem)

**Why this MVP**:
- Enables testing of storage abstraction without external dependencies
- Validates configuration approach
- Maintains backward compatibility
- Provides foundation for Azure backend

### Incremental Delivery

1. **Increment 1 (MVP)**: Phase 1 + Phase 2 + Phase 3
   - Storage abstraction + filesystem backend
   - Configuration system
   - Backward compatible

2. **Increment 2**: Phase 4 (US2 - Azure backend)
   - Azure Blob Storage support
   - Cloud storage capability

3. **Increment 3**: Phase 5 (US3 - Document operations)
   - Full document operation support
   - Seamless backend switching

4. **Increment 4**: Phase 6 (US4 - Extensibility)
   - Architecture documentation
   - Extensibility validation

5. **Increment 5**: Phase 7 (Polish)
   - Error handling
   - Documentation
   - Production readiness

---

## Task Summary

- **Total Tasks**: 74
- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 7 tasks
- **Phase 3 (US1 - Configuration)**: 12 tasks
- **Phase 4 (US2 - Azure Connection)**: 15 tasks
- **Phase 5 (US3 - Document Operations)**: 17 tasks
- **Phase 6 (US4 - Extensibility)**: 7 tasks
- **Phase 7 (Polish)**: 11 tasks

### Tasks per User Story

- **US1 (Configure Storage Backend)**: 12 tasks (Phase 3)
- **US2 (Configure Azure Connection)**: 15 tasks (Phase 4)
- **US3 (Seamless Operations)**: 17 tasks (Phase 5)
- **US4 (Extensible Architecture)**: 7 tasks (Phase 6)

### Independent Test Criteria

- **US1**: Set environment variables, restart application, verify documents stored/retrieved from configured backend
- **US2**: Provide Azure connection string and container name, restart application, verify successful Azure connection
- **US3**: Perform all document operations (upload, view, download, delete, archive, thumbnails) with both backends, verify identical behavior
- **US4**: Create new storage backend implementation following interface, configure via environment variables, verify all operations work

### Parallel Opportunities

- **High Parallelism**: Phase 3 and Phase 4 can be developed in parallel after Phase 2
- **Medium Parallelism**: Within each phase, backend method implementations can be parallelized
- **Low Parallelism**: Phase 5 requires Phase 3 and Phase 4, Phase 6 requires all previous phases

---

## Notes

- All tasks follow the strict checklist format: `- [ ] T### [P?] [Story?] Description with file path`
- File paths are absolute or relative to repository root as specified
- Tests should be added during implementation per Constitution Principle II (Testing & Code Quality)
- All code must pass ruff formatting (line length 88) and mypy type checking
- Storage backend operations must be thread-safe
- Error handling and logging are critical for production readiness

