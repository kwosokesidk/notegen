# NoteGen — AI-Powered Text Summarizer

> A production-ready, beginner-friendly AI summarization API built with **FastAPI** and **Hugging Face Transformers**.
> Runs entirely on CPU — no GPU required. Completely free.

---

## Project Overview

NoteGen is a web application + REST API that takes long text (or uploaded files) and returns a concise AI-generated summary.

| Feature | Details |
|---|---|
| AI Model | `sshleifer/distilbart-cnn-12-6` (Hugging Face) |
| Framework | FastAPI (Python) |
| File Support | PDF (PyMuPDF) and TXT |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Docs | Swagger UI at `/docs`, ReDoc at `/redoc` |
| Deployment | Render / Railway / Hugging Face Spaces (all free) |

---

## Folder Structure

```
NoteGen/
│
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, middleware, routes
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic request/response models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── summarize.py        # POST /api/summarize
│   │   └── upload.py           # POST /api/upload
│   │
│   └── utils/
│       ├── __init__.py
│       ├── summarizer.py       # AI model logic (singleton pipeline)
│       └── file_handler.py     # PDF/TXT extraction
│
├── templates/
│   └── index.html              # Frontend web interface
│
├── static/                     # Static assets (CSS/JS if separated)
│
├── run.py                      # Start the server locally
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment (Render/Railway)
├── runtime.txt                 # Python version for deployment
├── .gitignore
└── README.md                   # This file
```

---

## Setup Instructions (Step by Step)

### Prerequisites

- Python 3.9 or higher → Download from https://python.org
- pip (comes with Python)
- ~2 GB free disk space (for the AI model download, one-time only)
- ~2 GB RAM minimum (4 GB recommended)

---

### Step 1 — Clone or Download the Project

```bash
# If using git:
git clone https://github.com/yourusername/notegen.git
cd notegen

# Or just download the ZIP and extract it, then open a terminal in the folder.
```

### Step 2 — Create a Virtual Environment

A virtual environment keeps project dependencies separate from your system Python.

```bash
# Create venv
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# You should see (venv) at the start of your terminal prompt.
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ This may take 5–10 minutes on first run. It installs PyTorch (CPU version), transformers, FastAPI, and PyMuPDF.

### Step 4 — Run the Server

```bash
python run.py
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Loading summarization model: sshleifer/distilbart-cnn-12-6 ...
INFO:     Model loaded successfully.
```

> ⚠️ The **first request** will download the AI model (~1.2 GB). This is a one-time download cached locally.

### Step 5 — Open in Browser

| URL | What you'll see |
|---|---|
| http://localhost:8000 | Web interface |
| http://localhost:8000/docs | Interactive Swagger API docs |
| http://localhost:8000/redoc | Beautiful ReDoc documentation |
| http://localhost:8000/health | Health check JSON |

---

## API Reference

### POST /api/summarize

Summarize plain text.

**Request Body (JSON):**
```json
{
  "text": "Your long text goes here (minimum 50 characters)...",
  "max_length": 150,
  "min_length": 30
}
```

**Response:**
```json
{
  "success": true,
  "original_length": 342,
  "summary_length": 48,
  "compression_ratio": 7.13,
  "summary": "The AI-generated summary will appear here.",
  "model_used": "sshleifer/distilbart-cnn-12-6"
}
```

---

### POST /api/upload

Upload a PDF or TXT file and receive a summary.

**Form Data:**
- `file` — The PDF or TXT file (multipart/form-data)
- `max_length` — (optional) Max tokens, default 150
- `min_length` — (optional) Min tokens, default 30

**Response:**
```json
{
  "success": true,
  "filename": "research_paper.pdf",
  "file_type": "application/pdf",
  "extracted_chars": 15420,
  "original_length": 2803,
  "summary_length": 61,
  "compression_ratio": 45.95,
  "summary": "Summary of the PDF content...",
  "model_used": "sshleifer/distilbart-cnn-12-6"
}
```

---

### GET /health

Health check endpoint.

```json
{
  "status": "ok",
  "service": "NoteGen API",
  "version": "1.0.0"
}
```

---

## Example API Requests

### Using curl

**Summarize text:**
```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence had previously been used to describe machines that mimic and display human cognitive skills associated with the human mind, such as learning and problem-solving.",
    "max_length": 100,
    "min_length": 20
  }'
```

**Upload a file:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/your/document.pdf" \
  -F "max_length=150" \
  -F "min_length=30"
```

**Health check:**
```bash
curl http://localhost:8000/health
```

---

### Using Postman

1. Open Postman and create a new request
2. **For text summarization:**
   - Method: `POST`
   - URL: `http://localhost:8000/api/summarize`
   - Body: Select `raw` → `JSON`
   - Paste the JSON body from above

3. **For file upload:**
   - Method: `POST`
   - URL: `http://localhost:8000/api/upload`
   - Body: Select `form-data`
   - Add key `file` → change type to `File` → select your file
   - Add key `max_length` → value `150`

---

### Using Python (requests library)

```python
import requests

# Summarize text
response = requests.post(
    "http://localhost:8000/api/summarize",
    json={
        "text": "Your long text here...",
        "max_length": 150,
        "min_length": 30,
    }
)
print(response.json())

# Upload file
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/upload",
        files={"file": ("document.pdf", f, "application/pdf")},
        data={"max_length": 150, "min_length": 30},
    )
print(response.json())
```

