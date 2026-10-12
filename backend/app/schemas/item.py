from typing import Optional, Union, Any
from pydantic import BaseModel, Field, field_validator


class ItemLine(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., description="Item name or description")
    count: str = Field(default="1", description="Count or quantity entered by user (voice or typed)")
    price: str = Field(default="0", description="Price or amount entered by user (voice or typed)")
    notes: Optional[str] = None

    @field_validator("count", "price", mode="before")
    @classmethod
    def coerce_to_str(cls, v: Any) -> str:
        if v is None:
            return ""
        return str(v)


class ItemParseRequest(BaseModel):
    speech_text: str


class ItemParseResponse(BaseModel):
    success: bool
    name: str
    count: str
    price: str
    raw_text: str
