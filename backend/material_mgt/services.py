import io
import json
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
    # Some scanners return UPC/EAN payloads with extra prefix/suffix digits.
    match = re.search(r"(97[89]\d{10})", digits)
    if match:
        return match.group(1)
    if len(digits) > 13:
        tail = digits[-13:]
        if tail.startswith(("978", "979")):
            return tail
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


def _extract_published_date(raw_value):
    raw = str(raw_value or "").strip()
    if not raw:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw
    if re.fullmatch(r"\d{4}-\d{2}", raw):
        return f"{raw}-01"
    match = re.search(r"(1[5-9]\d{2}|20\d{2}|21\d{2})", raw)
    if match:
        return f"{match.group(1)}-01-01"
    return ""


def _normalize_language_name(raw_language):
    value = str(raw_language or "").strip()
    if not value:
        return ""
    mapping = {
        "en": "English",
        "eng": "English",
        "am": "Amharic",
        "amh": "Amharic",
    }
    return mapping.get(value.lower(), value.title())


def _map_google_books_genre(categories):
    if not categories:
        return "OTHER"
    return _map_open_library_genre(categories)


def _extract_people_names(raw_value):
    if isinstance(raw_value, list):
        names = [_extract_people_names(item) for item in raw_value]
        return ", ".join(name for name in names if name)
    if isinstance(raw_value, dict):
        return str(raw_value.get("name") or raw_value.get("author") or "").strip()
    return str(raw_value or "").strip()


_BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
_OL_HEADERS = {"User-Agent": _BROWSER_UA, "Accept": "application/json"}


def _build_external_lookup_payload(*, source, isbn, title="", author="", genre="OTHER", published_date="", language="", publisher="", description=""):
    title = str(title or "").strip()
    if _is_invalid_book_title(title):
        return {"found": False, "source": source, "data": {"isbn": isbn}}
    return {
        "found": bool(title),
        "source": source,
        "data": {
            "title": title,
            "author": author,
            "isbn": isbn,
            "category": "BOOK",
            "genre": genre or "OTHER",
            "published_date": published_date,
            "language": language,
            "department": "",
            "barcode": "",
            "publisher": publisher,
            "description": description,
            "total_copies": 1,
            "condition": "NEW",
            "location": "STACK",
            "can_borrow": True,
        },
    }


def _lookup_open_library_isbn_json(isbn: str):
    """Primary Open Library lookup via structured ISBN JSON API."""
    try:
        response = requests.get(
            f"https://openlibrary.org/isbn/{isbn}.json",
            headers=_OL_HEADERS,
            timeout=8,
            allow_redirects=True,
        )
        if response.status_code == 404:
            return {"found": False, "source": "openlibrary", "data": {"isbn": isbn}}
        response.raise_for_status()
        payload = response.json() or {}

        title = str(payload.get("title") or "").strip()
        authors = payload.get("authors") or []
        author_keys = [item.get("key") for item in authors if isinstance(item, dict) and item.get("key")]
        author_names = []
        for author_key in author_keys[:3]:
            author_response = requests.get(
                f"https://openlibrary.org{author_key}.json",
                headers=_OL_HEADERS,
                timeout=6,
                allow_redirects=True,
            )
            if author_response.ok:
                author_payload = author_response.json() or {}
                name = str(author_payload.get("name") or "").strip()
                if name:
                    author_names.append(name)

        publish_dates = payload.get("publish_dates") or []
        published_date = _extract_published_date(publish_dates[0] if publish_dates else payload.get("publish_date"))
        publishers = payload.get("publishers") or []
        publisher_name = ", ".join(str(name).strip() for name in publishers[:2] if str(name).strip())
        languages = payload.get("languages") or []
        language = ""
        if languages and isinstance(languages[0], dict):
            language = _normalize_language_name(str(languages[0].get("key", "")).split("/")[-1])

        return _build_external_lookup_payload(
            source="openlibrary",
            isbn=isbn,
            title=title,
            author=", ".join(author_names),
            genre=_map_open_library_genre(payload.get("subjects")),
            published_date=published_date,
            language=language,
            publisher=publisher_name,
            description=str(payload.get("description") or "").strip(),
        )
    except Exception:
        logger.exception("Open Library ISBN JSON lookup failed for ISBN %s", isbn)
        return {"found": False, "source": "openlibrary", "data": {"isbn": isbn}}


def _lookup_open_library_search_metadata(isbn: str):
    try:
        response = requests.get(
            "https://openlibrary.org/search.json",
            params={"isbn": isbn, "limit": 1},
            headers=_OL_HEADERS,
            timeout=8,
            allow_redirects=True,
        )
        response.raise_for_status()
        payload = response.json() or {}
        doc = (payload.get("docs") or [None])[0] or {}
        title = str(doc.get("title") or "").strip()
        if not title:
            return {"found": False, "source": "openlibrary_search", "data": {"isbn": isbn}}

        publish_year = doc.get("first_publish_year")
        published_date = f"{publish_year}-01-01" if publish_year else ""
        author = ", ".join(str(name).strip() for name in (doc.get("author_name") or []) if str(name).strip())
        language_codes = doc.get("language") or []
        language = _normalize_language_name(language_codes[0]) if language_codes else ""
        publisher = ", ".join(str(name).strip() for name in (doc.get("publisher") or [])[:2] if str(name).strip())

        return _build_external_lookup_payload(
            source="openlibrary_search",
            isbn=isbn,
            title=title,
            author=author,
            genre=_map_open_library_genre(doc.get("subject")),
            published_date=published_date,
            language=language,
            publisher=publisher,
        )
    except Exception:
        logger.exception("Open Library search lookup failed for ISBN %s", isbn)
        return {"found": False, "source": "openlibrary_search", "data": {"isbn": isbn}}


