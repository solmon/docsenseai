# API Endpoints: Paperless-ngx REST API

**Feature**: Paperless-ngx Core Document Management System
**Date**: 2025-01-27
**Status**: Current Implementation

## API Overview

The Paperless-ngx REST API is fully documented via DRF Spectacular (OpenAPI 3.0). The interactive API documentation is available at `/api/schema/view/` when the application is running.

**Base URL**: `/api/`
**API Versioning**: Specified via `Accept: application/json; version=N` header
**Current Default Version**: 9
**Supported Versions**: 1, 2, 3, 4, 5, 6, 7, 8, 9

## Authentication

Four authentication methods are supported:

1. **Basic Authentication**: `Authorization: Basic <base64(username:password)>`
2. **Session Authentication**: Automatic when logged into web UI
3. **Token Authentication**: `Authorization: Token <token>` (obtain from `/api/token/`)
4. **Remote User Authentication**: When enabled via configuration

## Core Endpoints

### Documents

**Base**: `/api/documents/`

- `GET /api/documents/` - List documents (supports filtering, search, pagination)
- `POST /api/documents/` - Upload new document
- `GET /api/documents/{id}/` - Retrieve document details
- `PATCH /api/documents/{id}/` - Update document metadata
- `DELETE /api/documents/{id}/` - Delete document (soft delete)
- `GET /api/documents/{id}/download/` - Download document file
- `GET /api/documents/{id}/thumb/` - Get document thumbnail
- `GET /api/documents/{id}/preview/` - Get document preview
- `GET /api/documents/{id}/suggestions/` - Get automatic matching suggestions
- `GET /api/documents/{id}/metadata/` - Get document metadata
- `GET /api/documents/{id}/history/` - Get document history/audit log
- `GET /api/documents/{id}/notes/` - Get document notes
- `POST /api/documents/{id}/notes/` - Add note to document
- `DELETE /api/documents/{id}/notes/?id={note_id}` - Delete note

**Query Parameters**:

- `query`: Full-text search query
- `more_like_id`: Find similar documents
- `tags__id__in`: Filter by tag IDs
- `correspondent__id`: Filter by correspondent
- `document_type__id`: Filter by document type
- `created__gte`, `created__lte`: Date range filters
- `ordering`: Sort field (id, title, created, added, etc.)
- `page`: Page number for pagination
- `page_size`: Items per page
- `fields`: Comma-separated list of fields to return

### Tags

**Base**: `/api/tags/`

- `GET /api/tags/` - List tags
- `POST /api/tags/` - Create tag
- `GET /api/tags/{id}/` - Retrieve tag
- `PATCH /api/tags/{id}/` - Update tag
- `DELETE /api/tags/{id}/` - Delete tag

**Special Fields**:

- `color`: Hex color code
- `parent`: Parent tag ID for hierarchy
- `is_inbox_tag`: Boolean for automatic assignment

### Correspondents

**Base**: `/api/correspondents/`

- `GET /api/correspondents/` - List correspondents
- `POST /api/correspondents/` - Create correspondent
- `GET /api/correspondents/{id}/` - Retrieve correspondent
- `PATCH /api/correspondents/{id}/` - Update correspondent
- `DELETE /api/correspondents/{id}/` - Delete correspondent

### Document Types

**Base**: `/api/document_types/`

- `GET /api/document_types/` - List document types
- `POST /api/document_types/` - Create document type
- `GET /api/document_types/{id}/` - Retrieve document type
- `PATCH /api/document_types/{id}/` - Update document type
- `DELETE /api/document_types/{id}/` - Delete document type

### Storage Paths

**Base**: `/api/storage_paths/`

- `GET /api/storage_paths/` - List storage paths
- `POST /api/storage_paths/` - Create storage path
- `GET /api/storage_paths/{id}/` - Retrieve storage path
- `PATCH /api/storage_paths/{id}/` - Update storage path
- `DELETE /api/storage_paths/{id}/` - Delete storage path

### Custom Fields

**Base**: `/api/custom_fields/`

- `GET /api/custom_fields/` - List custom fields
- `POST /api/custom_fields/` - Create custom field
- `GET /api/custom_fields/{id}/` - Retrieve custom field
- `PATCH /api/custom_fields/{id}/` - Update custom field
- `DELETE /api/custom_fields/{id}/` - Delete custom field

**Data Types**: string, url, date, boolean, integer, float, monetary, documentlink, select, longtext

### Saved Views

**Base**: `/api/saved_views/`

- `GET /api/saved_views/` - List saved views
- `POST /api/saved_views/` - Create saved view
- `GET /api/saved_views/{id}/` - Retrieve saved view
- `PATCH /api/saved_views/{id}/` - Update saved view
- `DELETE /api/saved_views/{id}/` - Delete saved view

### Workflows

**Base**: `/api/workflows/`

- `GET /api/workflows/` - List workflows
- `POST /api/workflows/` - Create workflow
- `GET /api/workflows/{id}/` - Retrieve workflow
- `PATCH /api/workflows/{id}/` - Update workflow
- `DELETE /api/workflows/{id}/` - Delete workflow

