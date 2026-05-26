import io
import json
import logging
import re
import threading
from dataclasses import dataclass
from html import unescape

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


def _build_external_lookup_payload(*, source, isbn, title="", author="", genre="OTHER", published_date="", language="", publisher="", description=""):
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


def _lookup_open_library_search_metadata(isbn: str):
    try:
        response = requests.get(
            "https://openlibrary.org/search.json",
            params={"isbn": isbn, "limit": 1},
            timeout=8,
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
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f"isbn:{isbn}", "maxResults": 1},
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


def _extract_ld_json_book(html_text: str):
    matches = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in matches:
        payload = match.strip()
        if not payload:
            continue
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            continue

        stack = [parsed]
        while stack:
            current = stack.pop()
            if isinstance(current, list):
                stack.extend(current)
                continue
            if not isinstance(current, dict):
                continue

            current_type = current.get("@type")
            type_values = current_type if isinstance(current_type, list) else [current_type]
            normalized_types = {str(item or "").strip().lower() for item in type_values}
            if {"book", "product"} & normalized_types:
                return current
            stack.extend(current.values())
    return {}


def _extract_meta_content(html_text: str, attr_name: str, attr_value: str):
    pattern = (
        rf'<meta[^>]+{attr_name}=["\']{re.escape(attr_value)}["\'][^>]+content=["\']([^"\']+)["\']'
        rf'|<meta[^>]+content=["\']([^"\']+)["\'][^>]+{attr_name}=["\']{re.escape(attr_value)}["\']'
    )
    match = re.search(pattern, html_text, flags=re.IGNORECASE)
    if not match:
        return ""
    return unescape(next(group for group in match.groups() if group))


def _html_to_text(html_text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|li|h1|h2|h3|tr|td|section|article)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def _is_generic_catalog_title(value: str) -> bool:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return True
    generic_needles = (
        "find-more-books.com - buy used or antique books",
        "find-more-books.com is the price comparison site",
        "buy used or antique books at reduced prices",
        "compare book prices",
    )
    return any(needle in normalized for needle in generic_needles)


def _clean_catalog_title(value: str) -> str:
    title = re.sub(r"\s+", " ", str(value or "")).strip()
    title = re.sub(r"\s*-\s*find-more-books.*$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s*\|\s*find-more-books.*$", "", title, flags=re.IGNORECASE).strip()
    return title


def _extract_labeled_value(text: str, label: str) -> str:
    pattern = rf"{re.escape(label)}\s*:\s*(.+?)(?=\n[A-Z][A-Za-z0-9 &/+-]{{1,40}}\s*:|\n###|\nAdd to |\nClick on |\nRated |\nBook Summary:|$)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    value = re.sub(r"\s+", " ", match.group(1)).strip(" :-")
    return value


