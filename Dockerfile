# ==========================================
# STAGE 1: Builder (Compiles dependencies)
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 2: Runner (Lean production image)
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Security: Run as a non-root user (Enterprise Best Practice)
RUN groupadd -r raggroup && useradd -r -g raggroup -s /bin/false raguser

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy application source code
COPY --chown=raguser:raggroup app/ /app/app/

# Switch to non-privileged user
USER raguser

# Expose API port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Start Uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
