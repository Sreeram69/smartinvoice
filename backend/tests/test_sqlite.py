from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


def test_sqlite_endpoints_require_auth():
    res_docs = client.get("/api/v1/documents")
    assert res_docs.status_code == 401

    res_cust = client.get("/api/v1/customers")
    assert res_cust.status_code == 401


def test_sqlite_documents_history():
    response = client.get("/api/v1/documents", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_sqlite_customers_list():
    response = client.get("/api/v1/customers", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data
    assert isinstance(data["customers"], list)


def test_save_and_retrieve_sqlite_document():
    test_doc_number = "INV-SQLITE-TEST-101"
    payload = {
        "doc_type": "invoice",
        "doc_number": test_doc_number,
        "date": "2026-10-22",
        "sender": {
            "name": "Local Sender PC",
            "city": "Hyderabad",
            "phone": "+91 9999999999",
        },
        "customer": {
            "name": "Local Customer Phone",
            "city": "Vijayawada",
            "phone": "+91 8888888888",
        },
        "items": [
            {"name": "Local Processing Unit", "count": "1", "price": "5000"}
        ],
        "total": "5000.00",
        "include_address_label": False,
    }
    # Download endpoint automatically persists to local SQLite
    download_res = client.post("/api/v1/documents/generate-download", json=payload, headers=AUTH_HEADERS)
    assert download_res.status_code == 200

    # Retrieve from local SQLite
    get_res = client.get(f"/api/v1/documents/{test_doc_number}", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    doc_data = get_res.json()
    assert doc_data["doc_number"] == test_doc_number
    assert doc_data["total"] == "5000.00"
    assert doc_data["customer"]["name"] == "Local Customer Phone"
