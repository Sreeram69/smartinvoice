from fastapi import APIRouter
from app.schemas.item import ItemParseRequest, ItemParseResponse
from app.services.item_parser import parse_spoken_item

router = APIRouter()


@router.post("/parse-speech", response_model=ItemParseResponse)
def parse_speech_endpoint(payload: ItemParseRequest):
    result = parse_spoken_item(payload.speech_text)
    return {
        "success": True,
        "name": result["name"],
        "count": result["count"],
        "price": result["price"],
        "raw_text": result["raw_text"],
    }
