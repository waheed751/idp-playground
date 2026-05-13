"""
Local document classifier.
Uses RapidOCR to extract text from PDF, then keyword matching to classify.
"""
import os
import tempfile
from pdf2image import convert_from_bytes



def _extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Convert PDF bytes to text using RapidOCR."""
    from rapidocr import RapidOCR

    ocr_engine = RapidOCR()
    pages = convert_from_bytes(pdf_bytes, dpi=200)
    full_text = []

    for page in pages:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
            page.save(tmp_path, "JPEG")

        try:
            out = ocr_engine(tmp_path)
            if out.txts:
                full_text.append(" ".join(out.txts))
        finally:
            os.remove(tmp_path)

    return " ".join(full_text)


def _classify_text(text: str) -> str:
    """Keyword matching — returns classifier label string."""
    text_upper = text.upper()

    pfs_keywords = [
        "PERSONAL FINANCIAL STATEMENT",
        "ASSETS AND LIABILITIES",
        "NET WORTH",
        "SCHEDULE A", "SCHEDULE B", "SCHEDULE C"
    ]
    rent_roll_keywords = [
        "RENT ROLL",
        "OCCUPANT NAME",
        "MONTHLY BASE RENT",
        "ANNUAL RATE PSF",
        "EXPIRATION",
        "OCCUPIED SQFT"
    ]
    coi_keywords = [
        "CERTIFICATEOFLIABILITYINSURANCE",
        "ACORD",
        "COMMERCIALGENERALLIABILITY",
        "CERTIFICATEHOLDER",
        "POLICYNUMBER"
    ]

    scores = {
        "Personal Financial Statement": sum(1 for kw in pfs_keywords if kw in text_upper),
        "Rent Roll": sum(1 for kw in rent_roll_keywords if kw in text_upper),
        "Certificate of Insurance": sum(1 for kw in coi_keywords if kw in text_upper),
    }

    if max(scores.values()) == 0:
        return "Unknown Document"

    return max(scores, key=scores.get)


def validate_doc_type(pdf_bytes: bytes, selected_type: str, classifier_label: str) -> dict:
    """
    Run local OCR + classify on the PDF bytes.
    Returns:
        {
            "detected": "Certificate of Insurance",
            "matches": True/False,
            "error": None or error message
        }
    """
    try:
        text = _extract_text_from_bytes(pdf_bytes)
        detected = _classify_text(text)
        matches = detected == classifier_label
        return {"detected": detected, "matches": matches, "error": None}
    except Exception as e:
        return {"detected": "Unknown", "matches": False, "error": str(e)}
