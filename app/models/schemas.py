"""
models/schemas.py
=================
Pydantic models define the shape of data coming IN (requests)
and going OUT (responses).
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional


class SummarizeRequest(BaseModel):
    """Body expected when calling POST /api/summarize."""

    text: str = Field(
        ...,
        min_length=50,
        description="The text to be summarized (minimum 50 characters).",
        examples=["Artificial intelligence (AI) is intelligence demonstrated by machines..."],
    )
    max_length: Optional[int] = Field(default=150, ge=30, le=500)
    min_length: Optional[int] = Field(default=30, ge=10, le=200)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text must not be blank or contain only whitespace.")
        return v.strip()


class SummarizeResponse(BaseModel):
    # Fix Pydantic warning: 'model_used' clashes with protected 'model_' namespace
    model_config = ConfigDict(protected_namespaces=())

    success: bool
    original_length: int
    summary_length: int
    compression_ratio: float
    summary: str
    model_used: str


class UploadResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    success: bool
    filename: str
    file_type: str
    extracted_chars: int
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    model_used: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
