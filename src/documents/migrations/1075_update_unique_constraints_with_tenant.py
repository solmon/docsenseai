"""Update unique constraints to include tenant."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "1074_add_tenant_to_document_models"),
    ]

    operations = [
        # Remove old unique constraint on Document.checksum
        migrations.AlterUniqueTogether(
            name="document",
            unique_together=set(),
        ),
        # Add new unique constraint with tenant
        migrations.AddConstraint(
            model_name="document",
            constraint=models.UniqueConstraint(
                fields=["tenant", "checksum"],
                name="documents_document_unique_tenant_checksum",
            ),
        ),
        # Remove old unique constraints on Tag
        migrations.AlterUniqueTogether(
            name="tag",
            unique_together=set(),
        ),
        # Add new unique constraints with tenant for Tag
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name", "owner"],
                name="documents_tag_unique_tenant_name_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(
                condition=models.Q(owner__isnull=True),
                fields=["tenant", "name"],
                name="documents_tag_tenant_name_uniq",
            ),
        ),
        # Remove old unique constraints on Correspondent
        migrations.AlterUniqueTogether(
            name="correspondent",
            unique_together=set(),
        ),
        # Add new unique constraints with tenant for Correspondent
        migrations.AddConstraint(
            model_name="correspondent",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name", "owner"],
                name="documents_correspondent_unique_tenant_name_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="correspondent",
            constraint=models.UniqueConstraint(
                condition=models.Q(owner__isnull=True),
                fields=["tenant", "name"],
                name="documents_correspondent_tenant_name_uniq",
            ),
        ),
        # Remove old unique constraints on DocumentType
        migrations.AlterUniqueTogether(
            name="documenttype",
            unique_together=set(),
        ),
        # Add new unique constraints with tenant for DocumentType
        migrations.AddConstraint(
            model_name="documenttype",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name", "owner"],
                name="documents_documenttype_unique_tenant_name_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="documenttype",
            constraint=models.UniqueConstraint(
                condition=models.Q(owner__isnull=True),
                fields=["tenant", "name"],
                name="documents_documenttype_tenant_name_uniq",
            ),
        ),
        # Remove old unique constraints on StoragePath
        migrations.AlterUniqueTogether(
            name="storagepath",
            unique_together=set(),
        ),
        # Add new unique constraints with tenant for StoragePath
        migrations.AddConstraint(
            model_name="storagepath",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name", "owner"],
                name="documents_storagepath_unique_tenant_name_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="storagepath",
            constraint=models.UniqueConstraint(
                condition=models.Q(owner__isnull=True),
                fields=["tenant", "name"],
                name="documents_storagepath_tenant_name_uniq",
            ),
        ),
        # Remove old unique constraint on CustomField
        migrations.RemoveConstraint(
            model_name="customfield",
            name="documents_customfield_unique_name",
        ),
        # Add new unique constraint with tenant for CustomField
        migrations.AddConstraint(
            model_name="customfield",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name"],
                name="documents_customfield_unique_tenant_name",
            ),
        ),
    ]
