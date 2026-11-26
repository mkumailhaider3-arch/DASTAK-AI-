import re
from pathlib import Path
import numpy as np
from app.ml.quality.assessor import load_image_for_cv

try:
    from rapidocr_onnxruntime import RapidOCR
except Exception:  # pragma: no cover
    RapidOCR = None


_OCR_INSTANCE = None


def get_ocr_engine():
    global _OCR_INSTANCE
    if RapidOCR is None:
        return None
    if _OCR_INSTANCE is None:
        _OCR_INSTANCE = RapidOCR()
    return _OCR_INSTANCE


def get_ocr_engine_name() -> str:
    return "rapidocr-onnxruntime" if RapidOCR is not None else "unavailable"


def extract_text_from_document(file_path: Path, mime_type: str) -> dict:
    """Run real OCR on an image or rendered PDF page 1 and return text + line metadata."""
    engine = get_ocr_engine()
    if engine is None:
        return {
            "ocr_text": "",
            "lines": [],
            "ocr_error": "OCR engine (rapidocr-onnxruntime) is not available in this environment.",
            "ocr_engine": "unavailable",
        }

    try:
        bgr = load_image_for_cv(file_path, mime_type)
        # RapidOCR accepts numpy BGR/RGB arrays
        result, _ = engine(bgr)
        lines = []
        text_parts = []
        if result:
            for item in result:
                # item format: [box, text, confidence]
                box, text, conf = item[0], str(item[1]), float(item[2])
                text_parts.append(text)
                lines.append({"text": text, "confidence": round(conf, 4), "box": box})
        return {
            "ocr_text": "\n".join(text_parts),
            "lines": lines,
            "ocr_error": None,
            "ocr_engine": "rapidocr-onnxruntime",
        }
    except Exception as exc:
        return {
            "ocr_text": "",
            "lines": [],
            "ocr_error": f"OCR processing failed: {type(exc).__name__}",
            "ocr_engine": "rapidocr-onnxruntime",
        }


DEFAULT_FIELDS = ["full_name", "date_of_birth", "id_number", "document_date"]


def extract_fields_from_ocr(ocr_text: str, lines: list[dict] | None = None) -> list[dict]:
    """Parse a small configurable set of fields using rules/regex as a baseline.

    Does not assume every document has the same layout. Marks uncertain fields as 'Needs review'.
    """
    lines = lines or []
    line_conf_map = {str(item.get("text", "")).strip(): float(item.get("confidence", 0.0)) for item in lines}

    def find_confidence(matched_text: str) -> float | None:
        if not matched_text:
            return None
        for line_txt, conf in line_conf_map.items():
            if matched_text.lower() in line_txt.lower():
                return conf
        return None

    results: list[dict] = []

    # 1. Full Name
    name_val = ""
    name_match = re.search(
        r"(?:full\s*name|applicant\s*name|student\s*name|name)\s*[:\-]\s*([A-Za-z][A-Za-z\s\.\-]{2,50})",
        ocr_text,
        flags=re.IGNORECASE,
    )
    if name_match:
        name_val = name_match.group(1).strip().splitlines()[0].strip()

    # 2. Date of Birth
    dob_val = ""
    dob_match = re.search(
        r"(?:date\s*of\s*birth|d\.?o\.?b\.?|birth\s*date)\s*[:\-]?\s*(\d{2,4}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
        ocr_text,
        flags=re.IGNORECASE,
    )
    if dob_match:
        dob_val = dob_match.group(1).strip()

    # 3. Document / ID Number (supports synthetic IDs like ID-12345, PASS-9988, 00000-0000000-0)
    id_val = ""
    id_match = re.search(
        r"(?:id\s*(?:no|number)|passport\s*(?:no|number)|reg(?:istration)?\s*(?:no|number)|roll\s*(?:no|number)|ref(?:erence)?\s*(?:no|id))\s*[:\-]?\s*([A-Z0-9\-]{5,25})",
        ocr_text,
        flags=re.IGNORECASE,
    )
    if id_match:
        id_val = id_match.group(1).strip()

    # 4. Issue / Document Date
    doc_date_val = ""
    doc_date_match = re.search(
        r"(?:issue\s*date|issued\s*on|date\s*of\s*issue|document\s*date|date)\s*[:\-]?\s*(\d{2,4}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
        ocr_text,
        flags=re.IGNORECASE,
    )
    if doc_date_match:
        doc_date_val = doc_date_match.group(1).strip()

    extracted_map = {
        "full_name": name_val,
        "date_of_birth": dob_val,
        "id_number": id_val,
        "document_date": doc_date_val,
    }

    for field_name in DEFAULT_FIELDS:
        val = extracted_map.get(field_name, "")
        if not val:
            results.append(
                {
                    "field_name": field_name,
                    "value": "",
                    "confidence": None,
                    "status": "not_detected",
                }
            )
        else:
            conf = find_confidence(val)
            status = "Needs review" if (conf is not None and conf < 0.80) or len(val) < 3 else "extracted"
            results.append(
                {
                    "field_name": field_name,
                    "value": val,
                    "confidence": round(conf, 4) if conf is not None else None,
                    "status": status,
                }
            )

    return results
