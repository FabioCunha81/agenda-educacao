import json
import smtplib
import urllib.error
import urllib.request

from django.conf import settings


RESEND_API_URL = "https://api.resend.com/emails"


def sanitize_email_error(error):
    message = str(error)
    secrets = [
        getattr(settings, "EMAIL_HOST_PASSWORD", ""),
        getattr(settings, "RESEND_API_KEY", ""),
    ]
    for secret in secrets:
        if secret:
            message = message.replace(secret, "***")
    return message[:500]


def send_resend_email(message):
    api_key = getattr(settings, "RESEND_API_KEY", "")
    if not api_key:
        return False, "RESEND_API_KEY nao configurada."

    payload = {
        "from": message.from_email,
        "to": list(message.to or []),
        "subject": message.subject,
        "text": message.body or "",
    }
    if getattr(message, "reply_to", None):
        payload["reply_to"] = list(message.reply_to)

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        RESEND_API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=getattr(settings, "EMAIL_TIMEOUT", 10)) as response:
            if 200 <= response.status < 300:
                return True, ""
            body = response.read().decode("utf-8", errors="replace")
            return False, f"Resend retornou HTTP {response.status}: {body[:300]}"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, f"Resend retornou HTTP {exc.code}: {body[:300]}"
    except Exception as exc:
        detail = sanitize_email_error(exc)
        if detail:
            detail = f"{exc.__class__.__name__}: {detail}"
        else:
            detail = exc.__class__.__name__
        return False, detail


def send_email_message(message):
    provider = getattr(settings, "EMAIL_PROVIDER", "smtp").strip().lower()
    if provider == "resend":
        return send_resend_email(message)

    if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
        return (
            False,
            "O backend de e-mail esta em modo console. Configure EMAIL_PROVIDER=resend ou EMAIL_BACKEND como smtp.EmailBackend para envio real.",
        )

    try:
        return message.send(fail_silently=False) > 0, ""
    except smtplib.SMTPException as exc:
        return False, sanitize_email_error(exc)
    except Exception as exc:
        detail = sanitize_email_error(exc)
        if detail:
            detail = f"{exc.__class__.__name__}: {detail}"
        else:
            detail = exc.__class__.__name__
        return False, detail
