import io
import logging
import threading
from dataclasses import dataclass

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
import os

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency guard
    genai = None

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - optional dependency guard
    fitz = None


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def is_allowed_image_file(uploaded_file):
    name = str(getattr(uploaded_file, "name", "") or "").lower()
    if not name or "." not in name:
        return False
    ext = f".{name.rsplit('.', 1)[-1]}"
    return ext in ALLOWED_IMAGE_EXTENSIONS


@dataclass
class EmailTemplate:
    subject: str
    body_text: str
    body_html: str


def build_notification_email(template_name, context):
    subject = render_to_string(f"emails/{template_name}_subject.txt", context).strip()
    body_text = render_to_string(f"emails/{template_name}.txt", context)
    body_html = render_to_string(f"emails/{template_name}.html", context)
    return EmailTemplate(subject=subject, body_text=body_text, body_html=body_html)


def send_templated_email(template_name, context, recipients):
    if not recipients:
        return

    template = build_notification_email(template_name, context)
    message = EmailMultiAlternatives(
        subject=template.subject,
        body=template.body_text,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=list(recipients),
    )
    message.attach_alternative(template.body_html, "text/html")
    message.send(fail_silently=False)


def send_templated_email_background(*, template_name, context, recipients):
    def _runner():
        try:
            send_templated_email(template_name, context, recipients)
        except Exception:
            logger.exception("Failed to send %s email", template_name)

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()


def generate_pdf_cover_image(digital_material):
    if getattr(digital_material, "cover_image", None):
        return False
    if not getattr(digital_material, "file", None):
        return False
    if fitz is None:
        logger.warning("PyMuPDF is not installed; skipping digital cover generation")
        return False

    file_name = str(getattr(digital_material.file, "name", "") or "").lower()
    if not file_name.endswith(".pdf"):
        return False

    try:
        digital_material.file.seek(0)
        raw_bytes = digital_material.file.read()
        if not raw_bytes:
            return False

        with fitz.open(stream=raw_bytes, filetype="pdf") as pdf:
            if pdf.page_count < 1:
                return False
            page = pdf.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            image_bytes = pix.tobytes("png")

        base_name = str(digital_material.id)
        digital_material.cover_image.save(
            f"{base_name}_cover.png",
            ContentFile(image_bytes),
            save=False,
        )
        digital_material.cover_generated_at = timezone.now()
        return True
    except Exception:
        logger.exception("Failed generating cover image for digital material %s", digital_material.pk)
        return False


def generate_material_description(title: str, author: str, max_output_tokens: int = 220):
    """Generate a concise catalog description for a material using configured Gemini models.

    Returns (description_text, used_model) on success, or (None, None) on failure.
    """
    title = str(title or "").strip()
    author = str(author or "").strip()

    if not title or not author:
        return None, None

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or genai is None:
        return None, None

    models_to_try = [
        os.getenv("GEMINI_DESCRIPTION_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro",
    ]

    prompt = (
        f"Title: {title}\n"
        f"Author: {author}\n\n"
        "Write a concise, helpful library catalog description (80-130 words). "
        "Use clear, neutral language and avoid inventing specific facts."
    )

    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        return None, None

    for model in models_to_try:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            text = response.text.strip() if getattr(response, "text", None) else ""
            if text:
                return text, model
        except Exception:
            logger.exception("Material description generation failed for model %s", model)
            continue

    return None, None
