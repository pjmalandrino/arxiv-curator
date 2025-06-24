#!/usr/bin/env python3
"""
Test minimal pour vérifier que tout fonctionne
Place ce fichier dans pipeline/src/test_pipeline.py
"""

import logging
import os
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test la connexion PostgreSQL"""
    try:
        from sqlalchemy import create_engine, text
        db_url = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@postgres:5432/arxiv_curator')
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection: OK")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_ollama_connection():
    """Test la connexion Ollama"""
    try:
        ollama_host = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
        response = requests.get(f"{ollama_host}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            logger.info(f"✅ Ollama connection: OK")
            logger.info(f"   Available models: {[m['name'] for m in models]}")
            return True
        else:
            logger.error(f"❌ Ollama connection failed: Status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Ollama connection failed: {e}")
        return False

def test_arxiv_fetch():
    """Test la récupération ArXiv"""
    try:
        import arxiv
        search = arxiv.Search(
            query="LLM language model",
            max_results=3,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = list(search.results())
        logger.info(f"✅ ArXiv fetch: OK")
        logger.info(f"   Found {len(papers)} papers")
        for i, paper in enumerate(papers[:2]):
            logger.info(f"   {i+1}. {paper.title[:60]}...")
        return True
    except Exception as e:
        logger.error(f"❌ ArXiv fetch failed: {e}")
        return False

def test_ollama_generation():
    """Test la génération avec Ollama"""
    try:
        ollama_host = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
        model = os.getenv('OLLAMA_MODEL', 'gemma2:9b')

        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": model,
                "prompt": "In one sentence, what is a Large Language Model?",
                "stream": False
            }
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Ollama generation: OK")
            logger.info(f"   Response: {result.get('response', '')[:100]}...")
            return True
        else:
            logger.error(f"❌ Ollama generation failed: Status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Ollama generation failed: {e}")
        return False

def main():
    logger.info("🧪 Starting ArXiv Curator Pipeline Tests...")
    logger.info(f"📅 Current time: {datetime.now()}")

    tests = [
        ("Database Connection", test_database_connection),
        ("Ollama Connection", test_ollama_connection),
        ("ArXiv Fetch", test_arxiv_fetch),
        ("Ollama Generation", test_ollama_generation),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing: {test_name}")
        success = test_func()
        results.append((test_name, success))

    logger.info("\n" + "="*50)
    logger.info("📊 Test Summary:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")

    all_passed = all(success for _, success in results)
    if all_passed:
        logger.info("\n🎉 All tests passed! Your pipeline is ready to go!")
    else:
        logger.info("\n⚠️  Some tests failed. Please check the errors above.")

    return all_passed

if __name__ == "__main__":
    main()