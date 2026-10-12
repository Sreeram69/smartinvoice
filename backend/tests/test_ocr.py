import io
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.address_parser import parse_address_blocks

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


def create_dummy_image_bytes() -> bytes:
    img = Image.new("RGB", (300, 150), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_parse_address_blocks_with_markers():
    sample_text = (
        "FROM: TechCorp Solutions\n"
        "Plot 99, Cyber City\n"
        "Hyderabad, Telangana - 500081\n"
        "Phone: +91 9876543210\n\n"
        "TO: Acme Global Logistics\n"
        "Harbor Gate 4\n"
        "Kolkata, West Bengal - 700001\n"
        "Phone: +91 9123456789\n"
    )
    result = parse_address_blocks(sample_text)
    assert result["requires_review"] is True
    assert "TechCorp" in result["sender"]["name"]
    assert "Acme" in result["customer"]["name"]
    assert "500081" in result["sender"]["postal_code"]
    assert "700001" in result["customer"]["postal_code"]
    assert "9876543210" in result["sender"]["phone"]
    assert "9123456789" in result["customer"]["phone"]
    assert result["sender"]["city"].lower() == "hyderabad"
    assert result["customer"]["city"].lower() == "kolkata"


def test_parse_dubai_address_format():
    dubai_sample = (
        "TO,\n"
        "JAFFAR MIRZA\n"
        "BLVD FNO 102\n"
        "PT-655D ASTER HOSPITAL\n"
        "AL RAFFA,BUR\n"
        "DUBAI\n"
        "971523010566\n"
        "FROM\n"
        "KOVELAKONDA MOHAN RAO\n"
        "16-42-41/3,INDRA COL\n"
        "KAKINADA\n"
    )
    result = parse_address_blocks(dubai_sample)
    cust = result["customer"]
    send = result["sender"]

    assert "JAFFAR MIRZA" in cust["name"]
    assert "BLVD FNO 102" in cust["address_line_1"]
    assert "ASTER HOSPITAL" in cust["address_line_2"]
    assert cust["city"].upper() == "DUBAI"
    assert cust["phone"] == "971523010566"

    assert "KOVELAKONDA MOHAN RAO" in send["name"]
    assert "16-42-41/3" in send["address_line_1"]
    assert send["city"].upper() == "KAKINADA"
    assert send["phone"] == ""  # Sender phone was not in text, must not steal customer phone


def test_parse_joined_ocr_pincode():
    text = (
        "FROM: SmartTech Enterprises\n"
        "Door No 4-10-12, Main Road\n"
        "KAKINADA533001\n"
        "Phone: 9177777249\n"
    )
    result = parse_address_blocks(text)
    send = result["sender"]
    assert send["postal_code"] == "533001"
    assert "KAKINADA" in send["city"].upper()
    assert send["phone"] == "9177777249"


def test_parse_single_customer_label_without_markers():
    text = (
        "Seethayya Nidadavolu\n"
        "215 Federal Row Dr, Apt #202\n"
        "Collierville, Tennessee - 38017\n"
        "Phone: +1 3322017939\n"
    )
    result = parse_address_blocks(text)
    cust = result["customer"]
    send = result["sender"]

    # When a single address label is uploaded without markers,
    # it is assigned cleanly to customer, not cut in half
    assert "Seethayya" in cust["name"]
    assert "215 Federal Row" in cust["address_line_1"]
    assert cust["postal_code"] == "38017"
    assert cust["city"].lower() == "collierville"
    assert cust["phone"] == "+1 3322017939"
    assert send["name"] == ""


def test_ocr_endpoint_requires_auth():
    img_bytes = create_dummy_image_bytes()
    response = client.post(
        "/api/v1/ocr/extract-address",
        files={"file": ("test_address.png", img_bytes, "image/png")}
    )
    assert response.status_code == 401


def test_ocr_api_endpoint():
    img_bytes = create_dummy_image_bytes()
    response = client.post(
        "/api/v1/ocr/extract-address",
        files={"file": ("test_address.png", img_bytes, "image/png")},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sender" in data
    assert "customer" in data
    assert data["requires_review"] is True
