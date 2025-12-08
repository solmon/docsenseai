# Quickstart Guide: Multi-Tenancy Setup

**Feature**: Multi-Tenancy Support
**Date**: 2025-01-27
**Status**: Fresh Installation Guide

## Overview

This quickstart guide provides step-by-step instructions for setting up Paperless-ngx with multi-tenancy support on a fresh installation. The system supports multiple tenants in a shared database with complete data isolation.

## Prerequisites

- Fresh Paperless-ngx installation (no existing data)
- Docker Compose setup (recommended)
- PostgreSQL or MariaDB database
- Redis for Celery task queue
- Super admin account for initial setup

## Initial Setup

### 1. Create First Tenant (Super Admin)

After initial installation and super user creation:

1. **Log in as super admin** (user with `is_superuser=True`)
2. **Navigate to Tenant Management**: Go to Settings → Tenants (or `/settings/tenants`)
3. **Create Default Tenant**:
   - Click "Create Tenant"
   - Name: "Default Tenant" (or your organization name)
   - Identifier: "default" (URL-safe, lowercase, hyphens/underscores only)
   - Click "Create"
4. **Verify tenant is active** (should be active by default)

### 2. Associate Users with Tenants

**For new users**:
- When creating a user, associate them with a tenant via UserProfile
- User must have at least one tenant association to access the system

**For existing super admin**:
- Associate super admin user with default tenant via UserProfile
- Super admin can access all tenants for management, but needs a default tenant for normal operations

### 3. Configure API Version

**Frontend Configuration**:
- Update `src-ui/src/environments/environment.prod.ts` to use API version 10
- Set `apiVersion: '10'` in environment configuration

**Backend Configuration**:
- Add version 10 to `ALLOWED_VERSIONS` in `src/paperless/settings.py`
- Set `DEFAULT_VERSION = "10"` for new installations

## User Workflows

### Regular User - Single Tenant

1. **Log in** with user credentials
2. **Automatic Tenant Assignment**: If user has only one tenant association, they are automatically assigned to that tenant
3. **Use Application**: All operations are automatically scoped to their tenant
4. **No tenant selection needed**: UI does not show tenant selector

### Regular User - Multiple Tenants

1. **Log in** with user credentials
2. **Tenant Selection**: If user has multiple tenant associations, tenant selector appears
3. **Select Tenant**: Choose tenant from dropdown/list
4. **Use Application**: All operations scoped to selected tenant
5. **Switch Tenant**: Can switch tenants during session via user menu

### Super Admin - Tenant Management

1. **Log in** as super admin
2. **Access Tenant Management**: Navigate to Settings → Tenants
3. **View All Tenants**: See list of all tenants with status (active/inactive)
4. **Create Tenant**:
   - Click "Create Tenant" button
   - Enter name and identifier
   - Click "Create"
5. **Manage Tenant**:
   - Click on tenant to view details
   - Edit name or identifier
   - Activate/deactivate tenant
   - Soft delete tenant (marks as deleted, retains data)
6. **Monitor Tenant Status**: View active/inactive status and creation dates

## Tenant Operations

### Creating a Tenant

**Requirements**:
- Super admin access required
- Unique identifier (URL-safe: lowercase letters, numbers, hyphens, underscores)
- Name (human-readable)

**Steps**:
1. Go to Settings → Tenants
2. Click "Create Tenant"
3. Enter tenant name (e.g., "Acme Corporation")
4. Enter identifier (e.g., "acme-corp")
5. Click "Create"

**Result**: New tenant created and active. Users can be associated with this tenant.

### Activating/Deactivating a Tenant

**Activate**:
1. Go to Settings → Tenants
2. Find inactive tenant
3. Click "Activate" button
4. Tenant becomes active, users can access

**Deactivate**:
1. Go to Settings → Tenants
2. Find active tenant
3. Click "Deactivate" button
4. Tenant becomes inactive, active user sessions are invalidated

**Impact**:
- Active users logged out immediately
- Users cannot access system until tenant is reactivated
- Data is retained (soft deactivation)

### Deleting a Tenant

**Soft Delete**:
1. Go to Settings → Tenants
2. Find tenant to delete
3. Click "Delete" button
4. Confirm deletion
5. Tenant is soft-deleted (marked as deleted, data retained)

**Hard Delete** (if implemented):
- Permanently removes tenant and all associated data
- Irreversible operation
- Typically requires additional confirmation

## Data Isolation Verification

### Test Data Isolation

1. **Create Tenant A and Tenant B**
2. **Create users for each tenant**
3. **Log in as Tenant A user**:
   - Create documents, tags, correspondents
   - Verify data is created
4. **Log in as Tenant B user**:
   - Verify Tenant A's data is not visible
   - Create different documents, tags, correspondents
   - Verify Tenant B's data is separate
5. **Switch back to Tenant A**:
   - Verify Tenant B's data is not visible
   - Verify Tenant A's data is still present

