# Data Model: Paperless-ngx Core Entities

**Feature**: Paperless-ngx Core Document Management System
**Date**: 2025-01-27
**Status**: Current Implementation

## Entity Relationship Overview

```
User/Group (Django)
    │
    ├─── Document (owner, permissions)
    │       ├─── Correspondent
    │       ├─── DocumentType
    │       ├─── StoragePath
    │       ├─── Tag (many-to-many)
    │       ├─── CustomFieldInstance (many)
    │       ├─── Note (many)
    │       ├─── ShareLink (many)
    │       └─── WorkflowRun (many)
    │
    ├─── Tag (owner, hierarchical)
    ├─── Correspondent (owner)
    ├─── DocumentType (owner)
    ├─── StoragePath (owner)
    ├─── CustomField (owner)
    ├─── SavedView (owner)
    ├─── Workflow (no owner, global)
    │       ├─── WorkflowTrigger (many-to-many)
    │       └─── WorkflowAction (many-to-many)
    │
    └─── MailAccount (owner)
            └─── MailRule (many)
```

## Core Entities

### Document

**Purpose**: Core entity representing a stored document with all metadata and content.

**Key Attributes**:

- `id`: Primary key
- `title`: Document title (max 128 chars, indexed)
- `content`: Extracted text content for search (text field)
- `mime_type`: MIME type of original document
- `checksum`: MD5 checksum of original file (unique, prevents duplicates)
- `archive_checksum`: MD5 checksum of PDF/A archive version
- `page_count`: Number of pages
- `created`: Document creation date (from document content or user input)
- `modified`: Last modification timestamp
- `added`: When document was added to system (immutable, indexed)
- `filename`: Current filename in storage (unique)
- `archive_filename`: Archive version filename (unique, nullable)
- `original_filename`: Original filename when uploaded
- `storage_type`: "unencrypted" (default) or "gpg" (encrypted)
- `archive_serial_number`: Physical archive tracking number (0-0xFFFFFF, unique, indexed)
- `correspondent`: Foreign key to Correspondent (nullable)
- `document_type`: Foreign key to DocumentType (nullable)
- `storage_path`: Foreign key to StoragePath (nullable)
- `owner`: Foreign key to User (nullable, for permissions)
- `tags`: Many-to-many relationship with Tag
- `deleted`: Soft delete flag (from SoftDeleteModel)

**Relationships**:

- Belongs to: Correspondent, DocumentType, StoragePath, User (owner)
- Has many: CustomFieldInstance, Note, ShareLink, WorkflowRun
- Many-to-many: Tag

**Validation Rules**:

- Checksum must be unique (prevents duplicate documents)
- Archive serial number must be unique if set
- Created date should be parseable from document or provided by user

**State Transitions**:

- Created → Processing (via Celery task)
- Processing → Indexed (text extracted and indexed)
- Indexed → Archived (PDF/A version created)
- Any state → Deleted (soft delete)

### Tag

**Purpose**: Hierarchical labels for organizing documents.

**Key Attributes**:

