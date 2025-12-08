"""Add tenant to document models."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "1073_migrate_workflow_title_jinja"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,  # Allow null initially for migration
            ),
        ),
        migrations.AddField(
            model_name="tag",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tag_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="correspondent",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="correspondent_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="documenttype",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documenttype_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="storagepath",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="storagepath_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="customfield",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customfield_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="note",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="note_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="sharelink",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sharelink_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
    ]
