"""Admin interface for tenants app."""

from django.contrib import admin

from paperless.tenants.models import Tenant, UserProfile


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""

    list_display = ["name", "identifier", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "identifier"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""

    list_display = ["user", "tenant", "user__email"]
    list_filter = ["tenant"]
    search_fields = ["user__username", "user__email", "tenant__name"]
    raw_id_fields = ["user", "tenant"]

    def user__email(self, obj):
        """Display user email."""
        return obj.user.email if obj.user else ""

    user__email.short_description = "Email"
