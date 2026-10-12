from fastapi import APIRouter
from app.services.backup_service import backup_database, list_backups

router = APIRouter()


@router.get("")
def get_backups():
    """List all available database backups."""
    backups = list_backups()
    return {"backups": backups, "count": len(backups)}


@router.post("")
def trigger_backup():
    """Trigger an online snapshot backup of the SQLite database."""
    backup_path = backup_database()
    return {
        "success": True,
        "backup_file": backup_path.name,
        "path": str(backup_path),
        "message": "Database backup completed successfully.",
    }
