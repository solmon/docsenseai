"""Serializers for tenants app."""

from rest_framework import serializers

from paperless.tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""

    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "identifier",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_identifier(self, value):
        """Validate identifier is URL-safe and unique."""
        # Check uniqueness (excluding current instance)
        queryset = Tenant.objects.filter(identifier=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Identifier must be unique.")
        return value


class TenantDetailSerializer(TenantSerializer):
    """Detailed serializer for Tenant with additional fields."""

    user_count = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()

    class Meta(TenantSerializer.Meta):
        fields = TenantSerializer.Meta.fields + ["user_count", "document_count"]

    def get_user_count(self, obj):
        """Get number of users in this tenant."""
        return obj.users.count()

    def get_document_count(self, obj):
        """Get number of documents in this tenant."""
        # Import here to avoid circular imports
        from documents.models import Document

        return Document.objects.filter(tenant=obj).count()
