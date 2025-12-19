# Quickstart Guide: Multiple Storage Backends

**Feature**: Multiple Storage Backends
**Date**: 2025-01-27
**Phase**: 1 - Design & Contracts

## Overview

This guide explains how to configure and use multiple storage backends in Paperless-ngx. The storage backend abstraction allows you to choose between local filesystem storage (default) and Azure Blob Storage for document storage.

## Prerequisites

- Paperless-ngx installation (Python 3.10+)
- For Azure Blob Storage:
  - Azure Storage account
  - Connection string or managed identity access
  - Container name (will be created if it doesn't exist)

## Configuration

### Filesystem Storage (Default)

No configuration required. The application defaults to filesystem storage using existing directory structure:

```bash
# No environment variables needed - uses default filesystem storage
# Documents stored in: {MEDIA_ROOT}/documents/originals/
# Archives stored in: {MEDIA_ROOT}/documents/archive/
# Thumbnails stored in: {MEDIA_ROOT}/documents/thumbnails/
```

### Azure Blob Storage

Configure Azure Blob Storage by setting the following environment variables:

```bash
# Required: Set storage backend to Azure Blob Storage
export PAPERLESS_STORAGE_BACKEND=azure_blob

# Required: Azure Storage account connection string
export PAPERLESS_AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=your_account;AccountKey=your_key;EndpointSuffix=core.windows.net"

# Required: Azure Blob Storage container name
export PAPERLESS_AZURE_CONTAINER_NAME=paperless-documents
```

**Note**: The container will be created automatically if it doesn't exist.

## Getting Started

### Step 1: Choose Storage Backend

Decide which storage backend to use:
- **Filesystem**: Default, no configuration needed
- **Azure Blob Storage**: Requires Azure account and configuration

### Step 2: Configure Environment Variables

If using Azure Blob Storage, set the required environment variables (see Configuration section above).

### Step 3: Start Application

Start the Paperless-ngx application as usual:

```bash
python manage.py migrate
python manage.py runserver
```

The application will:
1. Validate storage backend configuration at startup
2. Initialize the selected storage backend
3. Create containers/directories if needed
4. Be ready to store documents

### Step 4: Verify Configuration

Check application logs for storage backend initialization messages:

```
INFO: Storage backend initialized: filesystem
# or
INFO: Storage backend initialized: azure_blob (container: paperless-documents)
```

## Usage

### Document Operations

All document operations work identically regardless of storage backend:

- **Upload**: Documents uploaded via API or UI are stored in the configured backend
- **Retrieve**: Documents are retrieved from the configured backend
- **Delete**: Documents are deleted from the configured backend
- **Archive**: Archive files are stored in the configured backend
- **Thumbnails**: Thumbnails are stored in the configured backend

### Switching Storage Backends

To switch storage backends:

1. Stop the application
2. Update environment variables (if switching to Azure)
3. Restart the application

**Important**: Existing documents remain in the previous storage backend. Migration tools may be needed to move documents between backends (not included in this feature).

## Troubleshooting

### Configuration Errors

**Error**: "Invalid storage backend '{value}'. Must be 'filesystem' or 'azure_blob'."

**Solution**: Check that `PAPERLESS_STORAGE_BACKEND` is set to 'filesystem' or 'azure_blob'.

---

**Error**: "Azure Blob Storage backend requires PAPERLESS_AZURE_CONNECTION_STRING environment variable."

**Solution**: Set the `PAPERLESS_AZURE_CONNECTION_STRING` environment variable with a valid Azure connection string.

---

**Error**: "Azure Blob Storage backend requires PAPERLESS_AZURE_CONTAINER_NAME environment variable."

**Solution**: Set the `PAPERLESS_AZURE_CONTAINER_NAME` environment variable with a valid container name.

---

**Error**: "Failed to connect to Azure Blob Storage: {error details}"

**Solution**:
- Verify connection string is correct
- Check network connectivity to Azure
- Verify Azure Storage account is accessible
- Check Azure account permissions

### Storage Operation Errors

**Error**: File not found when retrieving document

**Solution**:
- Verify document exists in storage backend
- Check storage backend logs for details
- Verify path resolution is working correctly

**Error**: Permission denied when storing document

**Solution**:
- For filesystem: Check directory permissions
- For Azure: Verify connection string has write permissions
- Check application user has appropriate access

## Examples

### Docker Compose Configuration

```yaml
services:
  webserver:
    environment:
      - PAPERLESS_STORAGE_BACKEND=azure_blob
      - PAPERLESS_AZURE_CONNECTION_STRING=${AZURE_CONNECTION_STRING}
      - PAPERLESS_AZURE_CONTAINER_NAME=paperless-documents
```

### Environment File (.env)

```bash
# Storage Backend Configuration
PAPERLESS_STORAGE_BACKEND=azure_blob
PAPERLESS_AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net
PAPERLESS_AZURE_CONTAINER_NAME=paperless-documents
```

## Best Practices

1. **Backup**: Ensure storage backend backups are configured (Azure automatic backups, filesystem backups)

2. **Security**:
   - Store connection strings securely (environment variables, secrets management)
   - Use managed identity for Azure when possible (future enhancement)
   - Restrict container access permissions

3. **Monitoring**:
   - Monitor storage backend health
   - Set up alerts for storage failures
   - Review storage operation logs regularly

4. **Performance**:
   - Consider Azure region proximity for latency
   - Monitor storage operation performance
   - Use appropriate Azure storage tier (Hot, Cool, Archive)

5. **Testing**:
   - Test storage backend configuration in development first
   - Verify document operations work correctly
   - Test error handling scenarios

## Next Steps

- Review [data-model.md](./data-model.md) for detailed entity relationships
- Review [research.md](./research.md) for technology decisions
- Review [plan.md](./plan.md) for implementation details

