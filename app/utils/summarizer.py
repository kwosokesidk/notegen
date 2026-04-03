"""
utils/summarizer.py
====================
Core AI summarization logic.

Model choice: facebook/bart-large-cnn
  - Pre-trained specifically for summarization tasks
  - Runs on CPU (no GPU required)
  - Free via Hugging Face pipeline
  - Produces high-quality summaries

The model is loaded ONCE at startup (singleton pattern) to avoid
reloading it on every request, which would be very slow.
"""

from transformers import pipeline, Pipeline
from typing import Optional
import logging
import textwrap

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------
# facebook/bart-large-cnn  → best quality, ~1.6 GB download (one-time)
# sshleifer/distilbart-cnn-12-6 → smaller/faster, ~1.2 GB  (recommended for low RAM)
# We default to distilbart for speed; change MODEL_NAME for better quality.

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# ---------------------------------------------------------------------------
# Singleton: load once, reuse forever
# ---------------------------------------------------------------------------
_summarizer: Optional[Pipeline] = None


def get_summarizer() -> Pipeline:
    """
    Returns the HuggingFace summarization pipeline.
    Loads the model only on the first call (lazy singleton).
    """
    global _summarizer
    if _summarizer is None:
        logger.info(f"Loading summarization model: {MODEL_NAME} ...")
        _summarizer = pipeline(
            "summarization",
            model=MODEL_NAME,
            # device=-1 forces CPU execution (no GPU needed)
            device=-1,
        )
        logger.info("Model loaded successfully.")
    return _summarizer


# ---------------------------------------------------------------------------
# Text Chunking  (BART has a ~1024 token limit)
# ---------------------------------------------------------------------------

def chunk_text(text: str, max_chunk_words: int = 400) -> list[str]:
    """
    Splits long text into chunks so the model can process it.
    BART/DistilBART can handle roughly 400–500 words per chunk safely.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_words):
        chunk = " ".join(words[i : i + max_chunk_words])
        chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# Main Summarization Function
# ---------------------------------------------------------------------------

def summarize_text(
    text: str,
    max_length: int = 150,
    min_length: int = 30,
) -> dict:
    """
    Summarizes the given text using the loaded AI model.

    Parameters
    ----------
    text       : The input text to summarize.
    max_length : Max tokens in the output summary.
    min_length : Min tokens in the output summary.

    Returns
    -------
    dict with keys: summary, original_length, summary_length,
                    compression_ratio, model_used
    """
    summarizer = get_summarizer()

    original_word_count = len(text.split())

    # If the text is short enough, summarize directly
    if original_word_count <= 400:
        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
        )
        summary = result[0]["summary_text"].strip()
    else:
        # Long text: chunk → summarize each chunk → join → summarize again
        chunks = chunk_text(text, max_chunk_words=400)
        logger.info(f"Text split into {len(chunks)} chunks for processing.")

        chunk_summaries = []
        for idx, chunk in enumerate(chunks):
            logger.info(f"Summarizing chunk {idx + 1}/{len(chunks)} ...")
            chunk_result = summarizer(
                chunk,
                max_length=max_length,
                min_length=min(min_length, 20),
                do_sample=False,
            )
            chunk_summaries.append(chunk_result[0]["summary_text"].strip())

        # Combine chunk summaries and do a final summarization pass
        combined = " ".join(chunk_summaries)

        if len(combined.split()) > 400:
            # Still too long: do one more summarization pass
            final_result = summarizer(
                combined,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
            )
            summary = final_result[0]["summary_text"].strip()
        else:
            summary = combined

    summary_word_count = len(summary.split())
    compression_ratio = round(original_word_count / max(summary_word_count, 1), 2)

    return {
        "summary": summary,
        "original_length": original_word_count,
        "summary_length": summary_word_count,
        "compression_ratio": compression_ratio,
        "model_used": MODEL_NAME,
    }
