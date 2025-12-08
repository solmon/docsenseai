"""Management command for tenant migration."""

from django.core.management.base import BaseCommand
from django.db import transaction

from paperless.tenants.models import Tenant


class Command(BaseCommand):
    """Management command to migrate existing data to multi-tenant."""

    help = "Migrate existing single-tenant data to multi-tenant structure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without making changes",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Batch size for bulk updates (default: 10000)",
        )

    def handle(self, *args, **options):
        """Execute the migration."""
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get default tenant
        default_tenant = Tenant.objects.filter(identifier="default").first()
        if not default_tenant:
            self.stdout.write(self.style.ERROR("Default tenant not found. Run migrations first."))
            return

        self.stdout.write(f"Using default tenant: {default_tenant.name} (ID: {default_tenant.id})")

        # This command is mainly for verification and manual migration if needed
        # The actual migration is handled by Django migrations
        self.stdout.write(self.style.SUCCESS("Migration should be handled via Django migrations."))
        self.stdout.write("Run: python manage.py migrate")
