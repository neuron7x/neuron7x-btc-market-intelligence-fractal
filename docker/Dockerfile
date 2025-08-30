# syntax=docker/dockerfile:1

FROM python:3.10.13-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install Python dependencies using constraints
COPY requirements.txt constraints.txt ./
RUN pip install --prefix=/usr/local \
    --no-cache-dir -r requirements.txt -c constraints.txt

FROM python:3.10.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local /usr/local

# Copy project files
COPY . /app

# Create non-root user and adjust ownership
RUN addgroup --system appuser \
    && adduser --system --ingroup appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

# Healthcheck for the API endpoint
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys;urllib.request.urlopen('http://localhost:8000/healthz')"]

ENTRYPOINT ["python3", "cli/btcmi.py"]
CMD ["--help"]
