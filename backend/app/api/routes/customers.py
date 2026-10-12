from fastapi import APIRouter
from app.schemas.document import AddressModel
from app.services.sqlite_service import save_customer_sqlite, list_customers_sqlite

router = APIRouter()


@router.get("")
def get_customers():
    """
    Retrieves saved customers from local SQLite for fast search and autofill.
    """
    customers = list_customers_sqlite()
    return {"customers": customers, "count": len(customers)}


@router.post("")
def create_or_update_customer(customer: AddressModel):
    """
    Saves or updates a customer in local SQLite.
    """
    res = save_customer_sqlite(customer.model_dump())
    return res
