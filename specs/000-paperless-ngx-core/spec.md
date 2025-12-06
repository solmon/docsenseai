# Feature Specification: Paperless-ngx Core Document Management System

**Feature Branch**: `dev`
**Created**: 2025-01-27
**Status**: Current Implementation
**Input**: Analysis of existing codebase to document current functionality

## User Scenarios & Testing

### User Story 1 - Document Upload and Processing (Priority: P1)

Users can upload documents through multiple channels (web UI, consumption folder, email, API) and the system automatically processes them through OCR, text extraction, PDF/A conversion, and metadata assignment.

**Why this priority**: This is the core functionality - without document ingestion, the system has no purpose.

**Independent Test**: Upload a PDF document via web UI and verify it appears in the document list with extracted text, thumbnail, and metadata.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they upload a document via web UI, **Then** the document is queued for processing and appears in the document list after processing completes
2. **Given** a file is placed in the consumption folder, **When** the consumer detects it, **Then** the document is automatically queued for processing via Celery
3. **Given** an email with attachment is received, **When** the mail processor runs, **Then** the attachment is extracted and queued as a document
4. **Given** a document is uploaded via API, **When** the POST request is made, **Then** the document is queued for processing and returns task ID

---

### User Story 2 - Document Search and Discovery (Priority: P1)

Users can search documents using full-text search, filter by metadata (tags, correspondents, document types, dates), and use saved views for common queries.

**Why this priority**: Users need to find documents quickly - search is essential for document management.

**Independent Test**: Create a document, search for it by title, filter by tag, and verify results are returned correctly.

**Acceptance Scenarios**:

1. **Given** documents exist in the system, **When** a user searches by query string, **Then** relevant documents are returned sorted by relevance with highlighted matches
2. **Given** documents have tags assigned, **When** a user filters by tag, **Then** only documents with that tag are shown
3. **Given** a user creates a saved view with filters, **When** they access the saved view, **Then** the filtered document list is displayed
4. **Given** a user searches for "more like this", **When** they select a document, **Then** similar documents are returned based on content similarity

---

### User Story 3 - Document Metadata Management (Priority: P1)

Users can assign and manage metadata (tags, correspondents, document types, storage paths, custom fields) on documents individually or in bulk.

**Why this priority**: Metadata organization is essential for document management and retrieval.

**Independent Test**: Create tags, correspondents, and document types, then assign them to documents individually and in bulk.

**Acceptance Scenarios**:

1. **Given** a document is displayed, **When** a user assigns tags, correspondent, and document type, **Then** the metadata is saved and displayed
2. **Given** multiple documents are selected, **When** a user performs bulk edit, **Then** all selected documents are updated with the new metadata
3. **Given** nested tags exist, **When** a child tag is assigned, **Then** parent tags are automatically added
4. **Given** custom fields are defined, **When** a user assigns values to custom fields, **Then** the values are stored and displayed on the document

---

### User Story 4 - Automatic Matching and Classification (Priority: P2)

The system automatically assigns tags, correspondents, and document types to documents using machine learning and rule-based matching algorithms.

**Why this priority**: Reduces manual work and improves document organization consistency.

**Independent Test**: Train the classifier on existing documents, then upload a new document and verify automatic assignments match expected values.

**Acceptance Scenarios**:

1. **Given** the classifier is trained, **When** a new document is processed, **Then** suggestions for tags, correspondents, and document types are generated
2. **Given** matching rules are configured, **When** a document matches a rule, **Then** the corresponding metadata is automatically assigned
3. **Given** a workflow trigger matches, **When** a document is consumed, **Then** workflow actions are executed automatically

---

### User Story 5 - Document Sharing and Access Control (Priority: P2)

Users can share documents via public links with optional expiration, and manage permissions at document and object levels.

**Why this priority**: Enables collaboration and controlled access to sensitive documents.

**Independent Test**: Create a share link for a document, access it via the public URL, and verify permissions are enforced.

**Acceptance Scenarios**:

