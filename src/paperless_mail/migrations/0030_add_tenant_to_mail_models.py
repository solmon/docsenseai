"""Add tenant to mail models."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("paperless_mail", "0029_mailrule_pdf_layout"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailaccount",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mailaccount_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,  # Allow null initially for migration
            ),
        ),
        migrations.AddField(
            model_name="mailrule",
            name="tenant",
            field=models.ForeignKey(
                db_index=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mailrule_set",
                to="tenants.tenant",
                verbose_name="tenant",
                null=True,
            ),
        ),
    ]

