import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from app.core.config import settings, DATA_DIR

BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def backup_database() -> Path:
    """
    Creates a timestamped, consistent backup copy of the SQLite database.
    Uses SQLite's online backup API for safe, non-corrupt copies even if writes are active.
    """
    source_db = settings.DATABASE_PATH
    if not source_db.exists():
        # Empty DB, initialize it
        return source_db

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"smartinvoice_backup_{timestamp}.db"

    # Online backup using sqlite3.backup API
    source_conn = sqlite3.connect(str(source_db))
    dest_conn = sqlite3.connect(str(backup_file))
    with dest_conn:
        source_conn.backup(dest_conn)
    source_conn.close()
    dest_conn.close()

    # Retain only the 10 most recent backups
    all_backups = sorted(BACKUP_DIR.glob("smartinvoice_backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old_backup in all_backups[10:]:
        try:
            old_backup.unlink()
        except Exception:
            pass

    return backup_file


def list_backups() -> list[dict]:
    """Lists available backups with timestamps and sizes."""
    all_backups = sorted(BACKUP_DIR.glob("smartinvoice_backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for b in all_backups:
        result.append({
            "filename": b.name,
            "path": str(b),
            "size_bytes": b.stat().st_size,
            "created_at": datetime.fromtimestamp(b.stat().st_mtime, timezone.utc).isoformat(),
        })
    return result
