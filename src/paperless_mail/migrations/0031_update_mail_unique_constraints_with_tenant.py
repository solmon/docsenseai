"""Update unique constraints to include tenant for mail models."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("paperless_mail", "0030_add_tenant_to_mail_models"),
    ]

    operations = [
        # Remove old unique constraint on MailAccount.name
        migrations.AlterUniqueTogether(
            name="mailaccount",
            unique_together=set(),
        ),
        # Add new unique constraint with tenant for MailAccount
        migrations.AddConstraint(
            model_name="mailaccount",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name"],
                name="paperless_mail_mailaccount_unique_tenant_name",
            ),
        ),
        # Remove old unique constraints on MailRule
        migrations.AlterUniqueTogether(
            name="mailrule",
            unique_together=set(),
        ),
        # Add new unique constraints with tenant for MailRule
        migrations.AddConstraint(
            model_name="mailrule",
            constraint=models.UniqueConstraint(
                fields=["tenant", "name", "owner"],
                name="paperless_mail_mailrule_unique_tenant_name_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="mailrule",
            constraint=models.UniqueConstraint(
                condition=models.Q(owner__isnull=True),
                fields=["tenant", "name"],
                name="paperless_mail_mailrule_tenant_name_unique",
            ),
        ),
    ]
