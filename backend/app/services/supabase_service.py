import os
import json
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Supabase Client Wrapper
_supabase_client = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.warning("Supabase credentials not configured.")
        return None

    try:
        from supabase import create_client, Client
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return _supabase_client
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {e}")
        return None


def save_document_record(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves or updates a document record in the Supabase 'documents' table.
    """
    client = get_supabase_client()
    doc_number = data.get("doc_number")
    record = {
        "doc_type": data.get("doc_type", "invoice"),
        "doc_number": doc_number,
        "date": data.get("date"),
        "sender": data.get("sender"),
        "customer": data.get("customer"),
        "items": data.get("items", []),
        "total": str(data.get("total", "0.00")),
        "notes": data.get("notes"),
        "transport_mode": data.get("transport_mode"),
        "vehicle_number": data.get("vehicle_number"),
    }

    if client:
        try:
            # Check if document already exists
            existing = client.table("documents").select("id").eq("doc_number", doc_number).execute()
            if existing.data and len(existing.data) > 0:
                res = client.table("documents").update(record).eq("doc_number", doc_number).execute()
            else:
                res = client.table("documents").insert(record).execute()
            return {"success": True, "source": "supabase", "data": res.data}
        except Exception as e:
            logger.error(f"Supabase save_document failed: {e}")

    # Also automatically save customer details if provided
    customer = data.get("customer")
    if customer and customer.get("name"):
        save_customer_record(customer)

    return {"success": True, "source": "local_fallback", "record": record}


def list_documents(doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches documents from Supabase.
    """
    client = get_supabase_client()
    if client:
        try:
            query = client.table("documents").select("*").order("created_at", desc=True)
            if doc_type:
                query = query.eq("doc_type", doc_type)
            res = query.execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase list_documents failed: {e}")

    return []


def get_document_by_number(doc_number: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single document by doc_number.
    """
    client = get_supabase_client()
    if client:
        try:
            res = client.table("documents").select("*").eq("doc_number", doc_number).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase get_document failed: {e}")
    return None


def save_customer_record(customer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves or updates a customer in the 'customers' table.
    """
    name = customer.get("name", "").strip()
    if not name:
        return {"success": False, "error": "Customer name is required"}

    client = get_supabase_client()
    record = {
        "name": name,
        "address_line_1": customer.get("address_line_1"),
        "address_line_2": customer.get("address_line_2"),
        "city": customer.get("city"),
        "state": customer.get("state"),
        "postal_code": customer.get("postal_code"),
        "phone": customer.get("phone"),
        "gstin": customer.get("gstin"),
    }

    if client:
        try:
            # Check by name
            existing = client.table("customers").select("id").eq("name", name).execute()
            if existing.data and len(existing.data) > 0:
                res = client.table("customers").update(record).eq("name", name).execute()
            else:
                res = client.table("customers").insert(record).execute()
            return {"success": True, "source": "supabase", "data": res.data}
        except Exception as e:
            logger.error(f"Supabase save_customer failed: {e}")

    return {"success": True, "source": "local_fallback", "record": record}


def list_customers() -> List[Dict[str, Any]]:
    """
    Fetches saved customers for quick search and reuse.
    """
    client = get_supabase_client()
    if client:
        try:
            res = client.table("customers").select("*").order("created_at", desc=True).limit(50).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase list_customers failed: {e}")
    return []
