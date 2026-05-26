import io
import logging
import re
import threading
from dataclasses import dataclass

import requests
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


def _normalize_isbn_digits(code: str) -> str:
    digits = re.sub(r"\D", "", str(code or ""))
    if len(digits) in (10, 13):
        return digits
    return ""


def _map_open_library_genre(subjects):
    if not subjects:
        return ""
    joined = " ".join(str(item) for item in subjects).lower()
    mapping = {
        "fiction": "FICTION",
        "history": "HISTORY",
        "science": "SCIENCE",
        "biograph": "BIOGRAPHY",
        "technolog": "TECHNOLOGY",
        "computer": "TECHNOLOGY",
        "education": "EDUCATIONAL",
    }
    for needle, genre in mapping.items():
        if needle in joined:
            return genre
    return "OTHER"


def lookup_book_metadata(code: str):
    """Resolve book metadata from an ISBN or library barcode string."""
    raw = str(code or "").strip()
    if not raw:
        return {"found": False, "source": None, "data": {}}

    from material_mgt.models import PhysicalMaterial

    material = (
        PhysicalMaterial.objects.filter(barcode__iexact=raw).first()
        or PhysicalMaterial.objects.filter(isbn__iexact=raw).first()
    )
    if material:
        return {
            "found": True,
            "source": "library",
            "data": {
                "title": material.title,
                "author": material.author,
                "isbn": material.isbn or "",
                "category": material.category or "BOOK",
                "genre": material.genre or "OTHER",
                "published_date": material.published_date.isoformat() if material.published_date else "",
                "language": material.language or "",
                "department": material.department or "",
                "barcode": material.barcode or "",
            },
        }

    isbn = _normalize_isbn_digits(raw)
    if not isbn:
        return {"found": False, "source": None, "data": {}}

    try:
        response = requests.get(
            "https://openlibrary.org/api/books",
            params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
            timeout=8,
        )
        response.raise_for_status()
        payload = response.json() or {}
        book = payload.get(f"ISBN:{isbn}") or {}
        if not book:
            return {"found": False, "source": "openlibrary", "data": {"isbn": isbn}}

        authors = book.get("authors") or []
        author_names = ", ".join(
            author.get("name", "").strip()
            for author in authors
            if isinstance(author, dict) and author.get("name")
        )
        publish_date = str(book.get("publish_date") or "").strip()
        if publish_date and len(publish_date) >= 4:
            publish_date = f"{publish_date[:4]}-01-01"

        return {
            "found": True,
            "source": "openlibrary",
            "data": {
                "title": str(book.get("title") or "").strip(),
                "author": author_names,
                "isbn": isbn,
                "category": "BOOK",
                "genre": _map_open_library_genre(book.get("subjects")),
                "published_date": publish_date,
                "language": "",
                "department": "",
                "barcode": "",
            },
        }
    except Exception:
        logger.exception("Open Library lookup failed for ISBN %s", isbn)
        return {"found": False, "source": "openlibrary", "data": {"isbn": isbn}}