def _lookup_google_books_metadata(isbn: str):
    try:
        api_key = os.getenv("GOOGLE_BOOKS_API_KEY", "").strip()
        params: dict = {"q": f"isbn:{isbn}", "maxResults": 1}
        if api_key:
            params["key"] = api_key
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=params,
            headers={"User-Agent": _BROWSER_UA},
            timeout=8,
        )
        response.raise_for_status()
        payload = response.json() or {}
        item = (payload.get("items") or [None])[0] or {}
        volume_info = item.get("volumeInfo") or {}
        if not volume_info:
            return {"found": False, "source": "google_books", "data": {"isbn": isbn}}

        authors = volume_info.get("authors") or []
        description = str(volume_info.get("description") or "").strip()

        return _build_external_lookup_payload(
            source="google_books",
            isbn=isbn,
            title=str(volume_info.get("title") or "").strip(),
            author=", ".join(str(author).strip() for author in authors if str(author).strip()),
            genre=_map_google_books_genre(volume_info.get("categories")),
            published_date=_extract_published_date(volume_info.get("publishedDate")),
            language=_normalize_language_name(volume_info.get("language")),
            publisher=str(volume_info.get("publisher") or "").strip(),
            description=description,
        )
    except Exception:
        logger.exception("Google Books lookup failed for ISBN %s", isbn)
        return {"found": False, "source": "google_books", "data": {"isbn": isbn}}


_INVALID_BOOK_TITLE_PATTERNS = (
    "find-more-books.com",
    "compare book prices",
    "we love books",
    "happy you are here",
    "hello! happy",
    "captcha",
    "bot detected",
    "verify you are human",
    "access denied",
    "eurobuch",
    "sign in to continue",
    "cloudflare",
    "security check",
    "anti-bot",
    "are you a robot",
)


def _is_invalid_book_title(value: str) -> bool:
    normalized = str(value or "").strip().lower()
    if not normalized or len(normalized) < 2:
        return True
    if len(normalized) > 220:
        return True
    return any(pattern in normalized for pattern in _INVALID_BOOK_TITLE_PATTERNS)


def _lookup_external_isbn_metadata(isbn: str):
    """Resolve ISBN metadata using trusted public APIs only (no HTML scraping)."""
    google_result = _lookup_google_books_metadata(isbn)
    if google_result.get("found"):
        return google_result

    search_result = _lookup_open_library_search_metadata(isbn)
    if search_result.get("found"):
        return search_result

    isbn_json_result = _lookup_open_library_isbn_json(isbn)
    if isbn_json_result.get("found"):
        return isbn_json_result

    try:
        response = requests.get(
            "https://openlibrary.org/api/books",
            params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
            headers=_OL_HEADERS,
            timeout=8,
            allow_redirects=True,
        )
        response.raise_for_status()
        payload = response.json() or {}
        book = payload.get(f"ISBN:{isbn}") or {}
        if book:
            authors = book.get("authors") or []
            author_names = ", ".join(
                author.get("name", "").strip()
                for author in authors
                if isinstance(author, dict) and author.get("name")
            )
            publish_date = _extract_published_date(book.get("publish_date"))
            publishers = book.get("publishers") or []
            publisher_name = ", ".join(
                publisher.get("name", "").strip()
                for publisher in publishers
                if isinstance(publisher, dict) and publisher.get("name")
            )
            description = book.get("description")
            if isinstance(description, dict):
                description = description.get("value")

            result = _build_external_lookup_payload(
                source="openlibrary",
                isbn=isbn,
                title=str(book.get("title") or "").strip(),
                author=author_names,
                genre=_map_open_library_genre(book.get("subjects")),
                published_date=publish_date,
                language="",
                publisher=publisher_name,
                description=str(description or "").strip(),
            )
            if result.get("found"):
                return result
    except Exception:
        logger.exception("Open Library books API lookup failed for ISBN %s", isbn)

    return {"found": False, "source": None, "data": {"isbn": isbn}}


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
        title = str(material.title or "").strip()
        if _is_invalid_book_title(title):
            material = None
        else:
            return {
                "found": True,
                "source": "library",
                "data": {
                    "id": str(material.id),
                    "material_type": "physical",
                    "title": material.title,
                    "author": material.author,
                    "isbn": material.isbn or "",
                    "category": material.category or "BOOK",
                    "genre": material.genre or "OTHER",
                    "published_date": material.published_date.isoformat() if material.published_date else "",
                    "language": material.language or "",
                    "department": material.department or "",
                    "barcode": material.barcode or "",
                    "description": material.description or "",
                    "price": str(material.price) if material.price is not None else "",
                    "total_copies": material.total_copies or 1,
                    "condition": material.condition or "GOOD",
                    "location": material.location or "STACK",
                    "can_borrow": bool(material.can_borrow),
                    "library": str(material.library_id) if material.library_id else "",
                },
            }

    isbn = _normalize_isbn_digits(raw)
    if not isbn:
        return {"found": False, "source": None, "data": {}}

    return _lookup_external_isbn_metadata(isbn)
