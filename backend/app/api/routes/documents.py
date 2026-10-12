from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.document import DocumentGenerateRequest
from app.services.document_service import create_document_package
from app.services.sqlite_service import (
    save_document_sqlite,
    list_documents_sqlite,
    get_document_by_number_sqlite,
    get_next_document_number,
    delete_document_sqlite,
)

router = APIRouter()


@router.get("/next-number")
def get_next_number_endpoint(doc_type: str = Query("invoice"), country: Optional[str] = Query(None)):
    """Calculates and returns the next sequential invoice or address label number."""
    next_num = get_next_document_number(doc_type, country=country or "")
    return {"doc_type": doc_type, "next_number": next_num}


@router.post("/generate-download")
def generate_and_download_document(payload: DocumentGenerateRequest):
    """
    Generates and returns:
      - Single PDF (Invoice or Challan) if include_address_label is False.
      - Combined ZIP containing PDF + Address Label (PDF or DOCX) if include_address_label is True.
    Automatically persists to local SQLite and cloud Supabase!
    """
    data = payload.model_dump()
    
    # 1. Automatically persist to local SQLite
    save_doc_data = dict(data)
    if save_doc_data.get("doc_type") in ["address", "address_label"]:
        save_doc_data["doc_type"] = "address"
    elif save_doc_data.get("doc_type") in ["booking", "awb"]:
        save_doc_data["doc_type"] = "booking"
    save_document_sqlite(save_doc_data)

    # 1a. If this is an invoice AND include_address_label is True, also persist an address label record
    if save_doc_data.get("doc_type") == "invoice" and data.get("include_address_label"):
        try:
            from app.services.sqlite_service import get_next_document_number
            country = data.get("customer", {}).get("country") or data.get("customer", {}).get("state") or data.get("customer", {}).get("city") or data.get("destination_country") or "USA"
            addr_num = data.get("address_doc_number") or get_next_document_number("address", country)
            addr_data = dict(data)
            addr_data["doc_type"] = "address"
            addr_data["doc_number"] = addr_num
            save_document_sqlite(addr_data)
            try:
                from app.services.supabase_service import save_document_record
                save_document_record(addr_data)
            except Exception:
                pass
        except Exception:
            pass

    # 1a. Automatically persist customer into customers table for Address Book
    try:
        from app.services.sqlite_service import save_customer_sqlite
        if data.get("customer") and data["customer"].get("name"):
            save_customer_sqlite(data["customer"])
    except Exception:
        pass

    # 1b. Automatically sync to Supabase cloud if configured
    try:
        from app.services.supabase_service import save_document_record
        save_document_record(save_doc_data)
    except Exception:
        pass

    # 2. Package and return the requested file
    buffer, filename, media_type = create_document_package(data)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }
    return StreamingResponse(buffer, media_type=media_type, headers=headers)


@router.post("/save")
def save_document_record_endpoint(payload: DocumentGenerateRequest):
    """
    Saves document (e.g. Booking AWB) to local SQLite and Supabase cloud archive
    without generating or downloading any file to the browser.
    """
    data = payload.model_dump()
    save_doc_data = dict(data)
    if save_doc_data.get("doc_type") in ["address", "address_label"]:
        save_doc_data["doc_type"] = "address"
    elif save_doc_data.get("doc_type") in ["booking", "awb"]:
        save_doc_data["doc_type"] = "booking"
    save_document_sqlite(save_doc_data)

    # 1a. If this is an invoice AND include_address_label is True, also persist an address label record
    if save_doc_data.get("doc_type") == "invoice" and data.get("include_address_label"):
        try:
            from app.services.sqlite_service import get_next_document_number
            country = data.get("customer", {}).get("country") or data.get("customer", {}).get("state") or data.get("customer", {}).get("city") or data.get("destination_country") or "USA"
            addr_num = data.get("address_doc_number") or get_next_document_number("address", country)
            addr_data = dict(data)
            addr_data["doc_type"] = "address"
            addr_data["doc_number"] = addr_num
            save_document_sqlite(addr_data)
            try:
                from app.services.supabase_service import save_document_record
                save_document_record(addr_data)
            except Exception:
                pass
        except Exception:
            pass

    try:
        from app.services.sqlite_service import save_customer_sqlite
        if data.get("customer") and data["customer"].get("name"):
            save_customer_sqlite(data["customer"])
    except Exception:
        pass

    try:
        from app.services.supabase_service import save_document_record
        save_document_record(save_doc_data)
    except Exception:
        pass

    return {
        "status": "success",
        "message": f"Document {payload.doc_number} saved successfully",
        "doc_number": payload.doc_number,
    }


@router.get("")
def get_documents_history(doc_type: Optional[str] = Query(None, description="Filter by invoice or challan")):
    """
    Retrieves all past documents from local SQLite.
    """
    docs = list_documents_sqlite(doc_type=doc_type)
    return {"documents": docs, "count": len(docs)}


@router.get("/{doc_number}")
def get_single_document(doc_number: str):
    """
    Retrieves single document by document number from local SQLite.
    """
    doc = get_document_by_number_sqlite(doc_number)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {doc_number} not found")
    return doc


@router.delete("/{doc_number}")
def delete_document_endpoint(doc_number: str):
    """
    Deletes a single document by document number from local SQLite (and Supabase if configured).
    """
    deleted = delete_document_sqlite(doc_number)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document {doc_number} not found")

    try:
        from app.services.supabase_service import get_supabase_client
        supabase = get_supabase_client()
        if supabase:
            supabase.table("documents").delete().eq("doc_number", doc_number).execute()
    except Exception:
        pass

    return {"success": True, "deleted": doc_number}
