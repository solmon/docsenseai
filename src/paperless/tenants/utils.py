"""Thread-local tenant context utilities."""

import threading

_thread_locals = threading.local()


def set_current_tenant(tenant):
    """Set the current tenant for this thread."""
    _thread_locals.current_tenant = tenant


def get_current_tenant():
    """Get the current tenant for this thread."""
    return getattr(_thread_locals, "current_tenant", None)


def clear_current_tenant():
    """Clear the current tenant for this thread."""
    if hasattr(_thread_locals, "current_tenant"):
        delattr(_thread_locals, "current_tenant")
