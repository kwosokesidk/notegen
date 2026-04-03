"""
routes/summarize.py
====================
Handles POST /api/summarize — accepts raw text and returns a summary.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.utils.summarizer import summarize_text
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    summary="Summarize Text",
    description=(
        "Send a block of text and receive an AI-generated summary. "
        "You can control summary length via `max_length` and `min_length`."
    ),
)
async def summarize_endpoint(request: SummarizeRequest):
    """
    **Summarize any text using AI.**

    - **text**: The body of text you want summarized (min 50 chars).
    - **max_length**: Upper bound on summary length (in tokens). Default 150.
    - **min_length**: Lower bound on summary length (in tokens). Default 30.

    Returns a structured response including the summary, word counts,
    and compression ratio.
    """
    try:
        logger.info(f"Summarization request received. Text length: {len(request.text)} chars.")

        result = summarize_text(
            text=request.text,
            max_length=request.max_length,
            min_length=request.min_length,
        )

        return SummarizeResponse(
            success=True,
            **result,
        )

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as exc:
        logger.exception(f"Unexpected error during summarization: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during summarization. Please try again.",
        )