- `id`: Primary key
- `name`: Tag name (max 128 chars, unique per owner)
- `color`: Hex color code (default: #a6cee3)
- `is_inbox_tag`: Boolean, automatically assigned to new documents
- `match`: Matching pattern string (max 256 chars)
- `matching_algorithm`: Integer choice (none, any word, all words, exact, regex, fuzzy, automatic)
- `is_insensitive`: Case-insensitive matching (default: True)
- `owner`: Foreign key to User (nullable, for permissions)
- `parent`: Self-referential foreign key for hierarchy (nullable)
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: User (owner)
- Self-referential: Parent tag (nullable)
- Many-to-many: Document

**Validation Rules**:

- Maximum nesting depth: 5 levels (root = 1, max = 5)
- Cannot be its own parent
- Cannot have descendant as parent (prevents cycles)
- Name must be unique per owner (or globally if no owner)

**Hierarchy Behavior**:

- When child tag assigned to document, parent tags automatically added
- When tag removed from document, child tags automatically removed
- When parent assigned to existing tag, all documents with child tag get parent tag

### Correspondent

**Purpose**: Person, institution, or company associated with documents.

**Key Attributes**:

- `id`: Primary key
- `name`: Correspondent name (max 128 chars, unique per owner)
- `match`: Matching pattern string (max 256 chars)
- `matching_algorithm`: Integer choice (none, any word, all words, exact, regex, fuzzy, automatic)
- `is_insensitive`: Case-insensitive matching (default: True)
- `owner`: Foreign key to User (nullable, for permissions)
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: User (owner)
- Has many: Document

**Validation Rules**:

- Name must be unique per owner (or globally if no owner)

### DocumentType

**Purpose**: Classification of document purpose (invoice, letter, contract, etc.).

**Key Attributes**:

- `id`: Primary key
- `name`: Document type name (max 128 chars, unique per owner)
- `match`: Matching pattern string (max 256 chars)
- `matching_algorithm`: Integer choice (none, any word, all words, exact, regex, fuzzy, automatic)
- `is_insensitive`: Case-insensitive matching (default: True)
- `owner`: Foreign key to User (nullable, for permissions)
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: User (owner)
- Has many: Document

**Validation Rules**:

- Name must be unique per owner (or globally if no owner)

### StoragePath

**Purpose**: File system path configuration for document storage organization.

**Key Attributes**:

- `id`: Primary key
- `name`: Storage path name (max 128 chars, unique per owner)
- `path`: Path template string (text field, supports Jinja2 templating)
- `match`: Matching pattern string (max 256 chars)
- `matching_algorithm`: Integer choice (none, any word, all words, exact, regex, fuzzy, automatic)
- `is_insensitive`: Case-insensitive matching (default: True)
- `owner`: Foreign key to User (nullable, for permissions)
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: User (owner)
- Has many: Document

**Validation Rules**:

- Name must be unique per owner (or globally if no owner)
- Path template must be valid Jinja2 syntax

### CustomField

**Purpose**: Definition of custom metadata fields with data type and configuration.

**Key Attributes**:

- `id`: Primary key
- `name`: Field name (max 128 chars, unique globally)
- `data_type`: String choice (string, url, date, boolean, integer, float, monetary, documentlink, select, longtext)
- `extra_data`: JSON field for type-specific configuration (select options, default currency, etc.)
- `created`: Creation timestamp

**Relationships**:

- Has many: CustomFieldInstance

**Data Type Details**:

- `string`: Text up to 128 characters
- `url`: Valid URL
- `date`: Date value
- `boolean`: True/false
- `integer`: Integer number
- `float`: Floating point number
- `monetary`: Currency amount (stored as string with amount and currency)
- `documentlink`: Reference to other document(s)
- `select`: Choice from predefined options (stored in extra_data)
- `longtext`: Text without length limit

### CustomFieldInstance

**Purpose**: Value of a custom field attached to a specific document.

**Key Attributes**:

- `id`: Primary key
- `document`: Foreign key to Document
- `field`: Foreign key to CustomField
- `value_text`: String value (for string, url types)
- `value_bool`: Boolean value
- `value_url`: URL value
- `value_date`: Date value
- `value_int`: Integer value
- `value_float`: Float value
- `value_monetary`: Monetary string value
- `value_document_ids`: JSON array of document IDs (for documentlink)
- `value_select`: String choice value (for select)
- `value_long_text`: Text value (for longtext)
- `created`: Creation timestamp
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: Document, CustomField

**Validation Rules**:

- Only one value field is populated based on field.data_type
- Value must match field data type constraints

### SavedView

**Purpose**: Saved filter configuration with display preferences.

**Key Attributes**:

- `id`: Primary key
- `name`: View name (max 128 chars)
- `show_on_dashboard`: Boolean, display on dashboard
- `show_in_sidebar`: Boolean, display in sidebar
- `sort_field`: Field name to sort by (max 128 chars, nullable)
- `sort_reverse`: Boolean, reverse sort order
- `page_size`: Number of items per page (nullable)
- `display_mode`: String choice (table, smallCards, largeCards)
- `display_fields`: JSON array of field names to display
- `owner`: Foreign key to User (nullable, for permissions)

**Relationships**:

- Belongs to: User (owner)
- Has many: SavedViewFilterRule

### SavedViewFilterRule

**Purpose**: Individual filter rule within a saved view.

**Key Attributes**:

- `id`: Primary key
- `saved_view`: Foreign key to SavedView
- `rule_type`: Integer choice (25+ rule types: title contains, content contains, ASN is, correspondent is, has tag, created before/after, etc.)
- `value`: Filter value (text field, depends on rule_type)

**Relationships**:

- Belongs to: SavedView

### ShareLink

**Purpose**: Public access link for documents with optional expiration.

**Key Attributes**:

- `id`: Primary key
- `document`: Foreign key to Document
- `slug`: Unique slug for URL (generated)
- `created`: Creation timestamp
- `expiration`: Expiration datetime (nullable)
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: Document

**Validation Rules**:

- Slug must be unique
- Expiration must be in future if set

### Workflow

**Purpose**: Automation configuration with triggers and actions.

**Key Attributes**:

- `id`: Primary key
- `name`: Workflow name (max 256 chars, unique)
- `order`: Integer, execution order (default: 0)
- `enabled`: Boolean, whether workflow is active (default: True)

**Relationships**:

- Many-to-many: WorkflowTrigger, WorkflowAction
- Has many: WorkflowRun

**Validation Rules**:

- Must have at least one trigger
- Must have at least one action

### WorkflowTrigger

**Purpose**: Condition that triggers a workflow.

**Key Attributes**:

- `id`: Primary key
- `type`: Integer choice (CONSUMPTION, UPDATE, SCHEDULED)
- `sources`: Multi-select field (ConsumeFolder, ApiUpload, MailFetch, WebUI)
- `filter_path`: Path filter pattern (max 256 chars, nullable, supports wildcards)
- `filter_filename`: Filename filter pattern (max 256 chars, nullable, supports wildcards)
- `filter_mailrule`: Foreign key to MailRule (nullable)
- `match`: Matching pattern string (max 256 chars)
- `matching_algorithm`: Integer choice (NONE, ANY, ALL, LITERAL, REGEX, FUZZY, AUTO)
- `is_insensitive`: Boolean, case-insensitive matching
- `filter_has_tags`: Many-to-many with Tag
- `filter_has_all_tags`: Many-to-many with Tag
- `filter_has_not_tags`: Many-to-many with Tag
- `filter_has_document_type`: Foreign key to DocumentType (nullable)
- `filter_has_not_document_types`: Many-to-many with DocumentType
- `filter_has_correspondent`: Foreign key to Correspondent (nullable)
- `filter_has_not_correspondents`: Many-to-many with Correspondent
- `filter_has_storage_path`: Foreign key to StoragePath (nullable)
- `filter_has_not_storage_paths`: Many-to-many with StoragePath
- `filter_custom_field_query`: JSON-encoded custom field query (text field, nullable)
- `schedule_offset_days`: Integer, days to offset schedule (default: 0)
- `schedule_is_recurring`: Boolean, recurring schedule (default: False)
- `schedule_recurring_interval_days`: Positive integer, days between recurrences (default: 1)
- `schedule_date_field`: String choice (added, created, modified, custom_field)
- `schedule_date_custom_field`: Foreign key to CustomField (nullable)

**Relationships**:

- Many-to-many: Workflow, Tag, DocumentType, Correspondent, StoragePath
- Belongs to: MailRule (filter_mailrule), CustomField (schedule_date_custom_field)

### WorkflowAction

**Purpose**: Action executed when workflow triggers.

**Key Attributes**:

- `id`: Primary key
- `type`: Integer choice (ASSIGNMENT, REMOVAL, EMAIL, WEBHOOK)
- `assign_title`: Jinja2 template for document title (text field, nullable)
- `assign_tags`: Many-to-many with Tag
- `assign_document_type`: Foreign key to DocumentType (nullable)
- `assign_correspondent`: Foreign key to Correspondent (nullable)
- `assign_storage_path`: Foreign key to StoragePath (nullable)
- `assign_owner`: Foreign key to User (nullable)
- `assign_view_users`: Many-to-many with User
- `assign_view_groups`: Many-to-many with Group
- `assign_change_users`: Many-to-many with User
- `assign_change_groups`: Many-to-many with Group
- `assign_custom_fields`: Many-to-many with CustomField
- `assign_custom_fields_values`: JSON object mapping custom field IDs to values
- `remove_tags`: Many-to-many with Tag
- `remove_all_tags`: Boolean
- `remove_document_types`: Many-to-many with DocumentType
- `remove_all_document_types`: Boolean
- `remove_correspondents`: Many-to-many with Correspondent
- `remove_all_correspondents`: Boolean
- `remove_storage_paths`: Many-to-many with StoragePath
- `remove_all_storage_paths`: Boolean
- `remove_owners`: Many-to-many with User
- `remove_all_owners`: Boolean
- `remove_view_users`: Many-to-many with User
- `remove_view_groups`: Many-to-many with Group
- `remove_change_users`: Many-to-many with User
- `remove_change_groups`: Many-to-many with Group
- `remove_all_permissions`: Boolean
- `remove_custom_fields`: Many-to-many with CustomField
- `remove_all_custom_fields`: Boolean
- `email`: Foreign key to WorkflowActionEmail (nullable)
- `webhook`: Foreign key to WorkflowActionWebhook (nullable)

**Relationships**:

- Many-to-many: Workflow, Tag, DocumentType, Correspondent, StoragePath, User, Group, CustomField
- Belongs to: WorkflowActionEmail, WorkflowActionWebhook

### WorkflowActionEmail

**Purpose**: Email action configuration for workflows.

**Key Attributes**:

- `id`: Primary key
- `subject`: Email subject (max 256 chars, supports placeholders)
- `body`: Email body (text field, supports placeholders)
- `to`: Comma-separated email addresses (text field)

**Relationships**:

- Has one: WorkflowAction

### WorkflowActionWebhook

**Purpose**: Webhook action configuration for workflows.

**Key Attributes**:

- `id`: Primary key
- `url`: Webhook URL (text field, validation in serializer)
- `method`: HTTP method (GET, POST, PUT, PATCH, DELETE)
- `headers`: JSON object of HTTP headers (nullable)
- `include_document`: Boolean, include document in payload

**Relationships**:

- Has one: WorkflowAction

### WorkflowRun

**Purpose**: Execution record of a workflow.

**Key Attributes**:

- `id`: Primary key
- `workflow`: Foreign key to Workflow
- `document`: Foreign key to Document
- `trigger`: Foreign key to WorkflowTrigger
- `created`: Execution timestamp
- `deleted`: Soft delete flag

**Relationships**:

- Belongs to: Workflow, Document, WorkflowTrigger

## Supporting Entities

### Note

**Purpose**: User notes attached to documents.

**Key Attributes**:

- `id`: Primary key
- `document`: Foreign key to Document
- `note`: Note text (text field)
- `created`: Creation timestamp
- `user`: Foreign key to User (author)

**Relationships**:

- Belongs to: Document, User

### MailAccount (from paperless_mail app)

**Purpose**: Email account configuration for document ingestion.

**Key Attributes**:

- `id`: Primary key
- `name`: Account name
- `imap_server`: IMAP server address
- `imap_port`: IMAP port
- `imap_security`: Security type (SSL, STARTTLS, none)
- `username`: Email username
- `password`: Encrypted password
- `is_token`: Boolean, OAuth token authentication
- `owner`: Foreign key to User (nullable, for permissions)

**Relationships**:

- Belongs to: User (owner)
- Has many: MailRule

### MailRule (from paperless_mail app)

**Purpose**: Rule for processing emails and extracting documents.

**Key Attributes**:

- `id`: Primary key
- `name`: Rule name
- `account`: Foreign key to MailAccount
- `folder`: IMAP folder to monitor
- `filter_from`: From address filter
- `filter_subject`: Subject filter
- `filter_body`: Body filter
- `filter_attachment_filename`: Attachment filename filter
- `maximum_age`: Maximum email age in days
- `action`: Action to perform (mark_read, delete, move, flag)
- `action_parameter`: Action parameter (folder name, etc.)
- `assign_title`: Title template
- `assign_tags`: Many-to-many with Tag
- `assign_correspondent`: Foreign key to Correspondent (nullable)
- `assign_document_type`: Foreign key to DocumentType (nullable)
- `assign_storage_path`: Foreign key to StoragePath (nullable)
- `owner`: Foreign key to User (nullable, for permissions)

**Relationships**:

- Belongs to: MailAccount, Correspondent, DocumentType, StoragePath, User (owner)
- Many-to-many: Tag

## Base Classes and Mixins

### ModelWithOwner

**Purpose**: Abstract base class providing ownership for permission management.

**Attributes**:

- `owner`: Foreign key to User (nullable)

**Used by**: All matching models (Tag, Correspondent, DocumentType, StoragePath), Document, SavedView, CustomField, MailAccount

### MatchingModel

**Purpose**: Abstract base class for entities that support automatic matching.

**Attributes**:

- `name`: Entity name (max 128 chars)
- `match`: Matching pattern (max 256 chars)
- `matching_algorithm`: Integer choice (none, any word, all words, exact, regex, fuzzy, automatic)
- `is_insensitive`: Boolean, case-insensitive matching
- `owner`: Foreign key to User (from ModelWithOwner)

**Used by**: Tag, Correspondent, DocumentType, StoragePath

**Constraints**:

- Unique constraint on (name, owner)
- Unique constraint on name when owner is null

### SoftDeleteModel

**Purpose**: Abstract base class providing soft deletion.

**Attributes**:

- `deleted`: Boolean, soft delete flag

**Used by**: Document, Tag, Correspondent, DocumentType, StoragePath, CustomFieldInstance, ShareLink, WorkflowRun

## Permission Model

**Framework**: Django Guardian for object-level permissions

**Permission Types**:

- `view`: Read access to object
- `change`: Modify object
- `delete`: Delete object (hard delete, separate from soft delete)

**Permission Scope**:

- Global permissions: Applied to all objects of a type
- Object-level permissions: Applied to specific objects
- User permissions: Granted to individual users
- Group permissions: Granted to user groups

**Default Behavior**:

- Objects without owner: Accessible to all authenticated users (based on global permissions)
- Objects with owner: Owner has full permissions, others require explicit permissions

## Indexes and Performance

**Database Indexes**:

- Document: `title`, `added`, `created`, `archive_serial_number`, `checksum` (unique)
- Tag: `name`, `owner` (composite unique)
- All models: `id` (primary key, auto-indexed)

**Search Index**:

- Whoosh full-text index on Document.content
- Updated asynchronously after document processing
- Supports relevance ranking and highlighting

## Data Integrity

**Referential Integrity**:

- Foreign keys use `on_delete=models.SET_NULL` for optional relationships
- Foreign keys use `on_delete=models.CASCADE` for required relationships (CustomFieldInstance → Document)
- Soft deletion preserves relationships (deleted flag, not actual deletion)

**Unique Constraints**:

- Document.checksum (prevents duplicate documents)
- Document.archive_serial_number (if set)
- Tag/CustomField name per owner
- Workflow name globally
- ShareLink.slug globally

**Validation**:

- Archive serial number: 0 to 0xFFFFFF
- Tag nesting depth: Maximum 5 levels
- Custom field values must match field data type
