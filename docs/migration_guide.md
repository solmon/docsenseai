# Multi-Tenant Migration Guide

This guide provides instructions for migrating existing single-tenant paperless-ngx installations to multi-tenant architecture.

## Prerequisites

- Backup your database before starting migration
- Ensure you have sufficient disk space
- Plan for a maintenance window (migration can take time for large databases)

## Migration Process

### Step 1: Backup Database

**Critical**: Always backup before migration.

```bash
# PostgreSQL
pg_dump paperless > backup_$(date +%Y%m%d).sql

# MariaDB
mysqldump paperless > backup_$(date +%Y%m%d).sql
```

### Step 2: Run Migrations

Execute Django migrations in order:

```bash
python src/manage.py migrate tenants
python src/manage.py migrate paperless
python src/manage.py migrate documents
python src/manage.py migrate paperless_mail
```

The migrations will:
1. Create Tenant model and UserProfile model
2. Add tenant_id columns to all tenant-specific tables (nullable initially)
3. Create default tenant
4. Associate existing users with default tenant
5. Populate tenant_id for all existing data
6. Update unique constraints to include tenant_id
7. Make tenant_id required (non-nullable)
8. Add composite indexes for performance

### Step 3: Verify Migration

After migration completes:

1. Verify default tenant exists:
   ```python
   python src/manage.py shell
   >>> from paperless.tenants.models import Tenant
   >>> Tenant.objects.filter(identifier="default").exists()
   True
   ```

2. Verify users are associated:
   ```python
   >>> from django.contrib.auth.models import User
   >>> User.objects.filter(profile__tenant__isnull=False).count()
   # Should match total user count
   ```

3. Verify data has tenant_id:
   ```python
   >>> from documents.models import Document
   >>> Document.objects.filter(tenant__isnull=True).count()
   0  # Should be zero
   ```

4. Test the application:
   - Log in with existing user
   - Verify documents are visible
   - Create new document
   - Verify tenant isolation works

## Rollback Procedure

If migration fails and rollback is needed:

1. **Stop the application**

2. **Restore database from backup**:
   ```bash
   # PostgreSQL
   psql paperless < backup_YYYYMMDD.sql

   # MariaDB
   mysql paperless < backup_YYYYMMDD.sql
   ```

3. **Remove tenant app from INSTALLED_APPS** in `src/paperless/settings.py`

4. **Restart application**

**Note**: Rollback removes tenant_id columns but preserves all existing data.

## Performance Considerations

- Migration uses bulk updates for efficiency
- For very large databases (100,000+ records), migration may take 30+ minutes
- Composite indexes are created after data population to speed up migration
- Monitor database performance during migration

## Troubleshooting

### Issue: Migration fails with constraint violation

**Solution**: Check for existing data that violates new unique constraints. The migration should handle this, but if it fails, you may need to clean up duplicate data first.

### Issue: Users cannot log in after migration

**Solution**: Verify users are associated with default tenant:
```python
from django.contrib.auth.models import User
from paperless.tenants.models import Tenant, UserProfile

default_tenant = Tenant.objects.get(identifier="default")
for user in User.objects.filter(profile__isnull=True):
    UserProfile.objects.create(user=user, tenant=default_tenant)
```

### Issue: Documents not visible after migration

**Solution**: Verify documents have tenant_id:
```python
from documents.models import Document
from paperless.tenants.models import Tenant

default_tenant = Tenant.objects.get(identifier="default")
Document.objects.filter(tenant__isnull=True).update(tenant=default_tenant)
```

## Post-Migration

After successful migration:

1. Test all core functionality
2. Verify tenant isolation works correctly
3. Monitor application performance
4. Update API clients to include X-Tenant-ID header (optional)
5. Create additional tenants as needed

## Support

For issues during migration:
- Check application logs for detailed error messages
- Review migration output for warnings
- Restore from backup if needed
- Consult troubleshooting section above
