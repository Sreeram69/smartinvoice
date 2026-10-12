import io
import shutil
import logging
from typing import Dict, Any, Tuple, List
from PIL import Image, ImageOps, ImageEnhance
from app.core.config import settings
from app.services.address_parser import parse_address_blocks

logger = logging.getLogger(__name__)


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """
    Preprocesses an uploaded photo to optimize OCR accuracy and minimize memory consumption:
    - Auto-orients mobile camera photos using EXIF tags (exif_transpose).
    - Converts RGBA / CMYK / Grayscale to RGB.
    - Limits max dimensions to 2048px preserving aspect ratio.
    - Enhances contrast and sharpness for crisp text line extraction.
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Correct smartphone camera orientation
    try:
        img = ImageOps.exif_transpose(img)
    except Exception as e:
        logger.debug(f"EXIF transpose skipped: {e}")

    # Convert to RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize oversized images preserving aspect ratio
    max_dim = 2048
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    # Moderate contrast and sharpness boost
    try:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.25)
        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(1.2)
    except Exception as e:
        logger.debug(f"Image enhancement skipped: {e}")

    return img


def order_ocr_results(ocr_results: List[Any]) -> str:
    """
    Orders OCR text boxes intelligently:
    - If a 2-column layout (e.g. FROM on left, TO on right) is present, groups column-by-column.
    - Otherwise, sorts natural top-to-bottom reading order.
    """
    if not ocr_results:
        return ""

    boxes = []
    for item in ocr_results:
        if not item or len(item) < 2 or not item[1]:
            continue
        poly = item[0]
        text = str(item[1]).strip()
        if not text:
            continue
        xs = [pt[0] for pt in poly]
        ys = [pt[1] for pt in poly]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        boxes.append({
            'text': text,
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'center_x': (min_x + max_x) / 2.0,
            'center_y': (min_y + max_y) / 2.0,
        })

    if not boxes:
        return ""

    all_min_x = min(b['min_x'] for b in boxes)
    all_max_x = max(b['max_x'] for b in boxes)
    width = all_max_x - all_min_x

    # Check for 2 distinct columns (e.g. sender column left, customer column right)
    if width > 150:
        mid_x = all_min_x + width / 2.0
        left_boxes = [b for b in boxes if b['max_x'] < mid_x + width * 0.12 and b['center_x'] < mid_x]
        right_boxes = [b for b in boxes if b['min_x'] > mid_x - width * 0.12 and b['center_x'] >= mid_x]

        if len(left_boxes) >= 2 and len(right_boxes) >= 2 and (len(left_boxes) + len(right_boxes) >= len(boxes) * 0.85):
            left_boxes.sort(key=lambda b: b['min_y'])
            right_boxes.sort(key=lambda b: b['min_y'])
            left_text = "\n".join(b['text'] for b in left_boxes)
            right_text = "\n".join(b['text'] for b in right_boxes)
            return f"{left_text}\n\n{right_text}"

    # Default: Natural vertical sort by y, then x
    boxes.sort(key=lambda b: (b['min_y'], b['min_x']))
    return "\n".join(b['text'] for b in boxes)


def run_ocr(img: Image.Image) -> Tuple[str, str]:
    """
    Runs OCR on the given PIL Image.
    Uses RapidOCR (deep learning ONNX models) first for fast, standalone offline execution.
    Falls back to Tesseract if available.
    Returns (extracted_text, engine_used).
    """
    # 1. RapidOCR (Fast, highly accurate, works offline on Windows without extra system installs)
    try:
        from rapidocr_onnxruntime import RapidOCR
        import numpy as np
        engine = RapidOCR()
        res, _ = engine(np.array(img))
        if res:
            text = order_ocr_results(res).strip()
            if text:
                return text, "rapidocr"
    except Exception as e:
        logger.warning(f"RapidOCR failed: {e}")

    # 2. Tesseract OCR fallback
    try:
        if shutil.which(settings.TESSERACT_CMD):
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            gray = img.convert('L')
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(1.4)
            text = pytesseract.image_to_string(enhanced, config='--oem 3 --psm 6').strip()
            if text:
                return text, "tesseract"
    except Exception as e:
        logger.warning(f"Tesseract OCR failed: {e}")

    return "", "none"


def extract_addresses_from_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Runs image preprocessing and OCR to extract addresses.
    """
    processed_img = preprocess_image(image_bytes)
    extracted_text, engine_used = run_ocr(processed_img)

    parsed = parse_address_blocks(extracted_text)
    return {
        "success": True,
        "sender": parsed["sender"],
        "customer": parsed["customer"],
        "raw_text": extracted_text,
        "requires_review": True,
        "ocr_engine": engine_used,
    }
