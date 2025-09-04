# Backend with Python only (frontend removed)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/tmp/.cache \
    TRANSFORMERS_CACHE=/tmp/.cache \
    SENTENCE_TRANSFORMERS_HOME=/tmp/.cache \
    XDG_CACHE_HOME=/tmp/.cache \
    CHROMA_DB_PATH=/tmp/chroma_db \
    PYTHONPATH=/app \
    NODE_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    unzip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory
WORKDIR /app

# Create cache + db dirs with full permissions (for Hugging Face)
RUN mkdir -p /tmp/.cache /tmp/chroma_db && \
    chmod -R 777 /tmp/.cache /tmp/chroma_db

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy download script
COPY download_db.sh ./download_db.sh
RUN chmod +x download_db.sh

# Hugging Face Spaces require port 7860
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run DB download + backend
CMD ["sh", "-c", "./download_db.sh && uvicorn backend.main:app --host 0.0.0.0 --port 7860 --workers 1"]
