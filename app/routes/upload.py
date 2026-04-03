"""
routes/upload.py
=================
Handles POST /api/upload — accepts a PDF or TXT file,
extracts its text, then summarizes it.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.schemas import UploadResponse
from app.utils.file_handler import extract_text_from_file
from app.utils.summarizer import summarize_text
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload & Summarize File",
    description=(
        "Upload a PDF or TXT file. The server extracts the text and "
        "returns an AI-generated summary. Max file size: 10 MB."
    ),
)
async def upload_and_summarize(
    file: UploadFile = File(..., description="A .pdf or .txt file to summarize."),
    max_length: Optional[int] = Form(default=150, ge=30, le=500),
    min_length: Optional[int] = Form(default=30, ge=10, le=200),
):
    """
    **Upload a PDF or TXT file and receive an AI summary.**

    - **file**: The file to upload (.pdf or .txt only, max 10 MB).
    - **max_length**: Upper bound on summary tokens. Default 150.
    - **min_length**: Lower bound on summary tokens. Default 30.
    """
    try:
        logger.info(f"File upload received: '{file.filename}'")

        # Step 1: Extract text from the uploaded file
        extracted_text, file_type = await extract_text_from_file(file)

        logger.info(f"Extracted {len(extracted_text)} characters from '{file.filename}'.")

        # Step 2: Check extracted text is long enough to summarize
        if len(extracted_text.split()) < 30:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short to summarize (need at least 30 words).",
            )

        # Step 3: Summarize the extracted text
        result = summarize_text(
            text=extracted_text,
            max_length=max_length,
            min_length=min_length,
        )

        return UploadResponse(
            success=True,
            filename=file.filename or "unknown",
            file_type=file_type,
            extracted_chars=len(extracted_text),
            **result,
        )

    except HTTPException:
        raise  # Re-raise known HTTP errors as-is

    except Exception as exc:
        logger.exception(f"Unexpected error processing upload: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the file.",
        )
