#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
import requests

def main():
    print(f"Testing Ollama at {settings.ollama_host}...")
    try:
        response = requests.get(f"{settings.ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running!")
            models = response.json().get('models', [])
            print(f"Available models: {[m['name'] for m in models]}")
        else:
            print("❌ Ollama not responding")
    except:
        print("❌ Cannot connect to Ollama. Run: ollama serve")

if __name__ == "__main__":
    main()
