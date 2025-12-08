"""Tenant models."""

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from paperless.tenants.managers import TenantManager


class Tenant(models.Model):
    """Represents an organizational unit that owns and isolates data."""

    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Human-readable tenant name"),
    )
    identifier = models.SlugField(
        _("identifier"),
        unique=True,
        max_length=255,
        help_text=_("URL-safe identifier (e.g., 'acme-corp')"),
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_-]+$",
                message=_("Identifier must contain only lowercase letters, numbers, hyphens, and underscores."),
            )
        ],
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Whether tenant is active"),
    )
    deleted_at = models.DateTimeField(
        _("deleted at"),
        null=True,
        blank=True,
        help_text=_("Soft delete timestamp"),
    )
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("tenant")
        verbose_name_plural = _("tenants")
        ordering = ("name",)

    def __str__(self):
        return self.name

    def clean(self):
        """Validate tenant data."""
        from django.core.exceptions import ValidationError

        if not self.name:
            raise ValidationError({"name": _("Name cannot be empty.")})

        if not self.identifier:
            raise ValidationError({"identifier": _("Identifier cannot be empty.")})

        # Check identifier uniqueness (excluding self)
        if self.pk:
            if Tenant.objects.filter(identifier=self.identifier).exclude(pk=self.pk).exists():
                raise ValidationError({"identifier": _("Identifier must be unique.")})
        else:
            if Tenant.objects.filter(identifier=self.identifier).exists():
                raise ValidationError({"identifier": _("Identifier must be unique.")})

    def delete(self, using=None, keep_parents=False):
        """Soft delete the tenant."""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)

    def hard_delete(self):
        """Permanently delete the tenant."""
        super().delete()


class TenantModel(models.Model):
    """Abstract base class for tenant-specific models."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        db_index=True,
        verbose_name=_("tenant"),
    )

    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Auto-assign tenant from context if not set."""
        from paperless.tenants.utils import get_current_tenant

        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
            else:
                raise ValueError("Tenant context not set. Cannot save tenant-specific model without tenant.")
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """User profile to extend User model with tenant association."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        verbose_name=_("tenant"),
        help_text=_("Tenant this user belongs to"),
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        return f"{self.user.username} - {self.tenant.name if self.tenant else 'No tenant'}"


# Add property to User model for easy access
def user_get_tenant(self):
    """Get tenant for user via profile."""
    if hasattr(self, "profile") and self.profile:
        return self.profile.tenant
    return None


User.add_to_class("tenant", property(user_get_tenant))
