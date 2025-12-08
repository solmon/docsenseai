"""Initial migration for tenants app."""

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(help_text="Human-readable tenant name", max_length=255, verbose_name="name")),
                (
                    "identifier",
                    models.SlugField(
                        help_text="URL-safe identifier (e.g., 'acme-corp')",
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Identifier must contain only lowercase letters, numbers, hyphens, and underscores.",
                                regex="^[a-z0-9_-]+$",
                            )
                        ],
                        verbose_name="identifier",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, help_text="Whether tenant is active", verbose_name="is active")),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, help_text="Soft delete timestamp", null=True, verbose_name="deleted at"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "tenant",
                "verbose_name_plural": "tenants",
                "ordering": ("name",),
            },
        ),
    ]
