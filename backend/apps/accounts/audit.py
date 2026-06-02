from .models import AuditLog


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or None


def log_audit(request, action, module, description, metadata=None, user=None):
    actor = user
    if actor is None and getattr(request, "user", None) and request.user.is_authenticated:
        actor = request.user
    return AuditLog.objects.create(
        user=actor,
        action=action,
        module=module,
        description=description[:255],
        metadata=metadata or {},
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
