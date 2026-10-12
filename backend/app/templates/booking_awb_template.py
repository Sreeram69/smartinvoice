import io
import re
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from app.templates.invoice_template import amount_to_words


def generate_booking_awb_pdf(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a professional single-page Air Waybill (AWB) Booking Note & Pricing Receipt.
    Features:
      - Clean single A4 layout
      - Shipper & Consignee routing
      - Shipment specs (Pieces, Dimensions, Gross Wt, Volumetric Wt, Chargeable Wt)
      - Customer pricing breakdown (Rate/KG, Freight, Handling, Total ₹)
      - Payment status & mode
      - Legal cargo declaration & dual signature blocks
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=26,
        rightMargin=26,
        topMargin=26,
        bottomMargin=26,
    )

    styles = getSampleStyleSheet()

    f_title = ParagraphStyle('B_Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=1)
    f_sub = ParagraphStyle('B_Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1)
    f_hdr = ParagraphStyle('B_Hdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
    f_hdr_c = ParagraphStyle('B_HdrC', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1)
    f_hdr_r = ParagraphStyle('B_HdrR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=2)
    f_body = ParagraphStyle('B_Body', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5)
    f_body_b = ParagraphStyle('B_BodyB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5)
    f_body_c = ParagraphStyle('B_BodyC', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=1)
    f_body_r = ParagraphStyle('B_BodyR', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2)
    
    f_decl_title = ParagraphStyle('B_DeclTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, spaceAfter=2)
    f_decl = ParagraphStyle('B_Decl', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, leading=8.2, spaceAfter=1)
    f_sig_lbl = ParagraphStyle('B_SigLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=1)

    # Document details
    awb_number = str(data.get('doc_number') or 'AWB-2026-0001').strip().upper()
    date_str = str(data.get('date') or datetime.now().strftime('%Y-%m-%d')).strip()
    sender = data.get('sender') or {}
    customer = data.get('customer') or {}

    # Shipment details
    dest_country = str(data.get('destination_country') or customer.get('country') or customer.get('state') or 'INTL').strip().upper()
    dest_city = str(customer.get('city') or '').strip().upper()
    service_partner = str(data.get('service_partner') or 'EXPRESS AIR CARGO').strip().upper()
    package_type = str(data.get('package_type') or 'PARCEL / NON-DOC').strip().upper()
    pieces = str(data.get('pieces') or '1 PCS').strip().upper()
    contents = str(data.get('contents_description') or 'PERSONAL GOODS & EFFECTS').strip().upper()

    actual_wt_str = str(data.get('actual_weight') or data.get('weight') or '1.0').strip()
    vol_wt_str = str(data.get('volumetric_weight') or '').strip()
    chargeable_wt_str = str(data.get('chargeable_weight') or actual_wt_str).strip()

    # Pricing & Charges
    try:
        chg_wt = float(re.sub(r'[^0-9.]', '', chargeable_wt_str) or 1.0)
    except Exception:
        chg_wt = 1.0

    rate_str = str(data.get('rate_per_kg') or '0.00').strip()
    try:
        rate_n = float(re.sub(r'[^0-9.]', '', rate_str) or 0.0)
    except Exception:
        rate_n = 0.0

    try:
        freight_n = float(re.sub(r'[^0-9.]', '', str(data.get('freight_amount') or '0')) or (chg_wt * rate_n))
    except Exception:
        freight_n = chg_wt * rate_n

    try:
        other_n = float(re.sub(r'[^0-9.]', '', str(data.get('other_charges') or '0')) or 0.0)
    except Exception:
        other_n = 0.0

    try:
        disc_n = float(re.sub(r'[^0-9.]', '', str(data.get('discount') or '0')) or 0.0)
    except Exception:
        disc_n = 0.0

    # Total given to customer
    custom_total = str(data.get('total') or '').strip()
    if custom_total and custom_total != '0.00':
        try:
            total_n = float(re.sub(r'[^0-9.]', '', custom_total))
        except Exception:
            total_n = freight_n + other_n - disc_n
    else:
        total_n = max(0.0, freight_n + other_n - disc_n)

    payment_status = str(data.get('payment_status') or 'PAID').strip().upper()
    payment_mode = str(data.get('payment_mode') or 'UPI / CASH').strip().upper()
    words_text = amount_to_words(total_n)

    # 1. SENDER HTML
    sender_lines = []
    if sender.get('name'):
        sender_lines.append(f"<b>{str(sender['name']).strip().upper()}</b>")
    if sender.get('address_line_1'):
        sender_lines.append(str(sender['address_line_1']).strip().upper())
    if sender.get('address_line_2'):
        sender_lines.append(str(sender['address_line_2']).strip().upper())
    city_s = f"{sender.get('city', '')} {sender.get('state', '')} {sender.get('postal_code', '')}".strip().upper()
    if city_s:
        sender_lines.append(city_s)
    if sender.get('phone'):
        sender_lines.append(f"<b>PHONE: {str(sender['phone']).strip()}</b>")
    sender_html = "<br/>".join(sender_lines) if sender_lines else "N/A"

    # 2. CONSIGNEE HTML
    cust_lines = []
    if customer.get('name'):
        cust_lines.append(f"<b>{str(customer['name']).strip().upper()}</b>")
    if customer.get('address_line_1'):
        cust_lines.append(str(customer['address_line_1']).strip().upper())
    if customer.get('address_line_2'):
        cust_lines.append(str(customer['address_line_2']).strip().upper())
    city_c = f"{customer.get('city', '')} {customer.get('state', '')} {customer.get('postal_code', '')}".strip().upper()
    if city_c:
        cust_lines.append(city_c)
    if customer.get('country') and str(customer['country']).upper() not in city_c:
        cust_lines.append(f"<b>COUNTRY: {str(customer['country']).strip().upper()}</b>")
    if customer.get('phone'):
        cust_lines.append(f"<b>PHONE: {str(customer['phone']).strip()}</b>")
    consignee_html = "<br/>".join(cust_lines) if cust_lines else "N/A"

    # Table 0: Super Header
    company_name = str(sender.get('name') or 'SMARTINVOICE COURIER & LOGISTICS').strip().upper()
    top_header_data = [
        [
            Paragraph(f"<b>{company_name}</b>", f_title),
            Paragraph(f"<b>AWB NO: &nbsp; {awb_number}</b>", f_hdr),
        ],
        [
            Paragraph("<b>AIR WAYBILL & CUSTOMER BOOKING RECEIPT</b>", f_sub),
            Paragraph(f"<b>BOOKING DATE:</b> &nbsp; {date_str}<br/><b>NETWORK / SERVICE:</b> &nbsp; {service_partner}", f_body),
        ]
    ]
    top_table = Table(top_header_data, colWidths=[338, 205])
    top_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    # Table 1: Shipper & Consignee
    parties_data = [
        [
            Paragraph("<b>SHIPPER / CONSIGNOR (FROM)</b>", f_hdr),
            Paragraph("<b>CONSIGNEE / DESTINATION (TO)</b>", f_hdr),
        ],
        [
            Paragraph(sender_html, f_body),
            Paragraph(consignee_html, f_body),
        ]
    ]
    parties_table = Table(parties_data, colWidths=[271, 272])
    parties_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    # Table 2: Shipment Specifications
    full_dest = f"{dest_city}, {dest_country}" if dest_city and dest_city != dest_country else dest_country
    ship_data = [
        [
            Paragraph("<b>FINAL DESTINATION</b>", f_hdr_c),
            Paragraph("<b>PIECES</b>", f_hdr_c),
            Paragraph("<b>PACKAGE TYPE</b>", f_hdr_c),
            Paragraph("<b>ACTUAL WT</b>", f_hdr_c),
            Paragraph("<b>CHARGEABLE WT</b>", f_hdr_c),
        ],
        [
            Paragraph(f"<b>{full_dest}</b>", f_body_c),
            Paragraph(pieces, f_body_c),
            Paragraph(package_type, f_body_c),
            Paragraph(f"{actual_wt_str} KG" if not actual_wt_str.endswith('KG') else actual_wt_str, f_body_c),
            Paragraph(f"<b>{chg_wt:.2f} KG</b>", f_body_c),
        ],
        [
            Paragraph(f"<b>CONTENTS DESCRIPTION:</b> &nbsp; {contents}", f_body),
            "",
            "",
            "",
            "",
        ]
    ]
    ship_table = Table(ship_data, colWidths=[153, 75, 115, 100, 100])
    ship_table.setStyle(TableStyle([
        ('SPAN', (0, 2), (4, 2)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    # Table 3: Customer Pricing Breakdown
    pricing_data = [
        [
            Paragraph("<b>PRICING & CHARGES GIVEN TO CUSTOMER</b>", f_hdr),
            "",
            "",
            Paragraph("<b>AMOUNT (INR)</b>", f_hdr_r),
        ],
        [
            Paragraph(f"<b>Base Freight Charges</b> ({chg_wt:.2f} KG @ INR {rate_n:.2f}/KG)", f_body),
            "",
            "",
            Paragraph(f"INR {freight_n:.2f}", f_body_r),
        ],
        [
            Paragraph("<b>Handling / Packaging / Pickup Charges</b>", f_body),
            "",
            "",
            Paragraph(f"INR {other_n:.2f}", f_body_r),
        ],
        [
            Paragraph("<b>Promotional Discount</b>", f_body),
            "",
            "",
            Paragraph(f"- INR {disc_n:.2f}" if disc_n > 0 else "INR 0.00", f_body_r),
        ],
        [
            Paragraph("<b>NET TOTAL CHARGES GIVEN TO CUSTOMER</b>", f_hdr),
            "",
            "",
            Paragraph(f"<b>INR {total_n:.2f}</b>", f_title),
        ],
        [
            Paragraph(f"<b>AMOUNT IN WORDS:</b> &nbsp; {words_text}", f_body_b),
            "",
            Paragraph(f"<b>STATUS:</b> &nbsp; {payment_status}", f_body_c),
            Paragraph(f"<b>MODE:</b> &nbsp; {payment_mode}", f_body_r),
        ]
    ]
    pricing_table = Table(pricing_data, colWidths=[271, 72, 100, 100])
    pricing_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (2, 0)),
        ('SPAN', (0, 1), (2, 1)),
        ('SPAN', (0, 2), (2, 2)),
        ('SPAN', (0, 3), (2, 3)),
        ('SPAN', (0, 4), (2, 4)),
        ('SPAN', (0, 5), (1, 5)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    # Table 4: Declaration & Signatures
    decl_text = [
        Paragraph("<b>SHIPPER'S DECLARATION & TERMS:</b>", f_decl_title),
        Paragraph("1. I/We hereby declare that this consignment does not contain any cash, hazardous material, inflammable substances, contraband, or goods prohibited by customs regulations.", f_decl),
        Paragraph("2. The nature, value, and particulars of the goods specified above are true, complete, and correct to the best of my knowledge.", f_decl),
        Paragraph("3. All freight and booking charges quoted above have been verified and accepted for delivery to final destination.", f_decl),
    ]

    sig_shipper = [
        Paragraph("<br/><br/><br/>", f_body),
        Paragraph("___________________________________", f_sig_lbl),
        Paragraph("Shipper / Customer Signature", f_sig_lbl),
    ]

    sig_agent = [
        Paragraph("<br/><br/><br/>", f_body),
        Paragraph("___________________________________", f_sig_lbl),
        Paragraph("Authorized Booking Agent", f_sig_lbl),
    ]

    footer_data = [
        [
            decl_text,
            "",
        ],
        [
            sig_shipper,
            sig_agent,
        ]
    ]
    footer_table = Table(footer_data, colWidths=[271, 272])
    footer_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBEFORE', (1, 1), (1, 1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, 0), 'TOP'),
        ('VALIGN', (0, 1), (-1, 1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    doc.build([
        top_table,
        parties_table,
        ship_table,
        pricing_table,
        footer_table,
    ])

    buffer.seek(0)
    return buffer