1. **Given** a document exists, **When** a user creates a share link, **Then** a public URL is generated that allows access without authentication
2. **Given** a share link has expiration set, **When** the expiration date passes, **Then** the link no longer provides access
3. **Given** document-level permissions are set, **When** a user without permission tries to access, **Then** access is denied
4. **Given** object-level permissions are configured, **When** a user accesses documents, **Then** only permitted documents are visible

---

### User Story 6 - Email Processing (Priority: P2)

The system can process emails from configured mail accounts, extract attachments, and consume them as documents based on configurable rules.

**Why this priority**: Enables automated document ingestion from email sources.

**Independent Test**: Configure a mail account and rule, send a test email with attachment, verify the attachment is processed as a document.

**Acceptance Scenarios**:

1. **Given** a mail account is configured, **When** the mail processor runs, **Then** new emails are checked and attachments extracted
2. **Given** a mail rule matches an email, **When** the email is processed, **Then** the rule actions are executed (assign tags, correspondent, etc.)
3. **Given** an email is processed, **When** processing completes, **Then** post-processing actions are executed (mark as read, delete, etc.)

---

### User Story 7 - Workflow Automation (Priority: P3)

Users can create workflows with triggers and actions to automate document processing tasks.

**Why this priority**: Advanced feature that enables complex automation scenarios.

**Independent Test**: Create a workflow with consumption trigger and actions, upload a matching document, verify actions execute.

**Acceptance Scenarios**:

1. **Given** a workflow is created with consumption trigger, **When** a matching document is consumed, **Then** workflow actions are executed
2. **Given** a workflow has update trigger, **When** a document is updated, **Then** workflow actions are executed
3. **Given** workflow actions include metadata assignment, **When** workflow executes, **Then** metadata is applied to the document

---

### Edge Cases

- What happens when a duplicate document (same checksum) is uploaded? System prevents duplicate storage.
- How does system handle corrupted or unreadable files? Error is logged, task fails gracefully.
- What happens when OCR fails? Document is still stored but without extracted text.
- How are documents handled when storage is full? Error is raised, processing fails.
- What happens when a share link expires while being accessed? Access is denied immediately.
- How are nested tag hierarchies validated? Maximum depth of 5 levels enforced, circular references prevented.
- What happens when custom field data type changes? Existing instances retain old values, new instances use new type.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support document upload via web UI, consumption folder, email, and REST API
- **FR-002**: System MUST perform OCR on documents without text content
- **FR-003**: System MUST create PDF/A archive versions of documents
- **FR-004**: System MUST extract and index text content for full-text search
- **FR-005**: System MUST support multiple file formats (PDF, images, Office documents, plain text)
- **FR-006**: System MUST allow assignment of tags, correspondents, document types, and storage paths to documents
- **FR-007**: System MUST support nested tags with maximum depth of 5 levels
- **FR-008**: System MUST provide full-text search with relevance ranking and highlighting
- **FR-009**: System MUST support filtering by tags, correspondents, document types, dates, custom fields, and more
- **FR-010**: System MUST allow bulk editing of document metadata
- **FR-011**: System MUST support saved views with customizable filters and display options
- **FR-012**: System MUST provide automatic matching using machine learning classifier
- **FR-013**: System MUST support rule-based matching with multiple algorithms (any word, all words, exact match, regex, fuzzy, automatic)
- **FR-014**: System MUST support custom fields with multiple data types (string, URL, date, boolean, integer, float, monetary, document link, select, long text)
- **FR-015**: System MUST support document sharing via public links with optional expiration
- **FR-016**: System MUST enforce object-level and document-level permissions using Django Guardian
- **FR-017**: System MUST support multi-user access with user and group management
- **FR-018**: System MUST process emails from configured IMAP accounts
- **FR-019**: System MUST support mail rules for filtering and processing emails
- **FR-020**: System MUST support workflow automation with triggers and actions
- **FR-021**: System MUST provide REST API with versioning (versions 1-9 supported)
- **FR-022**: System MUST maintain backward compatibility for API versions for at least one year
- **FR-023**: System MUST support document export and import
- **FR-024**: System MUST provide document thumbnails and previews
- **FR-025**: System MUST support archive serial numbers for physical document tracking
- **FR-026**: System MUST support soft deletion of documents and objects
- **FR-027**: System MUST provide statistics and dashboard views
- **FR-028**: System MUST support document notes
- **FR-029**: System MUST support document history/audit logging (when enabled)
- **FR-030**: System MUST support optional GPG encryption for document storage

