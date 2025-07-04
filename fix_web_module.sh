#!/bin/bash
# fix_web_module.sh - Fix the web module import path

echo "Fixing web module path..."

# Update Dockerfile.web to use correct module path
cat > docker/Dockerfile.web << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn

# Copy application code
COPY src/ /app/src/

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run web server - Note the correct module path
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

# Make sure the web app exists
mkdir -p src/web
touch src/web/__init__.py

# Create a simple working app if it doesn't exist
if [ ! -f src/web/app.py ]; then
    cat > src/web/app.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="ArXiv Curator")

@app.get("/")
def read_root():
    return {"message": "ArXiv Curator API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
EOF
fi

echo "✅ Fixed module path"
echo ""
echo "Now rebuild and restart:"
echo "  docker-compose build web"
echo "  docker-compose up -d web"