from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.schemas.item import ItemLine


class AddressModel(BaseModel):
    name: str = Field(default="", description="Contact or company name")
    address_line_1: Optional[str] = Field(default="", description="Primary address line")
    address_line_2: Optional[str] = Field(default="", description="Secondary address line")
    city: Optional[str] = Field(default="", description="City")
    state: Optional[str] = Field(default="", description="State / Province")
    postal_code: Optional[str] = Field(default="", description="Postal or PIN code")
    phone: Optional[str] = Field(default="", description="Phone number")
    gstin: Optional[str] = Field(default="", description="Optional GSTIN or Tax ID")


class DocumentGenerateRequest(BaseModel):
    doc_type: Literal["invoice", "challan", "address", "address_label", "booking", "awb"] = Field(default="invoice")
    doc_number: str = Field(default="INV-2026-0001")

    date: str = Field(default="2026-10-24")
    sender: AddressModel
    customer: AddressModel
    items: List[ItemLine] = Field(default_factory=list)
    total: str = Field(default="0.00", description="User-specified document total")
    notes: Optional[str] = Field(default=None)
    transport_mode: Optional[str] = Field(default="By Road")
    vehicle_number: Optional[str] = Field(default=None)
    include_address_label: bool = Field(default=False)
    address_format: Literal["pdf", "docx"] = Field(default="pdf")
    invoice_format: Literal["pdf", "xlsx", "both"] = Field(default="pdf")
    weight: Optional[str] = Field(default="")
    awb_number: Optional[str] = Field(default="")
    # Booking AWB specific optional fields
    service_partner: Optional[str] = Field(default="DHL Express")
    package_type: Optional[str] = Field(default="Parcel")
    pieces: Optional[str] = Field(default="1")
    actual_weight: Optional[str] = Field(default="")
    volumetric_weight: Optional[str] = Field(default="")
    chargeable_weight: Optional[str] = Field(default="")
    rate_per_kg: Optional[str] = Field(default="")
    freight_amount: Optional[str] = Field(default="")
    other_charges: Optional[str] = Field(default="0.00")
    discount: Optional[str] = Field(default="0.00")
    payment_status: Optional[str] = Field(default="PAID")
    payment_mode: Optional[str] = Field(default="UPI")
    contents_description: Optional[str] = Field(default="Personal Goods / Effects")
    destination_country: Optional[str] = Field(default="")
    address_doc_number: Optional[str] = Field(default="", description="Specific ADD-COUNTRY-SERIES doc number")
