# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ── System dependencies ───────────────────────────────────────────────────────
# poppler-utils  → needed by pdf2image
# libgl1         → needed by opencv
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ───────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────────────────────────────────────
COPY app.py .
COPY pages/ pages/
COPY utils/ utils/
COPY .streamlit/ .streamlit/

# ── Streamlit config ──────────────────────────────────────────────────────────
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# ── Run ───────────────────────────────────────────────────────────────────────
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
