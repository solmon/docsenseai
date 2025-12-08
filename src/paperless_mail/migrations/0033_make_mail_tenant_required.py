"""Make tenant_id required for mail models."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("paperless_mail", "0032_populate_mail_tenant_ids"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mailaccount",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mailaccount_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
        migrations.AlterField(
            model_name="mailrule",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mailrule_set",
                to="tenants.tenant",
                verbose_name="tenant",
            ),
        ),
    ]
