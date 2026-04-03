"""
NoteGen - AI-Powered Text Summarizer
=====================================
Main application entry point.
FastAPI app is initialized here with all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os

from app.routes import summarize, upload

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="NoteGen - AI Text Summarizer",
    description=(
        "An AI-powered text summarization API built with FastAPI and "
        "Hugging Face Transformers. Accepts raw text or uploaded files "
        "(PDF / TXT) and returns a concise summary."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ---------------------------------------------------------------------------
# CORS Middleware  (allows frontend / Postman to call the API)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static Files & Templates
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ---------------------------------------------------------------------------
# Routers  (each router handles a group of related endpoints)
# ---------------------------------------------------------------------------
app.include_router(summarize.router, prefix="/api", tags=["Summarization"])
app.include_router(upload.router,    prefix="/api", tags=["File Upload"])

# ---------------------------------------------------------------------------
# Root Route  – serves the HTML frontend
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_frontend(request: Request):
    """Serve the NoteGen web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health-check endpoint for deployment monitoring."""
    return {"status": "ok", "service": "NoteGen API", "version": "1.0.0"}