def _split_author_names(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parts = re.split(r",\s*|\s+and\s+|;\s*", raw)
    cleaned = []
    seen = set()
    for part in parts:
        item = part.strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
    return ", ".join(cleaned)


def _extract_find_more_books_page_metadata(html_text: str):
    text = _html_to_text(html_text)

    title = ""
    heading_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if heading_match:
        title = _clean_catalog_title(unescape(re.sub(r"<[^>]+>", " ", heading_match.group(1))).strip())

    if not title:
        title = _clean_catalog_title(_extract_labeled_value(text, "Title"))

    if not title:
        summary_match = re.search(
            r"The title of this book is\s+(.+?)\s+and it was written by",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if summary_match:
            title = _clean_catalog_title(summary_match.group(1))

    if not title:
        title = _clean_catalog_title(_extract_meta_content(html_text, "property", "og:title"))

    if _is_generic_catalog_title(title):
        title = ""

    author = _split_author_names(_extract_labeled_value(text, "Author"))
    if not author:
        summary_author_match = re.search(
            r"it was written by\s+(.+?)(?:\.| This particular edition| This books publish date| It was published by| The 10 digit ISBN is)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if summary_author_match:
            author = _split_author_names(summary_author_match.group(1))

    publisher = _extract_labeled_value(text, "Publisher")
    language = _normalize_language_name(_extract_labeled_value(text, "Language"))
    published_date = _extract_published_date(_extract_labeled_value(text, "Publish Date"))
    if not published_date:
        summary_date_match = re.search(
            r"This books publish date is\s+(.+?)(?:\.| and it has| It was published by| The 10 digit ISBN is)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if summary_date_match:
            published_date = _extract_published_date(summary_date_match.group(1))

    description = _extract_labeled_value(text, "Book Summary")
    if _is_generic_catalog_title(title):
        title = ""

    return {
        "title": title,
        "author": author,
        "publisher": publisher,
        "language": language,
        "published_date": published_date,
        "description": description,
    }


def _lookup_find_more_books_metadata(isbn: str):
    try:
        response = requests.get(
            f"https://www.find-more-books.com/book/isbn/{isbn}.html",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        response.raise_for_status()
        html_text = response.text or ""
        schema = _extract_ld_json_book(html_text)
        page_metadata = _extract_find_more_books_page_metadata(html_text)

        title = _clean_catalog_title(str(schema.get("name") or schema.get("headline") or "").strip())
        author = _extract_people_names(schema.get("author"))
        publisher = _extract_people_names(schema.get("publisher"))
        description = str(schema.get("description") or "").strip()
        published_date = _extract_published_date(schema.get("datePublished"))
        language = _normalize_language_name(schema.get("inLanguage"))

        if _is_generic_catalog_title(title):
            title = ""
        if not title:
            title = page_metadata.get("title", "")
        if not author:
            author = page_metadata.get("author", "")
        if not publisher:
            publisher = page_metadata.get("publisher", "")
        if not published_date:
            published_date = page_metadata.get("published_date", "")
        if not language:
            language = page_metadata.get("language", "")
        if not description or description.lower().startswith("find-more-books.com is"):
            description = page_metadata.get("description", "")
        if not description:
            description = _extract_meta_content(html_text, "name", "description")
        if not title:
            title_match = re.search(r"<title>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
            if title_match:
                title = _clean_catalog_title(unescape(re.sub(r"\s+", " ", title_match.group(1))).strip())
        if _is_generic_catalog_title(title):
            title = ""

        if title and not author and description:
            author_match = re.search(r"\bby\s+([^,|]+)", description, flags=re.IGNORECASE)
            if author_match:
                author = author_match.group(1).strip()

        title = _clean_catalog_title(title)
        if not title or _is_generic_catalog_title(title):
            return {"found": False, "source": "find_more_books", "data": {"isbn": isbn}}

        return _build_external_lookup_payload(
            source="find_more_books",
            isbn=isbn,
            title=title,
            author=author,
            published_date=published_date,
            language=language,
            publisher=publisher,
            description=description,
        )
    except Exception:
        logger.exception("find-more-books lookup failed for ISBN %s", isbn)
        return {"found": False, "source": "find_more_books", "data": {"isbn": isbn}}


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
            search_result = _lookup_open_library_search_metadata(isbn)
            if search_result.get("found"):
                return search_result
            google_result = _lookup_google_books_metadata(isbn)
            if google_result.get("found"):
                return google_result
            return _lookup_find_more_books_metadata(isbn)

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
                "publisher": publisher_name,
                "description": str(description or "").strip(),
                "total_copies": 1,
                "condition": "NEW",
                "location": "STACK",
                "can_borrow": True,
            },
        }
    except Exception:
        logger.exception("Open Library lookup failed for ISBN %s", isbn)
        search_result = _lookup_open_library_search_metadata(isbn)
        if search_result.get("found"):
            return search_result
        google_result = _lookup_google_books_metadata(isbn)
        if google_result.get("found"):
            return google_result
        return _lookup_find_more_books_metadata(isbn)
