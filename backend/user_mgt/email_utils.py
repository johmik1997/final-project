import logging
import os
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def get_from_email():
    return getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)


def is_email_configured():
    backend = getattr(settings, "EMAIL_BACKEND", "")
    if "console" in str(backend).lower():
        return True
    user = getattr(settings, "EMAIL_HOST_USER", "") or os.getenv("EMAIL_HOST_USER", "") or ""
    password = getattr(settings, "EMAIL_HOST_PASSWORD", "") or os.getenv("EMAIL_HOST_PASSWORD", "") or ""
    return bool(str(user).strip() and str(password).strip())


def send_html_email(*, subject, body_text, body_html, recipients):
    recipients = [str(email).strip() for email in (recipients or []) if str(email).strip()]
    if not recipients:
        logger.warning("Skipped email (%s): no recipients", subject)
        return False

    from_email = get_from_email()
    if not from_email:
        logger.error("Skipped email (%s): DEFAULT_FROM_EMAIL is not configured", subject)
        return False

    if not is_email_configured():
        logger.error(
            "Skipped email (%s): set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env",
            subject,
        )
        return False

    message = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=from_email,
        to=recipients,
    )
    if body_html:
        message.attach_alternative(body_html, "text/html")
    message.send(fail_silently=False)
    return True


def send_templated_user_email(*, template_base, context, recipients):
    subject = render_to_string(f"emails/{template_base}_subject.txt", context).strip()
    body_text = render_to_string(f"emails/{template_base}.txt", context)
    body_html = render_to_string(f"emails/{template_base}.html", context)
    return send_html_email(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=recipients,
    )


def send_templated_user_email_background(*, template_base, context, recipients):
    def _runner():
        try:
            send_templated_user_email(
                template_base=template_base,
                context=context,
                recipients=recipients,
            )
        except Exception:
            logger.exception("Failed to send %s email", template_base)

    threading.Thread(target=_runner, daemon=True).start()
