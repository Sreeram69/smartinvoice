from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import extract_addresses_from_image

router = APIRouter()


@router.post("/extract-address")
async def extract_address_from_image(file: UploadFile = File(...)):
    """
    Accepts one photograph containing sender and customer addresses.
    Preprocesses the image, extracts text, identifies TO and FROM roles,
    and returns editable structured address blocks for manual review.
    """
    # Validate content type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type and file.content_type.lower() not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Supported formats: JPEG, PNG, WEBP.",
        )

    # Read image bytes
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Max 10MB limit
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    result = extract_addresses_from_image(content)
    return result
