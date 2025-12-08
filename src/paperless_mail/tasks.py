import logging

from celery import shared_task

from paperless_mail.mail import MailAccountHandler
from paperless_mail.mail import MailError
from paperless_mail.models import MailAccount
from paperless_mail.models import MailRule
from paperless.tenants.models import Tenant
from paperless.tenants.utils import set_current_tenant

logger = logging.getLogger("paperless.mail.tasks")


@shared_task
def process_mail_accounts(account_ids: list[int] | None = None, tenant_id: int | None = None) -> str:
    """Process mail accounts with tenant context."""
    # Set tenant context if provided
    if tenant_id:
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            set_current_tenant(tenant)
        except Tenant.DoesNotExist:
            logger.warning(f"Tenant {tenant_id} not found, proceeding without tenant context")

    total_new_documents = 0
    accounts = (
        MailAccount.objects.filter(pk__in=account_ids)
        if account_ids
        else MailAccount.objects.all()
    )
    for account in accounts:
        if not MailRule.objects.filter(account=account, enabled=True).exists():
            logger.info(f"No rules enabled for account {account}. Skipping.")
            continue
        try:
            total_new_documents += MailAccountHandler().handle_mail_account(account)
        except MailError:
            logger.exception(f"Error while processing mail account {account}")

    if total_new_documents > 0:
        return f"Added {total_new_documents} document(s)."
    else:
        return "No new documents were added."