### Key Entities

- **Document**: Core entity representing a stored document with metadata (title, correspondent, document type, tags, storage path, dates, checksums, page count, custom fields, notes). Supports soft deletion and ownership.
- **Tag**: Hierarchical labels for organizing documents. Supports nesting up to 5 levels, color coding, inbox tagging, and matching algorithms.
- **Correspondent**: Person, institution, or company associated with documents. Supports matching algorithms for automatic assignment.
- **DocumentType**: Classification of document purpose (invoice, letter, contract, etc.). Supports matching algorithms.
- **StoragePath**: File system path configuration for document storage. Supports matching algorithms and path templates.
- **CustomField**: Definition of custom metadata fields with data type and configuration. Supports 10 data types including select options and monetary fields.
- **CustomFieldInstance**: Value of a custom field attached to a specific document. Stores typed values based on field definition.
- **SavedView**: Saved filter configuration with display preferences (table, small cards, large cards) and field selections.
- **ShareLink**: Public access link for documents with optional expiration date and slug-based access.
- **Workflow**: Automation configuration with triggers (consumption, update) and actions (assign metadata, run actions).
- **WorkflowTrigger**: Condition that triggers a workflow (document matching criteria).
- **WorkflowAction**: Action executed when workflow triggers (assign tag, correspondent, document type, storage path, custom field, delete document).
- **MailAccount**: Email account configuration (IMAP settings, OAuth support) for document ingestion.
- **MailRule**: Rule for processing emails (filter criteria, actions, attachment handling).
- **User**: Authentication and authorization entity with Django user model integration.
- **Group**: User group for permission management.
- **Task**: Celery task tracking for document processing, classification training, and maintenance operations.

## Success Criteria

### Measurable Outcomes

- **SC-001**: System processes documents in parallel on multi-core systems (Celery task queue)
- **SC-002**: Full-text search returns results sorted by relevance with sub-second response time
- **SC-003**: Automatic matching achieves >80% accuracy on trained datasets
- **SC-004**: API supports 9 concurrent versions with backward compatibility
- **SC-005**: System handles documents up to reasonable size limits (configurable)
- **SC-006**: Bulk operations process 100+ documents efficiently
- **SC-007**: Search index updates in near real-time after document processing
- **SC-008**: Document processing pipeline handles errors gracefully without data loss

## API Considerations

- **API Version**: Current default version is 9. All versions 1-9 are supported. New breaking changes require new API version.
- **Backward Compatibility**: Older API versions guaranteed support for at least one year after new version release. Version specified via `Accept: application/json; version=N` header.
- **Migration Notes**: API clients should specify version explicitly. Default version 1 for legacy compatibility. Version headers (`X-Api-Version`, `X-Version`) included in authenticated responses.

## Architecture Notes

- **Backend**: Django 5.2+ with Django REST Framework, Python 3.10-3.14
- **Frontend**: Angular/TypeScript single-page application
- **Task Processing**: Celery with Redis message broker for async document processing
- **Search**: Whoosh-based full-text search index
- **Database**: PostgreSQL or MariaDB supported
- **Storage**: File-based storage with optional GPG encryption
- **Authentication**: Django authentication with token, session, basic auth, and remote user support
- **Permissions**: Django Guardian for object-level permissions
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)

## Technology Constraints

- Python 3.10+ required
- Django 5.2+ (non-semver, only patch versions guaranteed non-breaking)
- Redis required for Celery task queue
- Optional: Apache Tika for Office document support
- Optional: Gotenberg for PDF conversion
- Frontend API version must match backend default version
