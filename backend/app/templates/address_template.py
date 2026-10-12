import io
import os
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Pt, Inches


def get_template_docx_path() -> Optional[str]:
    """Finds the template DUBAI.docx asset or desktop fallback."""
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(curr_dir, "assets", "DUBAI.docx")
    if os.path.exists(asset_path):
        return asset_path
    desktop_fallback = r"C:\Users\cheek\OneDrive\Desktop\New folder\DUBAI.docx"
    if os.path.exists(desktop_fallback):
        return desktop_fallback
    return None


def build_address_lines(info: Dict[str, Any]) -> List[str]:
    """Extracts clean uppercase address lines from an address dict."""
    lines = []
    if info.get('name'):
        lines.append(str(info['name']).strip().upper())
    if info.get('address_line_1'):
        lines.append(str(info['address_line_1']).strip().upper())
    if info.get('address_line_2'):
        lines.append(str(info['address_line_2']).strip().upper())

    city_parts = [
        str(p).strip().upper()
        for p in [info.get('city'), info.get('state'), info.get('country')]
        if p and str(p).strip()
    ]
    if city_parts:
        city_str = ', '.join(city_parts)
        if not any(city_str == l for l in lines):
            lines.append(city_str)

    if info.get('postal_code'):
        pin = str(info['postal_code']).strip().upper()
        if not any(pin in l for l in lines):
            lines.append(pin)

    if info.get('phone'):
        clean_phone = str(info['phone']).strip()
        lines.append(clean_phone)

    return lines


def generate_address_docx(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates an editable Word (.docx) format Address Label
    filling the original 'DUBAI.docx' template directly with no newly added borders or backgrounds.
    """
    template_path = get_template_docx_path()
    if template_path and os.path.exists(template_path):
        doc = Document(template_path)
        # Clear body paragraphs to populate dynamically with identical styles
        for p in list(doc.paragraphs):
            p._element.getparent().remove(p._element)
    else:
        doc = Document()
        for s in doc.sections:
            s.top_margin = Inches(1.0)
            s.bottom_margin = Inches(1.0)
            s.left_margin = Inches(1.0)
            s.right_margin = Inches(1.0)
            s.page_width = Inches(8.5)
            s.page_height = Inches(11.0)

    customer = data.get('customer', {})
    sender = data.get('sender', {})

    # 1. TO, section in 20pt BOLD UPPERCASE
    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_before = Pt(0)
    p_to.paragraph_format.space_after = Pt(2)
    r_to = p_to.add_run("TO,")
    r_to.bold = True
    r_to.font.size = Pt(20)

    cust_lines = build_address_lines(customer)
    for line in cust_lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.bold = True
        r.font.size = Pt(20)

    # 2. Blank separation spacing (matches DUBAI.docx 5 blank lines)
    for _ in range(5):
        doc.add_paragraph()

    # 3. FROM section in 20pt BOLD UPPERCASE
    p_from = doc.add_paragraph()
    p_from.paragraph_format.space_before = Pt(0)
    p_from.paragraph_format.space_after = Pt(2)
    r_from = p_from.add_run("FROM")
    r_from.bold = True
    r_from.font.size = Pt(20)

    sender_lines = build_address_lines(sender)
    for line in sender_lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.bold = True
        r.font.size = Pt(20)

    doc.add_paragraph()

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def generate_address_pdf(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a printable Letter/A4 Address Label in PDF format
    matching the exact visual layout (20pt Bold, clean, simple TO/FROM, NO borders, NO backgrounds) of 'DUBAI.docx'.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=72,  # 1.0 inch margins
        rightMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()

    bold_20 = ParagraphStyle(
        'Bold20',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=23,
        textColor=colors.black,
        spaceAfter=2,
    )

    customer = data.get('customer', {})
    sender = data.get('sender', {})

    story = []

    # TO, header & address lines
    story.append(Paragraph("<b>TO,</b>", bold_20))
    for line in build_address_lines(customer):
        story.append(Paragraph(f"<b>{line}</b>", bold_20))

    # Separation Spacing matching 5 blank lines
    story.append(Spacer(1, 65))

    # FROM header & address lines
    story.append(Paragraph("<b>FROM</b>", bold_20))
    for line in build_address_lines(sender):
        story.append(Paragraph(f"<b>{line}</b>", bold_20))

    doc.build(story)
    buffer.seek(0)
    return buffer

