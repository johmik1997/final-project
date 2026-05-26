"""Very overdue warning letter preparation and PDF export."""

import logging
from dataclasses import dataclass
from datetime import date
from typing import List

logger = logging.getLogger(__name__)

from django.conf import settings
from django.utils import timezone

from user_mgt.access import get_active_library_policy

from .models import Borrow
from .services import calculate_overdue_days, sync_overdue_borrow_statuses

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 56
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN * 2)


@dataclass
class VeryOverdueLetter:
    borrow_id: str
    member_id: str
    member_id_number: str
    member_name: str
    member_email: str
    material_title: str
    material_author: str
    borrow_date: str
    due_date: str
    overdue_days: int
    letter_date: str
    library_name: str
    subject: str
    body_lines: List[str]


def get_very_overdue_threshold_days():
    return int(getattr(settings, "VERY_OVERDUE_DAYS", 14) or 14)


def get_very_overdue_borrows_queryset(base_queryset=None, *, now=None, threshold_days=None):
    now = now or timezone.now()
    threshold_days = threshold_days if threshold_days is not None else get_very_overdue_threshold_days()
    sync_overdue_borrow_statuses(base_queryset=base_queryset, now=now)

    queryset = base_queryset if base_queryset is not None else Borrow.objects.all()
    queryset = queryset.select_related("member", "material", "material__library").filter(
        status__in=["BORROWED", "OVERDUE"],
        due_date__lt=now,
    )

    results = []
    for borrow in queryset:
        policy = get_active_library_policy(getattr(borrow.material, "library", None))
        grace = int(getattr(policy, "grace_period_days", 0) or 0)
        overdue_days = calculate_overdue_days(borrow.due_date, now=now, grace_period_days=grace)
        if overdue_days >= threshold_days:
            results.append((borrow, overdue_days))
    return results


def build_warning_letter(borrow: Borrow, overdue_days: int, *, letter_date=None) -> VeryOverdueLetter:
    member = borrow.member
    material = borrow.material
    library = getattr(material, "library", None)
    letter_date = letter_date or timezone.localdate()
    member_name = f"{member.first_name} {member.last_name}".strip() or member.id_number

    body_lines = [
        f"Dear {member_name},",
        "",
        "This letter is a formal warning that the following library material is very overdue and must be returned immediately.",
        "",
        f"Book title: {getattr(material, 'title', 'Unknown')}",
        f"Author: {getattr(material, 'author', '—') or '—'}",
        f"Borrowed on: {borrow.borrow_date.strftime('%d %B %Y')}",
        f"Original due date: {borrow.due_date.strftime('%d %B %Y')}",
        f"Days overdue: {overdue_days}",
        "",
        "Please return this item to the library without delay. Further delay may result in fines, "
        "suspension of borrowing privileges, or other penalties under library policy.",
        "",
        "If you have already returned this material, present your return receipt at the library desk.",
        "",
        "Sincerely,",
        getattr(library, "name", "University Library"),
    ]

    return VeryOverdueLetter(
        borrow_id=str(borrow.pk),
        member_id=str(member.pk),
        member_id_number=member.id_number,
        member_name=member_name,
        member_email=(member.email or "").strip(),
        material_title=getattr(material, "title", "Unknown"),
        material_author=getattr(material, "author", "") or "—",
        borrow_date=borrow.borrow_date.strftime("%Y-%m-%d"),
        due_date=borrow.due_date.strftime("%Y-%m-%d"),
        overdue_days=overdue_days,
        letter_date=letter_date.isoformat() if isinstance(letter_date, date) else str(letter_date),
        library_name=getattr(library, "name", "University Library"),
        subject="Very Overdue Material — Official Warning Letter",
        body_lines=body_lines,
    )


def serialize_very_overdue_letters(borrows_with_days):
    return [build_warning_letter(borrow, overdue_days) for borrow, overdue_days in borrows_with_days]


def letter_to_dict(letter: VeryOverdueLetter):
    return {
        "borrow_id": letter.borrow_id,
        "member_id": letter.member_id,
        "member_id_number": letter.member_id_number,
        "member_name": letter.member_name,
        "member_email": letter.member_email,
        "material_title": letter.material_title,
        "material_author": letter.material_author,
        "borrow_date": letter.borrow_date,
        "due_date": letter.due_date,
        "overdue_days": letter.overdue_days,
        "letter_date": letter.letter_date,
        "library_name": letter.library_name,
        "subject": letter.subject,
        "body_lines": letter.body_lines,
    }


