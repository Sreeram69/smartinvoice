import io
from typing import Dict, Any, Tuple
from app.templates.invoice_template import generate_invoice_pdf
from app.templates.invoice_xlsx_template import generate_invoice_xlsx
from app.templates.challan_template import generate_challan_pdf
from app.templates.address_template import generate_address_pdf, generate_address_docx
from app.templates.booking_awb_template import generate_booking_awb_pdf


def create_document_package(data: Dict[str, Any]) -> Tuple[io.BytesIO, str, str]:
    """
    Creates and returns direct individual files (Zero ZIP files):
      1. Address Label (doc_type == 'address' or 'address_label'):
         - Word (.docx) matching 'DUBAI.docx' (default) or PDF.
      2. Tax Invoice (doc_type == 'invoice'):
         - PDF matching commercial shipping layout or Excel (.xlsx) matching 'INVOICE format.xlsx'.
      3. Delivery Challan (doc_type == 'challan'):
         - PDF.
    """
    doc_type = data.get('doc_type', 'invoice').lower()
    doc_number = data.get('doc_number', 'DOC-001').replace(' ', '_').replace('/', '_')
    address_format = data.get('address_format', 'pdf').lower()
    invoice_format = data.get('invoice_format', 'pdf').lower()

    # 1. Address Label requested
    if doc_type in ['address', 'address_label'] or data.get('address_only'):
        if address_format == 'docx':
            addr_buf = generate_address_docx(data)
            return (
                addr_buf,
                f"Address_Label_{doc_number}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            addr_buf = generate_address_pdf(data)
            fn = f"{doc_number}.pdf"
            return addr_buf, fn, "application/pdf"

    # 2. Booking AWB Receipt requested
    if doc_type in ['booking', 'awb']:
        booking_buf = generate_booking_awb_pdf(data)
        fn = f"{doc_number}.pdf" if doc_number.startswith("AWB-") or doc_number.startswith("BK-") else f"Booking_AWB_{doc_number}.pdf"
        return booking_buf, fn, "application/pdf"

    # 3. Tax Invoice (PDF or Excel)
    if invoice_format == 'xlsx':
        xlsx_buf = generate_invoice_xlsx(data)
        return (
            xlsx_buf,
            f"Invoice_{doc_number}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    elif doc_type == 'challan':
        challan_buf = generate_challan_pdf(data)
        return challan_buf, f"Challan_{doc_number}.pdf", "application/pdf"
    else:
        pdf_buf = generate_invoice_pdf(data)
        return pdf_buf, f"Invoice_{doc_number}.pdf", "application/pdf"