**Related Endpoints**:

- `/api/workflow_triggers/` - Manage workflow triggers
- `/api/workflow_actions/` - Manage workflow actions

### Share Links

**Base**: `/api/share_links/`

- `GET /api/share_links/` - List share links
- `POST /api/share_links/` - Create share link
- `GET /api/share_links/{id}/` - Retrieve share link
- `DELETE /api/share_links/{id}/` - Delete share link

**Public Access**: `/share/{slug}/` - Access document via share link (no authentication required)

### Mail Accounts

**Base**: `/api/mail_accounts/`

- `GET /api/mail_accounts/` - List mail accounts
- `POST /api/mail_accounts/` - Create mail account
- `GET /api/mail_accounts/{id}/` - Retrieve mail account
- `PATCH /api/mail_accounts/{id}/` - Update mail account
- `DELETE /api/mail_accounts/{id}/` - Delete mail account

### Mail Rules

**Base**: `/api/mail_rules/`

- `GET /api/mail_rules/` - List mail rules
- `POST /api/mail_rules/` - Create mail rule
- `GET /api/mail_rules/{id}/` - Retrieve mail rule
- `PATCH /api/mail_rules/{id}/` - Update mail rule
- `DELETE /api/mail_rules/{id}/` - Delete mail rule

### Users and Groups

**Base**: `/api/users/`, `/api/groups/`

- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Retrieve user
- `PATCH /api/users/{id}/` - Update user
- `GET /api/groups/` - List groups
- `GET /api/groups/{id}/` - Retrieve group

### Tasks

**Base**: `/api/tasks/`

- `GET /api/tasks/` - List Celery tasks
- `GET /api/tasks/{id}/` - Retrieve task status
- `POST /api/tasks/{id}/acknowledge/` - Acknowledge task

### Search

**Base**: `/api/search/`

- `GET /api/search/` - Global search across all documents
- `GET /api/search/autocomplete/` - Search autocomplete suggestions

### Statistics

**Base**: `/api/statistics/`

- `GET /api/statistics/` - Get system statistics (document counts, storage usage, etc.)

### Bulk Operations

**Base**: `/api/documents/bulk_edit/`

- `POST /api/documents/bulk_edit/` - Bulk edit documents (assign tags, correspondent, etc.)

**Base**: `/api/bulk_edit_objects/`

- `POST /api/bulk_edit_objects/` - Bulk edit objects (tags, correspondents, etc.) - set permissions or delete

### Bulk Download

**Base**: `/api/documents/bulk_download/`

- `POST /api/documents/bulk_download/` - Download multiple documents as ZIP archive

### UI Settings

**Base**: `/api/ui_settings/`

- `GET /api/ui_settings/` - Get UI settings
- `PATCH /api/ui_settings/` - Update UI settings

### System Status

**Base**: `/api/system_status/`

- `GET /api/system_status/` - Get system status and health information

### Trash

**Base**: `/api/trash/`

- `GET /api/trash/` - List soft-deleted documents
- `POST /api/trash/` - Restore or permanently delete documents

## API Versioning

**Version Specification**: Include `Accept: application/json; version=N` header in requests.

**Version Support**:

- Versions 1-9 are currently supported
- Default version (when not specified): 1 (for legacy compatibility)
- New API versions added to `ALLOWED_VERSIONS` in settings
- Older versions guaranteed support for at least one year after new version release

**Version Headers** (in responses):

- `X-Api-Version`: Current API version number
- `X-Version`: Application version string

## Response Formats

**Success Responses**:

- `200 OK`: Successful GET, PATCH requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests

**Error Responses**:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `406 Not Acceptable`: Invalid API version specified

**Pagination**:

- Responses include `count`, `next`, `previous`, `results` fields
- Use `page` and `page_size` query parameters

## OpenAPI Schema

The complete OpenAPI 3.0 schema is available at:

- `/api/schema/` - JSON schema
- `/api/schema/view/` - Interactive Swagger UI

The schema is generated automatically by DRF Spectacular from the Django REST Framework viewsets and serializers.

## Example Requests

### Upload Document

```http
POST /api/documents/ HTTP/1.1
Accept: application/json; version=9
Authorization: Token <token>
Content-Type: multipart/form-data

document: <file>
title: "Invoice 2024-01"
correspondent: 1
tags: [2, 3]
```

### Search Documents

```http
GET /api/documents/?query=invoice&tags__id__in=2&ordering=-created HTTP/1.1
Accept: application/json; version=9
Authorization: Token <token>
```

### Bulk Edit Documents

```http
POST /api/documents/bulk_edit/ HTTP/1.1
Accept: application/json; version=9
Authorization: Token <token>
Content-Type: application/json

{
  "documents": [1, 2, 3],
  "method": "modify_tags",
  "parameters": {
    "add_tags": [4, 5],
    "remove_tags": [2]
  }
}
```

## Notes

- All endpoints require authentication except `/share/{slug}/`
- Object-level permissions enforced via Django Guardian
- Soft deletion used for documents and related objects
- File downloads use streaming responses for large files
- API versioning ensures backward compatibility
