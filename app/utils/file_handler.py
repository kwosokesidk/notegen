"""
utils/file_handler.py
======================
Handles extraction of raw text from uploaded files.

Supported formats:
  - .txt  → read directly
  - .pdf  → extracted with PyMuPDF (fitz) — free, no API needed
"""

import fitz  # PyMuPDF
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# Maximum file size: 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


async def extract_text_from_file(file: UploadFile) -> tuple[str, str]:
    """
    Reads an uploaded file and returns (extracted_text, file_type).

    Parameters
    ----------
    file : FastAPI UploadFile object

    Returns
    -------
    (text: str, file_type: str)
    """
    filename = file.filename or ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # ------------------------------------------------------------------
    # Validate file type
    # ------------------------------------------------------------------
    if extension not in ("pdf", "txt"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{extension}'. Only PDF and TXT are accepted.",
        )

    # ------------------------------------------------------------------
    # Read raw bytes
    # ------------------------------------------------------------------
    raw_bytes = await file.read()

    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum allowed size is 10 MB.",
        )

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ------------------------------------------------------------------
    # Extract text
    # ------------------------------------------------------------------
    if extension == "txt":
        text = _extract_txt(raw_bytes, filename)
        return text, "text/plain"

    elif extension == "pdf":
        text = _extract_pdf(raw_bytes, filename)
        return text, "application/pdf"

    # Should never reach here due to validation above
    raise HTTPException(status_code=400, detail="Unsupported file type.")


def _extract_txt(raw_bytes: bytes, filename: str) -> str:
    """Decode a TXT file to a Python string."""
    try:
        # Try UTF-8 first, fall back to latin-1
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_bytes.decode("latin-1")

        text = text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="The TXT file appears to be empty.")
        return text

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to read TXT file '{filename}': {exc}")
        raise HTTPException(status_code=500, detail="Failed to read the TXT file.")


def _extract_pdf(raw_bytes: bytes, filename: str) -> str:
    """
    Extract all text from a PDF using PyMuPDF.
    Each page's text is joined with a newline.
    """
    try:
        # Open PDF from bytes (no temp file needed)
        pdf_doc = fitz.open(stream=raw_bytes, filetype="pdf")

        if pdf_doc.page_count == 0:
            raise HTTPException(status_code=400, detail="The PDF has no pages.")

        pages_text = []
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc.load_page(page_num)
            page_text = page.get_text("text")  # plain text extraction
            if page_text.strip():
                pages_text.append(page_text.strip())

        pdf_doc.close()

        full_text = "\n\n".join(pages_text).strip()

        if not full_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No text could be extracted from the PDF. "
                    "It may be a scanned image-only PDF (OCR not supported)."
                ),
            )

        return full_text

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to parse PDF '{filename}': {exc}")
        raise HTTPException(status_code=500, detail="Failed to parse the PDF file.")
