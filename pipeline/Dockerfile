FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/

# Create logs directory
RUN mkdir -p /logs

# Run the pipeline
CMD ["python", "-m", "main"]