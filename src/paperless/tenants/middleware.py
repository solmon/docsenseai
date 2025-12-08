"""Tenant context middleware."""

import logging

from django.http import HttpResponseForbidden, JsonResponse

from paperless.tenants.models import Tenant
from paperless.tenants.utils import clear_current_tenant, get_current_tenant, set_current_tenant

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """Middleware to set tenant context from request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Clear any existing tenant context
        clear_current_tenant()

        # Set tenant context if user is authenticated
        if request.user.is_authenticated:
            # Check for X-Tenant-ID header
            tenant_id_header = request.headers.get("X-Tenant-ID")

            if tenant_id_header:
                try:
                    tenant_id = int(tenant_id_header)
                    tenant = Tenant.objects.filter(id=tenant_id, is_active=True, deleted_at__isnull=True).first()

                    if not tenant:
                        logger.warning(f"Invalid tenant ID in header: {tenant_id}")
                        return JsonResponse(
                            {"detail": "Invalid tenant ID."},
                            status=400,
                        )

                    # Verify tenant matches user's tenant association
                    user_tenant = getattr(request.user, "tenant", None)
                    if user_tenant and user_tenant.id != tenant.id:
                            logger.warning(
                                f"Tenant ID mismatch: user {request.user.id} has tenant {request.user.tenant.id}, "
                                f"but header specifies {tenant.id}"
                            )
                            return JsonResponse(
                                {"detail": "Tenant ID in header does not match your tenant association."},
                                status=403,
                            )

                    set_current_tenant(tenant)
                    logger.debug(
                        f"Tenant context set from header: {tenant.id} ({tenant.name}) for user {request.user.id}"
                    )

                except (ValueError, TypeError):
                    logger.warning(f"Invalid tenant ID format in header: {tenant_id_header}")
                    return JsonResponse(
                        {"detail": "Invalid tenant ID format."},
                        status=400,
                    )
            else:
                # No header - use user's tenant from authentication context
                user_tenant = getattr(request.user, "tenant", None)
                if user_tenant:
                    tenant = user_tenant
                    if tenant.is_active and not tenant.deleted_at:
                        set_current_tenant(tenant)
                        logger.debug(
                            f"Tenant context set from user: {tenant.id} ({tenant.name}) for user {request.user.id}"
                        )
                    else:
                        logger.warning(
                            f"User {request.user.id} has inactive tenant: {tenant.id} (is_active={tenant.is_active}, deleted_at={tenant.deleted_at})"
                        )
                        return JsonResponse(
                            {"detail": "Your tenant account is inactive."},
                            status=403,
                        )
                else:
                    # User has no tenant association
                    logger.warning(
                        f"User {request.user.id} ({request.user.username}) has no tenant association - access denied"
                    )
                    return JsonResponse(
                        {"detail": "No tenant association found. Please contact your administrator."},
                        status=403,
                    )

        response = self.get_response(request)

        # Clear tenant context after request
        clear_current_tenant()

        return response
