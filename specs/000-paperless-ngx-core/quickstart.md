# Quickstart Guide: Paperless-ngx Core System

**Feature**: Paperless-ngx Core Document Management System
**Date**: 2025-01-27
**Status**: Current Implementation

## Overview

This quickstart guide provides a high-level overview of how to use the Paperless-ngx document management system, covering the main workflows and features.

## Prerequisites

- Paperless-ngx installed and running (Docker Compose recommended)
- Web browser for accessing the UI
- Documents to upload (PDF, images, Office documents, etc.)

## Getting Started

### 1. Initial Setup

1. **Access the Web UI**: Navigate to `http://localhost:8000` (or your configured URL)
2. **Create Admin User**: On first run, create an administrator account
3. **Configure Settings**: Set up consumption folder, storage paths, and other preferences

### 2. Adding Documents

**Method 1: Web UI Upload**

1. Click "Upload" button in the UI
2. Select file(s) or drag-and-drop
3. Documents are automatically queued for processing

**Method 2: Consumption Folder**

1. Place files in the configured consumption folder
2. The consumer service automatically detects and processes them
3. Monitor progress in the tasks view

**Method 3: Email**

1. Configure mail accounts in Settings → Mail
2. Set up mail rules to filter and process emails
3. Attachments are automatically extracted and processed

**Method 4: API**

1. Obtain API token from Profile → API Token
2. POST to `/api/documents/` with file and metadata
3. Document is queued for processing

### 3. Document Processing

Documents go through automatic processing:

1. **File Detection**: Consumer or upload detects new file
2. **Task Queue**: Document added to Celery task queue
3. **OCR**: Text extraction if document has no text
4. **PDF/A Conversion**: Archive version created
5. **Text Indexing**: Content indexed for search
6. **Metadata Assignment**: Automatic matching suggests tags, correspondents, etc.

Monitor processing in the Tasks view.

### 4. Organizing Documents

**Assign Metadata**:

- **Tags**: Create hierarchical tags for organization
- **Correspondent**: Assign sender/recipient
- **Document Type**: Classify (invoice, letter, contract, etc.)
- **Storage Path**: Organize file storage
- **Custom Fields**: Add custom metadata (dates, amounts, etc.)

**Automatic Matching**:

- Train classifier on existing documents
- Configure matching rules for tags, correspondents, document types
- System suggests metadata based on content

**Bulk Operations**:

- Select multiple documents
- Use bulk edit to assign tags, correspondent, document type
- Apply changes to all selected documents at once

### 5. Finding Documents

**Full-Text Search**:

- Use search bar to search document content
- Results sorted by relevance
- Highlighted matches in results

**Filtering**:

- Filter by tags, correspondent, document type, dates
- Combine multiple filters
- Use advanced search syntax

**Saved Views**:

- Create saved views with filters and display preferences
- Show on dashboard or sidebar for quick access
- Customize display mode (table, small cards, large cards)

**More Like This**:

- Select a document
- Click "More like this" to find similar documents
- Based on content similarity

### 6. Workflow Automation

**Create Workflows**:

1. Go to Settings → Workflows
2. Create workflow with triggers (consumption, update, scheduled)
3. Define actions (assign metadata, send email, webhook, etc.)
4. Enable workflow

**Workflow Triggers**:

- **Consumption**: When document is consumed
- **Update**: When document is modified
- **Scheduled**: Based on document dates

**Workflow Actions**:

- Assign tags, correspondent, document type, storage path
- Assign custom fields with values
- Remove metadata
- Send email notifications
- Call webhooks
- Delete documents

### 7. Sharing Documents

**Share Links**:

1. Open document detail page
2. Click "Share" button
3. Set optional expiration date
4. Copy share link URL
5. Share URL provides public access (no login required)

**Permissions**:

- Set document-level permissions (view, change, delete)
- Set object-level permissions (tags, correspondents, etc.)
- Use user groups for permission management

### 8. Email Processing

**Configure Mail Accounts**:

1. Go to Settings → Mail Accounts
2. Add IMAP account (server, port, credentials)
3. Test connection

**Create Mail Rules**:

1. Go to Settings → Mail Rules
2. Define filters (from, subject, body, attachment filename)
3. Set actions (assign metadata, move, delete, etc.)
4. Rule processes matching emails automatically

### 9. Custom Fields

**Create Custom Fields**:

1. Go to Settings → Custom Fields
2. Create field with name and data type
3. Configure type-specific options (select choices, currency, etc.)

**Assign Values**:

- Assign custom field values to documents
- Use in filters and saved views
- Reference in workflow actions

**Data Types**:

- String, URL, Date, Boolean
- Integer, Float, Monetary
- Document Link, Select, Long Text

### 10. Advanced Features

**Nested Tags**:

- Create parent-child tag relationships
- Maximum depth: 5 levels
- Child tags automatically include parent tags

**Archive Serial Numbers**:

- Assign ASN for physical document tracking
- Filter and sort by ASN
- Useful for organizing physical archives

**Document Notes**:

- Add notes to documents
- Multiple notes per document
- Notes visible in document detail view

**Statistics**:

- View document counts by type
- Storage usage statistics
- Tag and correspondent distributions

## Common Workflows

### Workflow 1: Invoice Processing

1. Upload invoice via email or consumption folder
2. Workflow triggers on consumption
3. Automatic matching assigns correspondent and document type
4. Custom field "Amount" extracted and assigned
5. Tag "Invoices" assigned
6. Notification email sent

### Workflow 2: Document Organization

1. Bulk select documents by date range
2. Assign tags based on document type
3. Set storage path based on correspondent
4. Create saved view for quick access
5. Documents organized and easily findable

### Workflow 3: Collaboration

1. Create user groups (Accounting, Legal, etc.)
2. Set document permissions by group
3. Share specific documents via share links
4. Team members access documents based on permissions

## Tips and Best Practices

1. **Train Classifier Early**: Train automatic matching on initial document set for better suggestions
2. **Use Nested Tags**: Organize tags hierarchically (e.g., Finance → Invoices → 2024)
3. **Create Saved Views**: Save common filter combinations for quick access
4. **Set Up Workflows**: Automate repetitive metadata assignment tasks
5. **Regular Backups**: Backup database and document storage regularly
6. **Monitor Tasks**: Check task queue for processing errors
7. **Use Archive Serial Numbers**: Track physical document locations
8. **Configure Mail Rules**: Automate email-based document ingestion

## Troubleshooting

**Documents Not Processing**:

- Check Celery worker is running
- Verify task queue in Tasks view
- Check logs for errors

**Search Not Working**:

- Verify search index is updated
- Rebuild index if needed (management command)

**Permissions Issues**:

- Check object-level permissions
- Verify user/group assignments
- Review Django Guardian permissions

**Email Not Processing**:

- Verify mail account credentials
- Check mail rule filters
- Monitor mail processing tasks

## Next Steps

- Explore API documentation at `/api/schema/view/`
- Configure advanced settings (OCR, PDF conversion, etc.)
- Set up automated backups
- Customize UI settings and preferences
- Review security best practices in documentation

## Resources

- **Documentation**: https://docs.paperless-ngx.com
- **API Documentation**: `/api/schema/view/` (when running)
- **GitHub**: https://github.com/paperless-ngx/paperless-ngx
- **Community Support**: Matrix room, GitHub Discussions