---

## Deployment Guide

### Option 1: Deploy on Render (Recommended — Free)

1. Push your project to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/notegen.git
   git push -u origin main
   ```

2. Go to https://render.com and sign up (free)

3. Click **"New"** → **"Web Service"**

4. Connect your GitHub repo

5. Fill in:
   - **Name:** notegen
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. Choose **"Free"** plan and click **Deploy**

7. Your app will be live at: `https://notegen.onrender.com`

> ⚠️ Free Render instances sleep after 15 minutes of inactivity. The first request after sleep may take 30–60 seconds to wake up.

---

### Option 2: Deploy on Railway (Free Tier)

1. Go to https://railway.app and sign up

2. Click **"New Project"** → **"Deploy from GitHub Repo"**

3. Select your repository

4. Railway auto-detects the Procfile and deploys

5. Get your live URL from the dashboard

---

### Option 3: Hugging Face Spaces (Free)

1. Go to https://huggingface.co/spaces
2. Create a new Space → choose **FastAPI** as the SDK
3. Upload your project files
4. HF Spaces runs the app at `https://huggingface.co/spaces/yourusername/notegen`

---

## Viva Preparation — How the Summarization Works

### Question: What model does NoteGen use and why?

**Answer:** NoteGen uses `sshleifer/distilbart-cnn-12-6`, a distilled version of Facebook's BART model fine-tuned on the CNN/DailyMail news summarization dataset. It was chosen because:
- It is free and open-source on Hugging Face
- It runs on CPU without needing a GPU
- It produces high-quality abstractive summaries
- It is smaller than the full BART model (~1.2 GB vs 1.6 GB)

---

### Question: What is the difference between extractive and abstractive summarization?

**Answer:**
- **Extractive:** Picks important sentences directly from the original text. Simple, but the summary sounds robotic.
- **Abstractive:** Generates entirely new sentences that capture the meaning, like a human would summarize. NoteGen uses this approach via BART.

---

### Question: How does NoteGen handle very long texts?

**Answer:** BART has a maximum input limit of ~1024 tokens (~750 words). For longer texts, NoteGen:
1. Splits the text into 400-word chunks
2. Summarizes each chunk independently
3. Joins the chunk summaries together
4. If the combined summaries are still too long, runs one final summarization pass

This is called the **"Chunk → Summarize → Merge → Re-summarize"** pattern.

---

### Question: What is FastAPI and why was it chosen?

**Answer:** FastAPI is a modern Python web framework for building APIs. It was chosen because:
- Automatically generates Swagger UI (`/docs`) — no extra work
- Uses Python type hints for automatic validation via Pydantic
- Async support makes it very fast
- Extremely easy for beginners but production-grade

---

### Question: What is Pydantic and what does it do?

**Answer:** Pydantic is a data validation library. In NoteGen, it:
- Validates that request fields have correct types (e.g., `text` is a string, `max_length` is an integer)
- Enforces constraints (e.g., text must be ≥ 50 chars, max_length must be 30–500)
- Automatically produces clear error messages if validation fails
- Defines the exact shape of API responses

---

### Question: How does PDF text extraction work?

**Answer:** NoteGen uses **PyMuPDF** (imported as `fitz`). When a PDF is uploaded:
1. The raw bytes are passed directly to `fitz.open()` (no temp file needed)
2. PyMuPDF iterates through each page
3. `page.get_text("text")` extracts plain text from each page
4. All pages are joined with newlines
5. The full text is then passed to the AI summarizer

---

### Question: What are the limitations of NoteGen?

**Answer:**
1. Scanned PDFs (image-only) cannot be read — they require OCR, which is not implemented
2. The model runs on CPU, so summarizing very long documents (10,000+ words) may take 1–2 minutes
3. The model works best with English text
4. Free Render deployment sleeps after inactivity

---

## Future Improvements

1. **OCR Support** — Use `pytesseract` or `easyocr` to handle scanned PDF images
2. **Multiple Languages** — Switch to a multilingual model like `mbart-large-cc25`
3. **User Accounts** — Add authentication (JWT tokens) so users can save their summaries
4. **Summary History** — Store summaries in a SQLite or PostgreSQL database
5. **Bullet-Point Mode** — Use a different prompt/model to return summaries as bullet points
6. **Keyword Extraction** — Add a YAKE or KeyBERT endpoint to extract keywords alongside the summary
7. **Docker Support** — Package the app in a Docker container for easy, consistent deployment
8. **GPU Support** — Change `device=-1` to `device=0` in `summarizer.py` for GPU acceleration
9. **Rate Limiting** — Add `slowapi` to prevent API abuse
10. **Better Model** — Upgrade to `facebook/bart-large-cnn` for higher quality summaries when hardware allows

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again inside your venv |
| First request is slow | Normal — model is downloading/loading (~1 min). Subsequent requests are faster. |
| Out of memory error | Close other apps. NoteGen needs ~2 GB RAM. |
| PDF shows "no text extracted" | The PDF is likely a scanned image. OCR not supported in v1. |
| Port already in use | Change port in `run.py`: `port=8001` |

---

*Built with ❤️ using FastAPI + Hugging Face Transformers*
