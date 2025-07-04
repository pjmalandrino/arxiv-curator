FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY tests/ /app/tests/

# Create necessary directories
RUN mkdir -p /logs

# Default command (can be overridden)
CMD ["python", "-m", "src.main"]
