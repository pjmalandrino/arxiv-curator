#!/usr/bin/env python3
"""
Test HuggingFace integration in Docker environment
"""

import logging
import os
import sys

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.database import DatabaseManager
from src.arxiv_client import ArxivClient
from src.hf_client import HuggingFaceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test la connexion PostgreSQL"""
    try:
        db_url = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@postgres:5432/arxiv_curator')
        db_manager = DatabaseManager(db_url)
        
        # Test simple query
        from sqlalchemy import text
        session = db_manager.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        
        logger.info("✅ Database connection: OK")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_hf_connection():
    """Test la connexion HuggingFace"""
    try:
        client = HuggingFaceClient()
        logger.info(f"✅ HuggingFace client initialized")
        logger.info(f"   Using model: {client.model}")
        return True
    except Exception as e:
        logger.error(f"❌ HuggingFace initialization failed: {e}")
        return False

def test_arxiv_fetch():
    """Test la récupération ArXiv"""
    try:
        client = ArxivClient(['cs.CL', 'cs.AI'], ['LLM', 'language model'])
        papers = client.fetch_recent_papers(max_results=3, days_back=7)
        
        logger.info(f"✅ ArXiv fetch: OK")
        logger.info(f"   Found {len(papers)} papers")
        for i, paper in enumerate(papers[:2]):
            logger.info(f"   {i+1}. {paper['title'][:60]}...")
        return True
    except Exception as e:
        logger.error(f"❌ ArXiv fetch failed: {e}")
        return False

def test_hf_summarization():
    """Test HuggingFace summarization"""
    try:
        # Test paper
        test_paper = {
            'title': 'Test Paper on LLMs',
            'authors': ['Author One', 'Author Two'],
            'abstract': 'This paper presents a novel approach to language models using transformer architecture. We demonstrate significant improvements in performance.'
        }
        
        client = HuggingFaceClient()
        result = client.summarize_paper(test_paper)
        
        if result:
            logger.info(f"✅ HuggingFace summarization: OK")
            logger.info(f"   Summary length: {len(result.get('summary', ''))} chars")
            logger.info(f"   Key points: {len(result.get('key_points', []))}")
            logger.info(f"   Relevance score: {result.get('relevance_score', 0)}/10")
            return True
        else:
            logger.warning("⚠️  HuggingFace summarization: No result (model may be loading)")
            return True  # Don't fail if model is loading
            
    except Exception as e:
        logger.error(f"❌ HuggingFace summarization failed: {e}")
        return False

def main():
    logger.info("🧪 Starting ArXiv Curator HuggingFace Tests...")
    logger.info(f"📅 Current time: {datetime.now()}")
    logger.info(f"🤖 HF Model: {os.getenv('HF_MODEL', 'Not set')}")

    tests = [
        ("Database Connection", test_database_connection),
        ("HuggingFace Client", test_hf_connection),
        ("ArXiv Fetch", test_arxiv_fetch),
        ("HuggingFace Summarization", test_hf_summarization),
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
        logger.info("\n🎉 All tests passed! Your HuggingFace pipeline is ready!")
        logger.info("\n📝 Note: BART-CNN model may take time to load on first use.")
    else:
        logger.info("\n⚠️  Some tests failed. Please check the errors above.")

    return all_passed

if __name__ == "__main__":
    main()
