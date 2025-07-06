FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy application code
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY tests/ /app/tests/

# Create necessary directories
RUN mkdir -p /logs

# Default command (can be overridden)
CMD ["python", "-m", "src.main"]
