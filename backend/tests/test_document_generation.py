import zipfile
import io
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.templates.invoice_template import generate_invoice_pdf
from app.templates.challan_template import generate_challan_pdf
from app.templates.address_template import generate_address_pdf, generate_address_docx
from app.templates.booking_awb_template import generate_booking_awb_pdf

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}

SAMPLE_PAYLOAD = {
    "doc_type": "invoice",
    "doc_number": "INV-2026-0001",
    "date": "2026-10-22",
    "sender": {
        "name": "Alpha Traders Ltd",
        "address_line_1": "Plot 42, Tech Park Road",
        "city": "Hyderabad",
        "state": "Telangana",
        "postal_code": "500081",
        "phone": "+91 9876543210",
        "gstin": "36AAAAA0000A1Z5",
    },
    "customer": {
        "name": "Omega Solutions",
        "address_line_1": "Tower B, Level 4",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560100",
        "phone": "+91 9123456780",
    },
    "items": [
        {"name": "Packaging Boxes", "count": "10", "price": "2500"},
        {"name": "Bubble Wrap", "count": "2", "price": "900"},
    ],
    "total": "3400.00",
    "notes": "Thank you for doing business with us.",
}


def test_invoice_pdf_generator():
    buf = generate_invoice_pdf(SAMPLE_PAYLOAD)
    data = buf.getvalue()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000


def test_challan_pdf_generator():
    challan_data = dict(SAMPLE_PAYLOAD, doc_type="challan", doc_number="DC-2026-0001")
    buf = generate_challan_pdf(challan_data)
    data = buf.getvalue()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000


def test_address_pdf_and_docx():
    pdf_buf = generate_address_pdf(SAMPLE_PAYLOAD)
    assert pdf_buf.getvalue().startswith(b"%PDF")

    docx_buf = generate_address_docx(SAMPLE_PAYLOAD)
    assert len(docx_buf.getvalue()) > 500


def test_endpoint_requires_api_key():
    payload = dict(SAMPLE_PAYLOAD, include_address_label=False)
    # Request without API key should be rejected with 401
    res_unauth = client.post("/api/v1/documents/generate-download", json=payload)
    assert res_unauth.status_code == 401

    # Request with invalid API key should also be rejected
    res_invalid = client.post(
        "/api/v1/documents/generate-download",
        json=payload,
        headers={"X-API-Key": "invalid-token-123"}
    )
    assert res_invalid.status_code == 401


def test_download_single_invoice_pdf():
    payload = dict(SAMPLE_PAYLOAD, include_address_label=False)
    response = client.post("/api/v1/documents/generate-download", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "Invoice_INV-2026-0001.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_download_direct_address_label_pdf():
    """Verify direct standalone address label PDF download without ZIP archive."""
    payload = dict(SAMPLE_PAYLOAD, doc_type="address", address_format="pdf", include_address_label=False)
    response = client.post("/api/v1/documents/generate-download", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "INV-2026-0001.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_download_direct_address_label_docx():
    """Verify direct standalone address label DOCX download without ZIP archive."""
    payload = dict(SAMPLE_PAYLOAD, doc_type="address", address_format="docx", include_address_label=False)
    response = client.post("/api/v1/documents/generate-download", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
    assert "Address_Label_INV-2026-0001.docx" in response.headers["content-disposition"]
    assert len(response.content) > 1000


def test_user_defined_total_preservation():
    """Verify that user-defined total is not overridden by item sum."""
    custom_total_payload = dict(
        SAMPLE_PAYLOAD,
        doc_number="INV-CUSTOM-TOTAL-01",
        items=[
            {"name": "Item A", "count": "1", "price": "100"},
            {"name": "Item B", "count": "1", "price": "200"},
        ],
        total="999.00",  # Deliberately different from 300.00
        include_address_label=False
    )
    res = client.post("/api/v1/documents/generate-download", json=custom_total_payload, headers=AUTH_HEADERS)
    assert res.status_code == 200

    # Retrieve and verify total from SQLite
    get_res = client.get("/api/v1/documents/INV-CUSTOM-TOTAL-01", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    assert get_res.json()["total"] == "999.00"


def test_booking_awb_pdf_generator():
    booking_payload = dict(
        SAMPLE_PAYLOAD,
        doc_type="booking",
        doc_number="AWB-USA-0001",
        service_partner="DHL Express",
        destination_country="USA",
        chargeable_weight="2.5",
        rate_per_kg="1500.00",
        freight_amount="3750.00",
        other_charges="250.00",
        discount="100.00",
        total="3900.00",
        payment_status="PAID",
        payment_mode="UPI",
    )
    buf = generate_booking_awb_pdf(booking_payload)
    data = buf.getvalue()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000


def test_download_direct_booking_awb_pdf():
    booking_payload = dict(
        SAMPLE_PAYLOAD,
        doc_type="booking",
        doc_number="AWB-USA-0001",
        service_partner="FedEx Priority",
        destination_country="USA",
        chargeable_weight="3.0",
        rate_per_kg="1400.00",
        total="4200.00",
        payment_status="PAID",
        payment_mode="UPI",
    )
    response = client.post("/api/v1/documents/generate-download", json=booking_payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "AWB-USA-0001.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_save_booking_record_endpoint():
    booking_payload = dict(
        SAMPLE_PAYLOAD,
        doc_type="booking",
        doc_number="AWB-SAVE-0001",
        service_partner="DHL Express",
        destination_country="USA",
        package_type="Document",
        weight="2.5KG",
        total="1500.00",
        payment_status="PAID",
        payment_mode="UPI",
    )
    res = client.post("/api/v1/documents/save", json=booking_payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    assert res.json()["doc_number"] == "AWB-SAVE-0001"

    # Verify saved in SQLite
    get_res = client.get("/api/v1/documents/AWB-SAVE-0001", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    assert get_res.json()["doc_number"] == "AWB-SAVE-0001"


def test_invoice_pdf_with_awb_number():
    invoice_payload = dict(
        SAMPLE_PAYLOAD,
        doc_number="INV-AWB-TEST-01",
        awb_number="AWB-USA-9999",
        weight="5KG",
    )
    buf = generate_invoice_pdf(invoice_payload)
    data = buf.getvalue()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000
