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
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_challan_pdf(data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a Delivery Challan PDF matching industrial transport standards.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    header_title_style = ParagraphStyle(
        'ChallanHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0A0A0A'),
    )

    sub_title_style = ParagraphStyle(
        'ChallanSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#EB0029'),
        alignment=2,
    )

    label_style = ParagraphStyle(
        'ChallanLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#555555'),
        textTransform='uppercase',
    )

    body_style = ParagraphStyle(
        'ChallanBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1A1A1A'),
    )

    table_header_style = ParagraphStyle(
        'CTableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        'CTableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1A1A1A'),
    )

    table_cell_right = ParagraphStyle(
        'CTableCellRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0A0A0A'),
        alignment=2,
    )

    story = []

    # 1. Header & Challan Info
    doc_number = data.get('doc_number', 'DC-2026-0001')
    doc_date = data.get('date', '2026-10-22')
    transport_mode = data.get('transport_mode') or 'By Road'
    vehicle_number = data.get('vehicle_number') or 'N/A'

    top_table_data = [
        [
            Paragraph("<b>DELIVERY CHALLAN</b>", header_title_style),
            Paragraph(f"CHALLAN NO: <b>{doc_number}</b><br/><font color='#555555'>DATE: {doc_date}</font>", sub_title_style),
        ]
    ]
    top_table = Table(top_table_data, colWidths=[320, 200])
    top_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(top_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#EB0029'), spaceAfter=12))

    # Transport / Dispatch Metadata
    transport_meta = [
        [
            Paragraph(f"<b>DISPATCH MODE:</b> {transport_mode}", body_style),
            Paragraph(f"<b>VEHICLE NO:</b> {vehicle_number}", body_style),
            Paragraph("<b>SUPPLY TYPE:</b> Delivery / Job Work", body_style),
        ]
    ]
    meta_table = Table(transport_meta, colWidths=[175, 175, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EEEEEE')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D0D0D0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 2. Consignor & Consignee
    sender = data.get('sender', {})
    customer = data.get('customer', {})

    sender_lines = [
        f"<b>{sender.get('name', 'Consignor / Sender')}</b>",
        sender.get('address_line_1', ''),
        sender.get('address_line_2', ''),
        f"{sender.get('city', '')} {sender.get('state', '')} {sender.get('postal_code', '')}".strip(),
        f"Contact: {sender.get('phone', 'N/A')}",
    ]
    sender_text = "<br/>".join([line for line in sender_lines if line])

    customer_lines = [
        f"<b>{customer.get('name', 'Consignee / Recipient')}</b>",
        customer.get('address_line_1', ''),
        customer.get('address_line_2', ''),
        f"{customer.get('city', '')} {customer.get('state', '')} {customer.get('postal_code', '')}".strip(),
        f"Contact: {customer.get('phone', 'N/A')}",
    ]
    customer_text = "<br/>".join([line for line in customer_lines if line])

    addr_data = [
        [Paragraph("FROM (CONSIGNOR):", label_style), Paragraph("TO (CONSIGNEE):", label_style)],
        [Paragraph(sender_text, body_style), Paragraph(customer_text, body_style)],
    ]
    addr_table = Table(addr_data, colWidths=[260, 260])
    addr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F8F8')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E0E0E0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#EBEBEB')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(addr_table)
    story.append(Spacer(1, 14))

    # 3. Goods Items Table
    items: List[Dict[str, Any]] = data.get('items', [])
    item_rows = [
        [
            Paragraph("#", table_header_style),
            Paragraph("DESCRIPTION OF GOODS", table_header_style),
            Paragraph("QUANTITY / COUNT", table_header_style),
            Paragraph("DECLARED VALUE (INR)", ParagraphStyle('HRightC', parent=table_header_style, alignment=2)),
        ]
    ]

    for idx, it in enumerate(items, 1):
        name = it.get('name', f"Item {idx}")
        count = str(it.get('count', '1'))
        price = str(it.get('price', '0.00'))
        item_rows.append([
            Paragraph(str(idx), table_cell_style),
            Paragraph(name, table_cell_style),
            Paragraph(count, table_cell_style),
            Paragraph(f"INR {price}", table_cell_right),
        ])

    if not items:
        item_rows.append([
            Paragraph("1", table_cell_style),
            Paragraph("Goods for delivery", table_cell_style),
            Paragraph("1", table_cell_style),
            Paragraph("INR 0.00", table_cell_right),
        ])

    item_table = Table(item_rows, colWidths=[30, 270, 100, 120])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#141414')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FAFAFA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 12))

    # Total row
    total_val = str(data.get('total', '0.00'))
    total_data = [
        [Paragraph("<b>TOTAL DECLARED VALUE:</b>", ParagraphStyle('CDLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=2)),
         Paragraph(f"<b>INR {total_val}</b>", ParagraphStyle('CDVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#0A0A0A'), alignment=2))]
    ]
    total_table = Table(total_data, colWidths=[380, 140])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F2F2F2')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D0D0D0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 14))

    # Declaration & Dual Signatures
    declaration = "Declaration: We declare that this delivery challan shows the actual quantity of goods described and that all particulars are true and correct."
    story.append(Paragraph(f"<i>{declaration}</i>", ParagraphStyle('DecStyle', parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor('#555555'))))
    story.append(Spacer(1, 14))

    sign_data = [
        [
            Paragraph("<b>RECEIVER'S ACKNOWLEDGEMENT:</b><br/><br/><br/>____________________________<br/>Receiver's Signature & Date", body_style),
            Paragraph("<b>FOR SENDER / CONSIGNOR:</b><br/><br/><br/>____________________________<br/>Authorized Signatory", ParagraphStyle('SignRight', parent=body_style, alignment=2)),
        ]
    ]
    sign_table = Table(sign_data, colWidths=[260, 260])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sign_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