def _insert_textbox(page, top, text, *, fontsize=11, fontname="helv", min_height=24, bold=False):
    """Insert wrapped text; return new Y position below the box."""
    if bold:
        fontname = "hebo"
    rect = fitz.Rect(MARGIN, top, PAGE_WIDTH - MARGIN, top + min_height)
    overflow = page.insert_textbox(
        rect,
        str(text or ""),
        fontsize=fontsize,
        fontname=fontname,
        align=fitz.TEXT_ALIGN_LEFT,
    )
    if overflow < 0:
        rect = fitz.Rect(MARGIN, top, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN)
        page.insert_textbox(
            rect,
            str(text or ""),
            fontsize=fontsize,
            fontname=fontname,
            align=fitz.TEXT_ALIGN_LEFT,
        )
        return PAGE_HEIGHT - MARGIN - 20

    lines = str(text or "").count("\n") + max(1, len(str(text or "")) // 72)
    height = max(min_height, lines * (fontsize + 5))
    return top + height + 10


def _generate_warning_letter_pdf_reportlab(letter: VeryOverdueLetter) -> bytes:
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=letter.subject,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "LetterTitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#92400e"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "LetterBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "LetterMeta",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        spaceAfter=4,
    )

    story = [
        Paragraph(letter.library_name, title_style),
        Paragraph(f"Date: {letter.letter_date}", meta_style),
        Spacer(1, 6),
        Paragraph(letter.subject, styles["Heading3"]),
        Spacer(1, 8),
        Paragraph(f"<b>To:</b> {letter.member_name}", meta_style),
        Paragraph(f"<b>Student ID:</b> {letter.member_id_number}", meta_style),
    ]
    if letter.member_email:
        story.append(Paragraph(f"<b>Email:</b> {letter.member_email}", meta_style))
    story.append(Spacer(1, 10))

    details = [
        ["Material", letter.material_title],
        ["Author", letter.material_author],
        ["Borrowed", letter.borrow_date],
        ["Due date", letter.due_date],
        ["Days overdue", str(letter.overdue_days)],
    ]
    table = Table(details, colWidths=[32 * mm, 130 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([table, Spacer(1, 12)])

    for line in letter.body_lines:
        if line:
            story.append(Paragraph(line, body_style))
        else:
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            "<i>This is an official library notice. Please retain a copy for your records.</i>",
            meta_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()


def _generate_warning_letter_pdf_fitz(letter: VeryOverdueLetter) -> bytes:
    doc = fitz.open()
    page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)

    header_rect = fitz.Rect(MARGIN, MARGIN, PAGE_WIDTH - MARGIN, MARGIN + 44)
    page.draw_rect(header_rect, color=(0.75, 0.35, 0.05), fill=(1, 0.97, 0.92), width=0.6)
    page.insert_textbox(
        fitz.Rect(MARGIN + 14, MARGIN + 10, PAGE_WIDTH - MARGIN - 14, MARGIN + 38),
        letter.library_name,
        fontsize=15,
        fontname="hebo",
        align=fitz.TEXT_ALIGN_LEFT,
    )

    y = MARGIN + 58
    y = _insert_textbox(page, y, f"Date: {letter.letter_date}", fontsize=10, min_height=18)
    y = _insert_textbox(page, y, letter.subject, fontsize=13, min_height=28, bold=True)

    y += 4
    meta_lines = [
        f"To: {letter.member_name}",
        f"Student ID: {letter.member_id_number}",
    ]
    if letter.member_email:
        meta_lines.append(f"Email: {letter.member_email}")
    y = _insert_textbox(page, y, "\n".join(meta_lines), fontsize=11, min_height=52)

    details_rect = fitz.Rect(MARGIN, y, PAGE_WIDTH - MARGIN, y + 92)
    page.draw_rect(details_rect, color=(0.82, 0.82, 0.82), fill=(0.98, 0.98, 0.99), width=0.5)
    details_text = (
        f"Material: {letter.material_title}\n"
        f"Author: {letter.material_author}\n"
        f"Borrowed: {letter.borrow_date}   |   Due: {letter.due_date}   |   "
        f"Days overdue: {letter.overdue_days}"
    )
    page.insert_textbox(
        fitz.Rect(MARGIN + 12, y + 10, PAGE_WIDTH - MARGIN - 12, y + 82),
        details_text,
        fontsize=10,
        fontname="helv",
        align=fitz.TEXT_ALIGN_LEFT,
    )
    y += 102

    body_text = "\n".join(letter.body_lines)
    _insert_textbox(page, y, body_text, fontsize=11, min_height=280)

    footer_y = PAGE_HEIGHT - MARGIN - 24
    page.insert_textbox(
        fitz.Rect(MARGIN, footer_y, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN),
        "This is an official library notice. Please retain a copy for your records.",
        fontsize=9,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def generate_warning_letter_pdf(letter: VeryOverdueLetter) -> bytes:
    if fitz is not None:
        try:
            return _generate_warning_letter_pdf_fitz(letter)
        except Exception:
            logger.exception("PyMuPDF warning letter failed; falling back to ReportLab")

    try:
        return _generate_warning_letter_pdf_reportlab(letter)
    except Exception as exc:
        logger.exception("ReportLab warning letter failed")
        raise RuntimeError("PDF generation is unavailable. Install reportlab or PyMuPDF.") from exc
