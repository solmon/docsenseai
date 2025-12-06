# Tasks: Paperless-ngx Core Document Management System

**Input**: Design documents from `/specs/000-paperless-ngx-core/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Note**: All tasks below are marked as complete (✅) as they represent the existing core implementation. This document establishes the baseline context for implementing add-on features.

**Organization**: Tasks are grouped by user story to show the implementation structure of each feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/` at repository root
- **Frontend**: `src-ui/` at repository root
- **Tests**: Co-located with source code in `src/*/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Django project structure with apps (documents, paperless, paperless_mail, etc.) in src/
- [x] T002 Initialize Django project with dependencies in pyproject.toml (Django 5.2+, DRF, Celery, etc.)
- [x] T003 [P] Configure ruff formatter and linting (line length 88, Python 3.10+) in pyproject.toml
- [x] T004 [P] Configure mypy type checking with strict settings in pyproject.toml
- [x] T005 [P] Setup pytest with pytest-django and pytest-cov in pyproject.toml
- [x] T006 [P] Initialize Angular frontend project in src-ui/ with TypeScript
- [x] T007 Configure Docker and docker-compose files in docker/
- [x] T008 Setup environment configuration management via environment variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Setup database schema and Django migrations framework in src/paperless/settings.py
- [x] T010 [P] Implement Django authentication system with User and Group models
- [x] T011 [P] Setup Django REST Framework with API routing in src/paperless/urls.py
- [x] T012 [P] Configure API versioning middleware in src/paperless/middleware.py (Accept header versioning)
- [x] T013 [P] Setup Celery task queue with Redis broker configuration in src/paperless/settings.py
- [x] T014 [P] Configure Django Guardian for object-level permissions in src/paperless/settings.py
- [x] T015 [P] Setup Whoosh search index infrastructure in src/documents/index.py
- [x] T016 Create base model classes (ModelWithOwner, MatchingModel, SoftDeleteModel) in src/documents/models.py
- [x] T017 Configure error handling and logging infrastructure
- [x] T018 Setup DRF Spectacular for OpenAPI documentation in src/paperless/settings.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Document Upload and Processing (Priority: P1) 🎯 MVP

**Goal**: Enable document upload through multiple channels (web UI, consumption folder, email, API) with automatic processing (OCR, text extraction, PDF/A conversion, metadata assignment)

**Independent Test**: Upload a PDF document via web UI and verify it appears in the document list with extracted text, thumbnail, and metadata.

### Implementation for User Story 1

- [x] T019 [P] [US1] Create Document model in src/documents/models.py with all metadata fields
- [x] T020 [P] [US1] Create Tag model in src/documents/models.py with hierarchical support
- [x] T021 [P] [US1] Create Correspondent model in src/documents/models.py
- [x] T022 [P] [US1] Create DocumentType model in src/documents/models.py
- [x] T023 [P] [US1] Create StoragePath model in src/documents/models.py
- [x] T024 [US1] Implement DocumentSerializer in src/documents/serialisers.py
- [x] T025 [US1] Implement DocumentViewSet with CRUD operations in src/documents/views.py
- [x] T026 [US1] Implement PostDocumentView for API upload in src/documents/views.py
- [x] T027 [US1] Create consume_file Celery task in src/documents/tasks.py
- [x] T028 [US1] Implement document consumption plugin system in src/documents/plugins/base.py
- [x] T029 [US1] Implement ConsumerPlugin for document processing in src/documents/consumer.py
- [x] T030 [US1] Implement document parsers (PDF, images, Office) in src/documents/parsers.py
- [x] T031 [US1] Implement OCR integration via Tesseract in src/paperless_tesseract/
- [x] T032 [US1] Implement PDF/A conversion in document processing pipeline
- [x] T033 [US1] Implement document consumer management command in src/documents/management/commands/document_consumer.py
- [x] T034 [US1] Implement file handling utilities in src/documents/file_handling.py
- [x] T035 [US1] Implement document thumbnail generation
- [x] T036 [US1] Implement frontend document upload component in src-ui/src/app/components/
- [x] T037 [US1] Implement frontend upload service in src-ui/src/app/services/
- [x] T038 [US1] Add document list view in frontend
- [x] T039 [US1] Add document detail view in frontend
- [x] T040 [US1] Implement duplicate detection via checksum validation

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Document Search and Discovery (Priority: P1)

**Goal**: Enable full-text search, filtering by metadata, and saved views for document discovery

**Independent Test**: Create a document, search for it by title, filter by tag, and verify results are returned correctly.

### Implementation for User Story 2

- [x] T041 [US2] Implement Whoosh search index schema in src/documents/index.py
- [x] T042 [US2] Implement document indexing after consumption in src/documents/signals/handlers.py
- [x] T043 [US2] Implement GlobalSearchView for full-text search in src/documents/views.py
- [x] T044 [US2] Implement SearchAutoCompleteView for search suggestions in src/documents/views.py
- [x] T045 [US2] Implement UnifiedSearchViewSet with query parameter support in src/documents/views.py
- [x] T046 [US2] Implement document filtering system in src/documents/filters.py
- [x] T047 [US2] Implement "more like this" similarity search functionality
- [x] T048 [US2] Create SavedView model in src/documents/models.py
- [x] T049 [US2] Create SavedViewFilterRule model in src/documents/models.py
- [x] T050 [US2] Implement SavedViewSerializer in src/documents/serialisers.py
- [x] T051 [US2] Implement SavedViewViewSet in src/documents/views.py
- [x] T052 [US2] Implement search result highlighting in API responses
- [x] T053 [US2] Implement relevance ranking for search results
- [x] T054 [US2] Implement frontend search component in src-ui/src/app/components/
- [x] T055 [US2] Implement frontend filter UI components
- [x] T056 [US2] Implement frontend saved views management UI
- [x] T057 [US2] Implement frontend document list with filtering and sorting

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Document Metadata Management (Priority: P1)

**Goal**: Enable assignment and management of metadata (tags, correspondents, document types, storage paths, custom fields) individually and in bulk

**Independent Test**: Create tags, correspondents, and document types, then assign them to documents individually and in bulk.

### Implementation for User Story 3

- [x] T058 [P] [US3] Implement TagViewSet with CRUD operations in src/documents/views.py
- [x] T059 [P] [US3] Implement CorrespondentViewSet in src/documents/views.py
- [x] T060 [P] [US3] Implement DocumentTypeViewSet in src/documents/views.py
- [x] T061 [P] [US3] Implement StoragePathViewSet in src/documents/views.py
- [x] T062 [US3] Implement nested tag hierarchy support in Tag model (parent relationship, max depth 5)
- [x] T063 [US3] Implement automatic parent tag assignment when child tag assigned in Document.add_nested_tags()
- [x] T064 [US3] Create CustomField model in src/documents/models.py with 10 data types
- [x] T065 [US3] Create CustomFieldInstance model in src/documents/models.py
- [x] T066 [US3] Implement CustomFieldSerializer in src/documents/serialisers.py
- [x] T067 [US3] Implement CustomFieldInstanceSerializer in src/documents/serialisers.py
- [x] T068 [US3] Implement CustomFieldViewSet in src/documents/views.py
- [x] T069 [US3] Implement custom field filtering in src/documents/filters.py (CustomFieldQueryParser)
- [x] T070 [US3] Implement BulkEditView for bulk document editing in src/documents/views.py
- [x] T071 [US3] Implement BulkEditObjectsView for bulk object operations in src/documents/views.py
- [x] T072 [US3] Implement bulk edit operations (modify_tags, modify_correspondent, etc.) in src/documents/bulk_edit.py
- [x] T073 [US3] Implement frontend metadata assignment UI components
- [x] T074 [US3] Implement frontend bulk selection and edit UI
- [x] T075 [US3] Implement frontend custom fields management UI
- [x] T076 [US3] Implement frontend nested tag hierarchy UI

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Automatic Matching and Classification (Priority: P2)

**Goal**: Automatically assign tags, correspondents, and document types using machine learning and rule-based matching

**Independent Test**: Train the classifier on existing documents, then upload a new document and verify automatic assignments match expected values.

### Implementation for User Story 4

- [x] T077 [US4] Implement matching algorithm system in MatchingModel base class
- [x] T078 [US4] Implement rule-based matching algorithms (any word, all words, exact, regex, fuzzy) in src/documents/matching.py
- [x] T079 [US4] Implement automatic matching algorithm using ML classifier in src/documents/classifier.py
- [x] T080 [US4] Implement train_classifier Celery task in src/documents/tasks.py
- [x] T081 [US4] Implement document suggestions endpoint in DocumentViewSet.suggestions() in src/documents/views.py
- [x] T082 [US4] Implement automatic metadata assignment via signals in src/documents/signals/handlers.py
- [x] T083 [US4] Implement matching rule evaluation for tags, correspondents, document types
- [x] T084 [US4] Implement frontend classifier training UI
- [x] T085 [US4] Implement frontend suggestions display UI
- [x] T086 [US4] Implement frontend matching rule configuration UI

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Document Sharing and Access Control (Priority: P2)

**Goal**: Enable document sharing via public links with expiration and fine-grained permission management

**Independent Test**: Create a share link for a document, access it via the public URL, and verify permissions are enforced.

### Implementation for User Story 5

- [x] T087 [US5] Create ShareLink model in src/documents/models.py with slug and expiration
- [x] T088 [US5] Implement ShareLinkSerializer in src/documents/serialisers.py
- [x] T089 [US5] Implement ShareLinkViewSet in src/documents/views.py
- [x] T090 [US5] Implement SharedLinkView for public access in src/documents/views.py
- [x] T091 [US5] Implement share link expiration validation
- [x] T092 [US5] Implement PaperlessObjectPermissions class in src/documents/permissions.py
- [x] T093 [US5] Apply object-level permissions to all document viewsets
- [x] T094 [US5] Implement permission filtering in ObjectOwnedOrGrantedPermissionsFilter
- [x] T095 [US5] Implement UserViewSet and GroupViewSet for user/group management in src/paperless/views.py
- [x] T096 [US5] Implement frontend share link creation UI
- [x] T097 [US5] Implement frontend permissions management UI
- [x] T098 [US5] Implement frontend user and group management UI

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Email Processing (Priority: P2)

**Goal**: Process emails from configured IMAP accounts, extract attachments, and consume as documents based on rules

**Independent Test**: Configure a mail account and rule, send a test email with attachment, verify the attachment is processed as a document.

### Implementation for User Story 6

- [x] T099 [US6] Create MailAccount model in src/paperless_mail/models.py
- [x] T100 [US6] Create MailRule model in src/paperless_mail/models.py
- [x] T101 [US6] Create ProcessedMail model for tracking in src/paperless_mail/models.py
- [x] T102 [US6] Implement MailAccountSerializer in src/paperless_mail/serialisers.py
- [x] T103 [US6] Implement MailRuleSerializer in src/paperless_mail/serialisers.py
- [x] T104 [US6] Implement MailAccountViewSet in src/paperless_mail/views.py
- [x] T105 [US6] Implement MailRuleViewSet in src/paperless_mail/views.py
- [x] T106 [US6] Implement process_mail_accounts Celery task in src/paperless_mail/tasks.py
- [x] T107 [US6] Implement IMAP email fetching and attachment extraction
- [x] T108 [US6] Implement mail rule filtering and action execution
- [x] T109 [US6] Implement OAuth support for mail accounts in src/paperless_mail/views.py (OauthCallbackView)
- [x] T110 [US6] Implement frontend mail account configuration UI
- [x] T111 [US6] Implement frontend mail rule management UI
- [x] T112 [US6] Implement frontend processed mail history UI

**Checkpoint**: At this point, User Stories 1-6 should all work independently

---

## Phase 9: User Story 7 - Workflow Automation (Priority: P3)

**Goal**: Enable workflow automation with triggers and actions for document processing tasks

**Independent Test**: Create a workflow with consumption trigger and actions, upload a matching document, verify actions execute.

### Implementation for User Story 7

- [x] T113 [US7] Create Workflow model in src/documents/models.py
- [x] T114 [US7] Create WorkflowTrigger model in src/documents/models.py with comprehensive filter options
- [x] T115 [US7] Create WorkflowAction model in src/documents/models.py with assignment/removal/email/webhook types
- [x] T116 [US7] Create WorkflowActionEmail model in src/documents/models.py
- [x] T117 [US7] Create WorkflowActionWebhook model in src/documents/models.py
- [x] T118 [US7] Create WorkflowRun model for execution tracking in src/documents/models.py
- [x] T119 [US7] Implement WorkflowSerializer in src/documents/serialisers.py
- [x] T120 [US7] Implement WorkflowTriggerSerializer in src/documents/serialisers.py
- [x] T121 [US7] Implement WorkflowActionSerializer in src/documents/serialisers.py
- [x] T122 [US7] Implement WorkflowViewSet in src/documents/views.py
- [x] T123 [US7] Implement WorkflowTriggerViewSet in src/documents/views.py
- [x] T124 [US7] Implement WorkflowActionViewSet in src/documents/views.py
- [x] T125 [US7] Implement workflow trigger evaluation in src/documents/signals/handlers.py (run_workflows)
- [x] T126 [US7] Implement workflow action execution (assign metadata, remove metadata, email, webhook)
- [x] T127 [US7] Implement WorkflowTriggerPlugin for consumption workflow in src/documents/consumer.py
- [x] T128 [US7] Implement scheduled workflow trigger support
- [x] T129 [US7] Implement frontend workflow creation and management UI
- [x] T130 [US7] Implement frontend workflow trigger configuration UI
- [x] T131 [US7] Implement frontend workflow action configuration UI

**Checkpoint**: All user stories should now be independently functional

---

## Phase 10: Additional Core Features

**Purpose**: Supporting features that enhance the core functionality

- [x] T132 [P] Create Note model for document notes in src/documents/models.py
- [x] T133 [P] Implement document notes API endpoints in DocumentViewSet.notes() in src/documents/views.py
- [x] T134 [P] Implement document history/audit logging support (when enabled) in src/documents/views.py
- [x] T135 [P] Implement document metadata endpoint in DocumentViewSet.metadata() in src/documents/views.py
- [x] T136 [P] Implement document download endpoint in DocumentViewSet.download() in src/documents/views.py
- [x] T137 [P] Implement document thumbnail endpoint in DocumentViewSet.thumb() in src/documents/views.py
- [x] T138 [P] Implement document preview endpoint in DocumentViewSet.preview() in src/documents/views.py
- [x] T139 [P] Implement StatisticsView for system statistics in src/documents/views.py
- [x] T140 [P] Implement SystemStatusView for health checks in src/documents/views.py
- [x] T141 [P] Implement TrashView for soft-deleted documents in src/documents/views.py
- [x] T142 [P] Implement BulkDownloadView for ZIP archive downloads in src/documents/views.py
- [x] T143 [P] Implement TasksViewSet for Celery task monitoring in src/documents/views.py
- [x] T144 [P] Implement UiSettingsView for UI configuration in src/documents/views.py
- [x] T145 [P] Implement SelectionDataView for bulk selection data in src/documents/views.py
- [x] T146 [P] Implement LogViewSet for system logs in src/documents/views.py
- [x] T147 [P] Implement document export functionality in src/documents/management/commands/document_exporter.py
- [x] T148 [P] Implement GPG encryption support for document storage (optional)
- [x] T149 [P] Implement archive serial number support in Document model
- [x] T150 [P] Implement double-sided document collation plugin in src/documents/double_sided.py
- [x] T151 [P] Implement barcode detection plugin in src/documents/barcodes.py
- [x] T152 [P] Implement sanity checker for document archive health in src/documents/sanity_checker.py
- [x] T153 [P] Implement sanity_check Celery task in src/documents/tasks.py

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T154 [P] Documentation updates in docs/ (per Constitution Principle VI)
- [x] T155 [P] API documentation via DRF Spectacular (OpenAPI schema) in src/paperless/urls.py
- [x] T156 Code cleanup and refactoring across all modules
- [x] T157 Run ruff formatter and fix formatting issues (per Constitution Principle II)
- [x] T158 Run mypy type checking and fix type errors (per Constitution Principle II)
- [x] T159 Run pytest with coverage reporting (per Constitution Principle II)
- [x] T160 [P] Comprehensive test suite in src/\*/tests/ (required per Constitution Principle II)
- [x] T161 Security review for document handling (per Constitution Principle III)
- [x] T162 Performance optimization across all stories (database queries, search indexing)
- [x] T163 [P] Frontend translation support via Crowdin (messages.xlf)
- [x] T164 [P] Backend translation support (django.po files)
- [x] T165 [P] Frontend API version interceptor in src-ui/src/app/interceptors/api-version.interceptor.ts
- [x] T166 [P] Frontend environment configuration in src-ui/src/environments/
- [x] T167 Implement caching for document queries in src/documents/caching.py
- [x] T168 Implement document signal handlers for automatic operations in src/documents/signals/handlers.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately ✅
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories ✅
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion ✅
  - User stories implemented in priority order (P1 → P2 → P3)
- **Additional Features (Phase 10)**: Depends on core user stories ✅
- **Polish (Phase 11)**: Depends on all desired user stories being complete ✅

### User Story Dependencies

- **User Story 1 (P1)**: Started after Foundational (Phase 2) - No dependencies on other stories ✅
- **User Story 2 (P2)**: Started after Foundational (Phase 2) - Depends on US1 (Document model) ✅
- **User Story 3 (P3)**: Started after Foundational (Phase 2) - Depends on US1 (Document model) ✅
- **User Story 4 (P4)**: Started after Foundational (Phase 2) - Depends on US1, US3 (metadata models) ✅
- **User Story 5 (P5)**: Started after Foundational (Phase 2) - Depends on US1 (Document model) ✅
- **User Story 6 (P6)**: Started after Foundational (Phase 2) - Depends on US1 (Document consumption) ✅
- **User Story 7 (P7)**: Started after Foundational (Phase 2) - Depends on US1, US3, US4 (documents, metadata, matching) ✅

### Within Each User Story

- Models before services ✅
- Services before endpoints ✅
- Core implementation before integration ✅
- Story complete before moving to next priority ✅

### Parallel Opportunities

- All Setup tasks marked [P] ran in parallel ✅
- All Foundational tasks marked [P] ran in parallel ✅
- Models within stories marked [P] ran in parallel ✅
- Frontend and backend development proceeded in parallel where possible ✅

---

## Implementation Summary

### Total Task Count: 168 tasks

### Task Count Per User Story

- **User Story 1 (P1)**: 22 tasks - Document Upload and Processing
- **User Story 2 (P1)**: 17 tasks - Document Search and Discovery
- **User Story 3 (P1)**: 19 tasks - Document Metadata Management
- **User Story 4 (P2)**: 10 tasks - Automatic Matching and Classification
- **User Story 5 (P2)**: 12 tasks - Document Sharing and Access Control
- **User Story 6 (P2)**: 14 tasks - Email Processing
- **User Story 7 (P3)**: 19 tasks - Workflow Automation
- **Additional Features**: 22 tasks - Supporting features
- **Setup & Foundational**: 18 tasks - Infrastructure
- **Polish**: 15 tasks - Cross-cutting concerns

### Independent Test Criteria

- **US1**: Upload PDF via web UI → appears in list with text, thumbnail, metadata ✅
- **US2**: Create document → search by title → filter by tag → results correct ✅
- **US3**: Create tags/correspondents/types → assign to documents individually and in bulk ✅
- **US4**: Train classifier → upload document → verify automatic assignments ✅
- **US5**: Create share link → access via public URL → permissions enforced ✅
- **US6**: Configure mail account/rule → send email → attachment processed ✅
- **US7**: Create workflow → upload matching document → actions execute ✅

### MVP Scope

**MVP (User Story 1 Only)**: Document upload and processing - Core functionality that enables the system to ingest and process documents. ✅

### Status

**All tasks complete** - This represents the baseline implementation of Paperless-ngx core functionality. Future add-on features can build upon this foundation.

---

## Notes

- All tasks marked as complete (✅) represent existing implementation
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Implementation follows Paperless-ngx Constitution principles
- Ready for add-on feature development