### Verify API Tenant Scoping

1. **Get API token** for Tenant A user
2. **Make API request with X-Tenant-ID header**:
   ```bash
   curl -H "Authorization: Token <token>" \
        -H "X-Tenant-ID: 1" \
        -H "Accept: application/json; version=10" \
        https://your-instance/api/documents/
   ```
3. **Verify only Tenant A documents returned**
4. **Try accessing Tenant B document ID**:
   ```bash
   curl -H "Authorization: Token <token>" \
        -H "X-Tenant-ID: 1" \
        -H "Accept: application/json; version=10" \
        https://your-instance/api/documents/<tenant_b_doc_id>/
   ```
5. **Verify access denied** (404 or 403)

## Common Scenarios

### Scenario 1: Single Organization Setup

**Use Case**: One organization, one tenant

**Setup**:
1. Create one tenant (e.g., "My Organization")
2. Associate all users with this tenant
3. Users automatically assigned to tenant (no selection needed)
4. All operations scoped to this tenant

**Result**: System behaves like single-tenant, but with multi-tenant architecture in place.

### Scenario 2: Multiple Organizations

**Use Case**: Multiple organizations, separate tenants

**Setup**:
1. Create tenant for each organization
2. Associate users with their organization's tenant
3. Users see only their organization's data
4. Super admin can manage all tenants

**Result**: Complete data isolation between organizations.

### Scenario 3: User Belongs to Multiple Tenants

**Use Case**: User needs access to multiple tenants (future enhancement)

**Setup**:
1. Associate user with multiple tenants (if supported)
2. User sees tenant selector on login
3. User selects tenant for current session
4. User can switch tenants during session

**Result**: User can work with multiple tenants, one at a time.

## Troubleshooting

### User Cannot Access System

**Symptoms**: User gets "No tenant association" error

**Solution**:
1. Verify user has UserProfile with tenant association
2. Verify tenant is active (`is_active=True`)
3. Verify tenant is not soft-deleted (`deleted_at is null`)
4. Associate user with active tenant if missing

### Tenant Selection Not Appearing

**Symptoms**: User with multiple tenants doesn't see selector

**Solution**:
1. Verify user has multiple tenant associations
2. Check frontend tenant selector component is implemented
3. Verify tenant context service is initialized
4. Check browser console for errors

### Data Visible Across Tenants

**Symptoms**: User sees data from other tenant (CRITICAL)

**Solution**:
1. Verify TenantMiddleware is configured in MIDDLEWARE
2. Verify TenantManager is used for all tenant-specific models
3. Verify X-Tenant-ID header is being sent
4. Check database queries include tenant filter
5. Review logs for tenant context issues

### Super Admin Cannot Access Tenant Management

**Symptoms**: 403 Forbidden on tenant endpoints

**Solution**:
1. Verify user has `is_superuser=True`
2. Verify super admin permission check in viewset
3. Check API version is 10
4. Verify authentication token is valid

### Celery Tasks Not Tenant-Scoped

**Symptoms**: Tasks process data from wrong tenant

**Solution**:
1. Verify tasks accept `tenant_id` parameter
2. Verify tasks call `set_current_tenant()` at start
3. Verify tasks call `clear_current_tenant()` at end
4. Check task invocation includes tenant_id

## Best Practices

1. **Tenant Naming**: Use clear, descriptive names (organization names)
2. **Identifier Format**: Use lowercase, hyphens for readability (e.g., "acme-corp" not "AcmeCorp")
3. **User Association**: Associate users with tenants during user creation
4. **Tenant Activation**: Keep tenants active unless decommissioning
5. **Soft Delete**: Use soft delete for tenants to retain data for recovery
6. **Monitoring**: Monitor tenant activity and data growth
7. **Backup**: Regular backups include all tenant data (shared database)
8. **Testing**: Test data isolation regularly to ensure no cross-tenant leakage

## Security Considerations

1. **Tenant Validation**: Always validate tenant ID against user's association
2. **Super Admin Access**: Restrict tenant management to super admin only
3. **Header Validation**: Verify X-Tenant-ID header in middleware
4. **Query Filtering**: Never bypass TenantManager for tenant-specific data
5. **Task Security**: Always pass tenant_id explicitly to Celery tasks
6. **Audit Logging**: Log tenant access and management operations (if audit log enabled)

## Next Steps

- Review API documentation at `/api/schema/view/` (version 10)
- Set up user associations for all users
- Configure tenant-specific settings if needed
- Test data isolation thoroughly
- Monitor system performance with multiple tenants

## Resources

- **API Documentation**: `/api/schema/view/` (when running, version 10)
- **Core System Spec**: `specs/000-paperless-ngx-core/spec.md`
- **Data Model**: `specs/001-multi-tenancy/data-model.md`
- **API Contracts**: `specs/001-multi-tenancy/contracts/api-endpoints.md`

