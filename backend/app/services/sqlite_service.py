import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import DATA_DIR

logger = logging.getLogger(__name__)

DB_PATH = DATA_DIR / "smartinvoice.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_sqlite_db():
    """Initializes SQLite tables for local documents and customer profiles."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Documents Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT NOT NULL,
                doc_number TEXT NOT NULL UNIQUE,
                date TEXT NOT NULL,
                sender TEXT NOT NULL,
                customer TEXT NOT NULL,
                items TEXT NOT NULL,
                total TEXT NOT NULL,
                notes TEXT,
                transport_mode TEXT,
                vehicle_number TEXT,
                created_at TEXT NOT NULL
            )
        """)
        # Customers Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                address_line_1 TEXT,
                address_line_2 TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                phone TEXT,
                gstin TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


# Initialize database schema immediately on load
init_sqlite_db()


def save_document_sqlite(data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves or updates a document record in local SQLite."""
    doc_number = data.get("doc_number")
    now_iso = datetime.now(timezone.utc).isoformat()
    
    sender_json = json.dumps(data.get("sender", {}))
    customer_json = json.dumps(data.get("customer", {}))
    items_json = json.dumps(data.get("items", []))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (doc_type, doc_number, date, sender, customer, items, total, notes, transport_mode, vehicle_number, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(doc_number) DO UPDATE SET
                date=excluded.date,
                sender=excluded.sender,
                customer=excluded.customer,
                items=excluded.items,
                total=excluded.total,
                notes=excluded.notes,
                transport_mode=excluded.transport_mode,
                vehicle_number=excluded.vehicle_number,
                created_at=excluded.created_at
        """, (
            data.get("doc_type", "invoice"),
            doc_number,
            data.get("date"),
            sender_json,
            customer_json,
            items_json,
            str(data.get("total", "0.00")),
            data.get("notes"),
            data.get("transport_mode"),
            data.get("vehicle_number"),
            now_iso,
        ))
        conn.commit()

    # Automatically save customer profile as well
    customer = data.get("customer")
    if customer and customer.get("name"):
        save_customer_sqlite(customer)

    return {"success": True, "source": "sqlite", "doc_number": doc_number}


def list_documents_sqlite(doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all past documents from local SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if doc_type:
            cursor.execute("SELECT * FROM documents WHERE doc_type = ? ORDER BY created_at DESC", (doc_type,))
        else:
            cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "doc_type": row["doc_type"],
                "doc_number": row["doc_number"],
                "date": row["date"],
                "sender": json.loads(row["sender"]),
                "customer": json.loads(row["customer"]),
                "items": json.loads(row["items"]),
                "total": row["total"],
                "notes": row["notes"],
                "transport_mode": row["transport_mode"],
                "vehicle_number": row["vehicle_number"],
                "created_at": row["created_at"],
            })
        return result


def get_document_by_number_sqlite(doc_number: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single document by number from local SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE doc_number = ?", (doc_number,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "doc_type": row["doc_type"],
            "doc_number": row["doc_number"],
            "date": row["date"],
            "sender": json.loads(row["sender"]),
            "customer": json.loads(row["customer"]),
            "items": json.loads(row["items"]),
            "total": row["total"],
            "notes": row["notes"],
            "transport_mode": row["transport_mode"],
            "vehicle_number": row["vehicle_number"],
            "created_at": row["created_at"],
        }


def save_customer_sqlite(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Saves or updates a customer profile in local SQLite."""
    name = customer.get("name", "").strip()
    if not name:
        return {"success": False, "error": "Customer name is required"}

    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (name, address_line_1, address_line_2, city, state, postal_code, phone, gstin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                address_line_1=excluded.address_line_1,
                address_line_2=excluded.address_line_2,
                city=excluded.city,
                state=excluded.state,
                postal_code=excluded.postal_code,
                phone=excluded.phone,
                gstin=excluded.gstin
        """, (
            name,
            customer.get("address_line_1"),
            customer.get("address_line_2"),
            customer.get("city"),
            customer.get("state"),
            customer.get("postal_code"),
            customer.get("phone"),
            customer.get("gstin"),
            now_iso,
        ))
        conn.commit()
    return {"success": True, "name": name}


