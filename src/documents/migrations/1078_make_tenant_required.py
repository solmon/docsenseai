"""Make tenant_id required (non-nullable) after population."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "1077_populate_tenant_ids"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tag_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="correspondent",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="correspondent_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="documenttype",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documenttype_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="storagepath",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="storagepath_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="customfield",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customfield_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="note",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="note_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="sharelink",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sharelink_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
    ]
