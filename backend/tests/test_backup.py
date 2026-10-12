from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.backup_service import backup_database, list_backups

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


def test_backup_service_direct():
    backup_path = backup_database()
    assert backup_path.exists()
    assert backup_path.name.startswith("smartinvoice_backup_")

    backups = list_backups()
    assert len(backups) > 0
    assert any(b["filename"] == backup_path.name for b in backups)


def test_backup_endpoints_auth():
    # Unauthorized requests fail
    assert client.get("/api/v1/backup").status_code == 401
    assert client.post("/api/v1/backup").status_code == 401


def test_backup_api_endpoints():
    # Trigger backup via API
    post_res = client.post("/api/v1/backup", headers=AUTH_HEADERS)
    assert post_res.status_code == 200
    data = post_res.json()
    assert data["success"] is True
    assert "backup_file" in data

    # List backups via API
    get_res = client.get("/api/v1/backup", headers=AUTH_HEADERS)
    assert get_res.status_code == 200
    backups_data = get_res.json()
    assert "backups" in backups_data
    assert backups_data["count"] > 0