def list_customers_sqlite() -> List[Dict[str, Any]]:
    """Retrieves saved customers from local SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY created_at DESC LIMIT 100")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_document_sqlite(doc_number: str) -> bool:
    """Deletes a document by document number from local SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE doc_number = ?", (doc_number,))
        conn.commit()
        return cursor.rowcount > 0


import re

def sanitize_country_code(country: str) -> str:
    c = (country or "").strip().upper()
    if not c:
        return "DEST"
    if "USA" in c or "UNITED STATES" in c or "AMERICA" in c:
        return "USA"
    if "UAE" in c or "EMIRATES" in c or "DUBAI" in c or "ABU DHABI" in c:
        return "UAE"
    if "UK" in c or "UNITED KINGDOM" in c or "ENGLAND" in c or "LONDON" in c:
        return "UK"
    if "CANADA" in c:
        return "CANADA"
    if "AUSTRALIA" in c:
        return "AUSTRALIA"
    if "GERMANY" in c:
        return "GERMANY"
    if "SINGAPORE" in c:
        return "SINGAPORE"
    if "INDIA" in c:
        return "INDIA"
    cleaned = re.sub(r'[^A-Z0-9]', '', c)
    return cleaned[:10] if cleaned else "DEST"


def get_next_document_number(doc_type: str = "invoice", country: str = "") -> str:
    """Finds highest document number and generates next sequential number."""
    if doc_type in ["address", "address_label"]:
        c_code = sanitize_country_code(country)
        prefix = f"ADD-{c_code}"
        pattern = f"{prefix}-%"

        max_num = 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT doc_number FROM documents WHERE (doc_type = 'address' OR doc_type = 'address_label') AND doc_number LIKE ?",
                (pattern,)
            )
            rows = cursor.fetchall()
            for r in rows:
                parts = r["doc_number"].split("-")
                if parts and parts[-1].isdigit():
                    max_num = max(max_num, int(parts[-1]))

        try:
            from app.services.supabase_service import get_supabase_client
            client = get_supabase_client()
            if client:
                res = client.table("documents").select("doc_number").like("doc_number", f"{prefix}-%").execute()
                if res.data:
                    for r in res.data:
                        parts = r["doc_number"].split("-")
                        if parts and parts[-1].isdigit():
                            max_num = max(max_num, int(parts[-1]))
        except Exception:
            pass

        return f"{prefix}-{(max_num + 1):04d}"
    elif doc_type in ["booking", "awb"]:
        c_code = sanitize_country_code(country)
        prefix = f"AWB-{c_code}"
        pattern = f"{prefix}-%"

        max_num = 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT doc_number FROM documents WHERE (doc_type = 'booking' OR doc_type = 'awb') AND doc_number LIKE ?",
                (pattern,)
            )
            rows = cursor.fetchall()
            for r in rows:
                parts = r["doc_number"].split("-")
                if parts and parts[-1].isdigit():
                    max_num = max(max_num, int(parts[-1]))

        try:
            from app.services.supabase_service import get_supabase_client
            client = get_supabase_client()
            if client:
                res = client.table("documents").select("doc_number").like("doc_number", f"{prefix}-%").execute()
                if res.data:
                    for r in res.data:
                        parts = r["doc_number"].split("-")
                        if parts and parts[-1].isdigit():
                            max_num = max(max_num, int(parts[-1]))
        except Exception:
            pass

        return f"{prefix}-{(max_num + 1):04d}"
    else:
        year = datetime.now().year
        prefix = "INV" if doc_type == "invoice" else "DC"
        pattern = f"{prefix}-{year}-%"

        max_num = 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT doc_number FROM documents WHERE doc_type = ? AND doc_number LIKE ? ORDER BY id DESC",
                (doc_type, pattern)
            )
            rows = cursor.fetchall()
            for r in rows:
                parts = r["doc_number"].split("-")
                if len(parts) >= 3 and parts[-1].isdigit():
                    max_num = max(max_num, int(parts[-1]))

        try:
            from app.services.supabase_service import get_supabase_client
            client = get_supabase_client()
            if client:
                res = client.table("documents").select("doc_number").like("doc_number", f"{prefix}-{year}-%").execute()
                if res.data:
                    for r in res.data:
                        parts = r["doc_number"].split("-")
                        if len(parts) >= 3 and parts[-1].isdigit():
                            max_num = max(max_num, int(parts[-1]))
        except Exception:
            pass

        return f"{prefix}-{year}-{(max_num + 1):04d}"

