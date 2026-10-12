import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def amount_to_words(n) -> str:
    """
    Converts a numeric amount into standard Indian currency words
    e.g. 4370 -> 'FOUR THOUSAND THREE HUNDRED SEVENTY ONLY'
    """
    try:
        n = int(round(float(str(n).replace(',', '').strip())))
    except (ValueError, TypeError):
        return 'ZERO ONLY'
    if n == 0:
        return 'ZERO ONLY'

    units = [
        '', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE',
        'TEN', 'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN',
        'SEVENTEEN', 'EIGHTEEN', 'NINETEEN'
    ]
    tens = ['', '', 'TWENTY', 'THIRTY', 'FORTY', 'FIFTY', 'SIXTY', 'SEVENTY', 'EIGHTY', 'NINETY']

    def two_digits(num: int) -> str:
        if num < 20:
            return units[num]
        return tens[num // 10] + ('' if num % 10 == 0 else ' ' + units[num % 10])

    def three_digits(num: int) -> str:
        h = num // 100
        rem = num % 100
        if h > 0:
            return units[h] + ' HUNDRED' + ('' if rem == 0 else ' ' + two_digits(rem))
        return two_digits(rem)

    parts = []
    # Crores (10,000,000)
    crores = n // 10000000
    n %= 10000000
    if crores > 0:
        parts.append(two_digits(crores) + ' CRORE')
    # Lakhs (100,000)
    lakhs = n // 100000
    n %= 100000
    if lakhs > 0:
        parts.append(two_digits(lakhs) + ' LAKH')
    # Thousands (1,000)
    thousands = n // 1000
    n %= 1000
    if thousands > 0:
        parts.append(two_digits(thousands) + ' THOUSAND')
    if n > 0:
        parts.append(three_digits(n))

    return ' '.join(parts) + ' ONLY'


def generate_invoice_pdf(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a single-page commercial shipping invoice PDF
    matching the exact structure, font hierarchy, and grid of 'INVOICE format.xlsx'.
    """
    buffer = io.BytesIO()
    # A4 dimensions: 595.27 x 841.89 pt. 26pt side margins => 543.27 pt width.
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=26,
        leftMargin=26,
        topMargin=26,
        bottomMargin=26,
    )

    styles = getSampleStyleSheet()

    # Typography matching Calibri / Arial in 'INVOICE format.xlsx'
    f_hdr = ParagraphStyle('F_Hdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=12)
    f_hdr_c = ParagraphStyle('F_HdrC', parent=f_hdr, alignment=1) # Center
    f_hdr_r = ParagraphStyle('F_HdrR', parent=f_hdr, alignment=2) # Right
    f_body = ParagraphStyle('F_Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5)
    f_body_b = ParagraphStyle('F_BodyB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5)
    f_body_c = ParagraphStyle('F_BodyC', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, alignment=1)
    f_decl = ParagraphStyle('F_Decl', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11)

    sender = data.get('sender', {})
    customer = data.get('customer', {})
    doc_number = str(data.get('doc_number', '123'))
    date_str = str(data.get('date', '22-10-2026'))
    items = data.get('items', [])
    total_val = str(data.get('total', '0'))

    # Calculate numeric total
    items_sum = 0.0
    for it in items:
        try:
            cnt = float(str(it.get('count', 1)).replace(',', ''))
            prc = float(str(it.get('price', 0)).replace(',', ''))
            items_sum += cnt * prc
        except Exception:
            pass

    if items_sum > 0:
        num_total = items_sum
    else:
        try:
            num_total = float(total_val.replace(',', '').strip())
        except Exception:
            num_total = 0.0

    words_text = amount_to_words(num_total)

    destination = str(customer.get('country') or customer.get('state') or customer.get('city') or '').strip().upper()
    origin_country = str(sender.get('country') or sender.get('state') or 'INDIA').strip().upper()
    loading_port = str(sender.get('city') or '').strip().upper()
    weight_str = str(data.get('weight') or '').strip()
    awb_number = str(data.get('awb_number') or data.get('awb') or '').strip().upper()
    awb_display = f"<b>AWB : {awb_number}</b>" if awb_number else "<b>AWB :</b>"
    contents_desc = str(data.get('contents_description') or data.get('contents') or '').strip().upper()
    other_block_text = f"<b>{contents_desc}</b>" if contents_desc else "<b>OTHERS</b>"

    # 1. SENDER block
    sender_lines = []
    if sender.get('name'):
        sender_lines.append(f"<b>{str(sender['name']).strip().upper()}</b>")
    if sender.get('address_line_1'):
        sender_lines.append(str(sender['address_line_1']).strip().upper())
    if sender.get('address_line_2'):
        sender_lines.append(str(sender['address_line_2']).strip().upper())
    if sender.get('city'):
        sender_lines.append(str(sender['city']).strip().upper())
    if sender.get('phone'):
        sender_lines.append(f"<b>PHONE NO. {str(sender['phone']).strip()}</b>")
    sender_html = "<br/>".join(sender_lines)

    # 2. CONSIGNEE block
    consignee_lines = []
    if customer.get('name'):
        consignee_lines.append(f"<b>{str(customer['name']).strip().upper()}</b>")
    if customer.get('address_line_1'):
        consignee_lines.append(str(customer['address_line_1']).strip().upper())
    if customer.get('address_line_2'):
        consignee_lines.append(str(customer['address_line_2']).strip().upper())
    city_str = f"{customer.get('city', '')} {customer.get('state', '')} {customer.get('postal_code', '')}".strip().upper()
    if city_str:
        consignee_lines.append(city_str)
    if customer.get('phone'):
        consignee_lines.append(f"<b>PHONE NO. {str(customer['phone']).strip()}</b>")
    consignee_html = "<br/>".join(consignee_lines)

    # Table 1: Parties & Header Meta (Total Width: 543 pt => Cols A-E: 308 pt, Cols F-G: 131 pt, Cols H-I: 104 pt)
    header_data = [
        [
            Paragraph("<b>SENDER</b>", f_hdr),
            Paragraph(f"<b>Date: {date_str}</b>", f_body_b),
            Paragraph(f"<b>INVOICE NO : {doc_number}</b>", f_body_b),
        ],
        [
            Paragraph(sender_html, f_body),
            Paragraph("<b>SEND FOR PERSONAL USE ONLY</b>", f_hdr_c),
            "",
        ],
        [
            Paragraph("<b>CONSIGNEE</b>", f_hdr),
            Paragraph(awb_display, f_hdr),
            "",
        ],
        [
            Paragraph(consignee_html, f_body),
            Paragraph(other_block_text, f_hdr_c),
            "",
        ],
    ]

    header_table = Table(header_data, colWidths=[308, 131, 104])
    header_table.setStyle(TableStyle([
        ('SPAN', (1, 0), (1, 0)),
        ('SPAN', (2, 0), (2, 0)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (1, 3), (2, 3)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('VALIGN', (1, 1), (2, 1), 'MIDDLE'),
        ('VALIGN', (1, 3), (2, 3), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    pcs_weight = f"1PCS / {weight_str}" if weight_str else "1PCS"

    # Table 2: Perfectly Realigned Route & Destination (Total Width: 543 pt => Left: 308 pt, Right: 235 pt)
    # Empty block and Port of Discharge removed; Port of Loading & Final Destination realigned
    route_data = [
        [
            Paragraph(f"<b>Port of loading:</b> &nbsp; {loading_port}", f_body),
            Paragraph(f"<b>Country of origin of goods:</b> &nbsp; {origin_country}", f_body),
        ],
        [
            Paragraph(f"<b>Final Destination:</b> &nbsp; {destination}", f_body),
            Paragraph(f"<b>{pcs_weight}</b>", f_hdr_c),
        ]
    ]
    route_table = Table(route_data, colWidths=[308, 235])
    route_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    # Table 3: Items Table (Total Width: 543 pt => S.NO: 45, ITEM DETAILS: 275, COUNT: 65, RATE: 75, AMOUNT: 83)
    items_data = [
        [
            Paragraph("<b>S.NO</b>", f_hdr_c),
            Paragraph("<b>ITEM DETAILS</b>", f_hdr_c),
            Paragraph("<b>COUNT</b>", f_hdr_c),
            Paragraph("<b>RATE</b>", f_hdr_c),
            Paragraph("<b>AMOUNT</b>", f_hdr_c),
        ]
    ]

    total_item_rows = max(15, len(items))
    for idx in range(total_item_rows):
        if idx < len(items):
            it = items[idx]
            name = str(it.get('name', f'Item {idx + 1}')).upper()
            qty = it.get('count', 1)
            price = it.get('price', 0)
            try:
                qty_n = float(str(qty).replace(',', ''))
                price_n = float(str(price).replace(',', ''))
                line_amt = qty_n * price_n
            except Exception:
                qty_n = 1.0
                price_n = 0.0
                line_amt = 0.0

            items_data.append([
                Paragraph(str(idx + 1), f_body_c),
                Paragraph(name, f_body_b),
                Paragraph(f"{qty_n:.0f}" if qty_n.is_integer() else f"{qty_n:.2f}", f_body_c),
                Paragraph(f"{price_n:.2f}", f_body_c),
                Paragraph(f"{line_amt:.2f}", f_body_c),
            ])
        else:
            items_data.append([
                Paragraph("", f_body),
                Paragraph("", f_body),
                Paragraph("", f_body),
                Paragraph("", f_body),
                Paragraph("", f_body),
            ])

    final_total_display = f"{num_total:.2f}"

    # Total Row (Row index total_item_rows + 1)
    items_data.append([
        Paragraph("<b>TOTAL AMOUNT</b>", f_hdr_r),
        "",
        "",
        "",
        Paragraph(f"<b>{final_total_display}</b>", f_hdr_c),
    ])

    items_col_widths = [45, 275, 65, 75, 83]
    items_row_heights = [18] + [14.0] * total_item_rows + [18]
    items_table = Table(items_data, colWidths=items_col_widths, rowHeights=items_row_heights)
    
    total_row_idx = total_item_rows + 1
    items_table.setStyle(TableStyle([
        # Header Row
        ('BOX', (0, 0), (-1, 0), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, 0), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

        # Items Area: continuous vertical columns through all prepared rows without inner horizontal lines
        ('BOX', (0, 1), (-1, total_item_rows), 0.5, colors.black),
        ('LINEBEFORE', (1, 1), (1, total_item_rows), 0.5, colors.black), # Between S.NO and ITEM DETAILS
        ('LINEBEFORE', (2, 1), (2, total_item_rows), 0.5, colors.black), # Between ITEM DETAILS and Quantity
        ('LINEBEFORE', (3, 1), (3, total_item_rows), 0.5, colors.black), # Between Quantity and RATE INR
        ('LINEBEFORE', (4, 1), (4, total_item_rows), 0.5, colors.black), # Between RATE INR and AMOUNT INR
        ('VALIGN', (0, 1), (-1, total_item_rows), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, total_item_rows), 1),
        ('BOTTOMPADDING', (0, 1), (-1, total_item_rows), 1),
        ('LEFTPADDING', (0, 1), (-1, total_item_rows), 4),
        ('RIGHTPADDING', (0, 1), (-1, total_item_rows), 4),

        # Total Row
        ('SPAN', (0, total_row_idx), (3, total_row_idx)),
        ('BOX', (0, total_row_idx), (-1, total_row_idx), 0.5, colors.black),
        ('INNERGRID', (0, total_row_idx), (-1, total_row_idx), 0.5, colors.black),
        ('VALIGN', (0, total_row_idx), (-1, total_row_idx), 'MIDDLE'),
        ('TOPPADDING', (0, total_row_idx), (-1, total_row_idx), 2),
        ('BOTTOMPADDING', (0, total_row_idx), (-1, total_row_idx), 2),
        ('LEFTPADDING', (0, total_row_idx), (-1, total_row_idx), 5),
        ('RIGHTPADDING', (0, total_row_idx), (-1, total_row_idx), 5),
    ]))

    f_decl_title = ParagraphStyle('F_DeclTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, spaceAfter=2.5)
    f_decl = ParagraphStyle('F_Decl', parent=styles['Normal'], fontName='Helvetica', fontSize=7.4, leading=9.2, spaceAfter=1.5)
    f_sig_title = ParagraphStyle('F_SigTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1)
    f_sig_rule = ParagraphStyle('F_SigRule', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9, alignment=1)
    f_sig_lbl = ParagraphStyle('F_SigLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=1)

    sender_display_name = str(sender.get('name') or 'SENDER').strip().upper()

    # Table 4: Words & Declaration / Signature (Total Width: 543 pt => Cols A-F: 374, Cols G-I: 169)
    # The dividing line at 374 pt aligns with the items table's Quantity/RATE column boundary
    decl_paragraphs = [
        Paragraph("<b>DECLARATION</b>", f_decl_title),
        Paragraph("1. We hereby declare that the goods described in this invoice are of Indian origin, and the prices stated represent the actual value of the goods.", f_decl),
        Paragraph("2. We certify that all particulars and information provided in this invoice are true, correct, and complete to the best of our knowledge.", f_decl),
        Paragraph("3. The description, quantity, and value of the goods have been accurately stated in this invoice.", f_decl),
        Paragraph("4. The goods are intended for personal use only and are not intended for commercial resale, where applicable.", f_decl),
        Paragraph("5. The shipment details and other particulars stated in this invoice are provided for customs clearance and shipping purposes.", f_decl),
        Paragraph("6. We accept responsibility for the accuracy of the information and documents provided in connection with this shipment.", f_decl),
        Paragraph("7. This invoice has been issued in good faith for the purpose of shipment, customs assessment, and related documentation.", f_decl),
    ]

    sig_paragraphs = [
        Paragraph(f"<b>For {sender_display_name}</b>", f_sig_title),
        Paragraph("<br/><br/><br/>", f_sig_title),
        Paragraph("___________________________________", f_sig_rule),
        Paragraph("Authorized Signatory", f_sig_lbl),
    ]

    footer_data = [
        [
            Paragraph(f"<b>IN WORDS : &nbsp; {words_text}</b>", f_body_b),
            "",
        ],
        [
            decl_paragraphs,
            "",
        ],
        [
            "",
            sig_paragraphs,
        ]
    ]

    footer_table = Table(footer_data, colWidths=[308, 235])
    footer_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('VALIGN', (0, 1), (-1, 1), 'TOP'),
        ('VALIGN', (1, 2), (1, 2), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, 0), 3),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
        ('TOPPADDING', (0, 1), (-1, 1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 3),
        ('TOPPADDING', (0, 2), (-1, 2), 6),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    story = [
        header_table,
        route_table,
        items_table,
        footer_table,
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer
