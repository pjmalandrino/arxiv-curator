"""
Performance tests for memory usage
"""
import pytest
import psutil
import os
from memory_profiler import memory_usage

from src.database import DatabaseManager
from src.arxiv_client import ArxivClient
from tests.fixtures.factories import PaperFactory


class TestMemoryUsage:
    """Test memory usage patterns"""
    
    def test_memory_leak_detection(self, db_manager):
        """Test for memory leaks in database operations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for i in range(10):
            # Create and save papers
            papers_data = [PaperFactory() for _ in range(100)]
            for paper_data in papers_data:
                db_manager.save_paper(paper_data)
            
            # Query and discard
            session = db_manager.get_session()
            papers = session.query(Paper).all()
            session.close()
            
            # Force garbage collection
            import gc
            gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB")
        print(f"Increase: {memory_increase:.1f}MB")
        
        # Should not have excessive memory growth
        assert memory_increase < 100  # Less than 100MB increase    
    def test_large_result_set_handling(self, db_manager):
        """Test memory usage with large result sets"""
        # Insert many papers
        for _ in range(1000):
            db_manager.save_paper(PaperFactory())
        
        def process_papers():
            session = db_manager.get_session()
            # Use query iteration instead of loading all at once
            for paper in session.query(Paper).yield_per(100):
                # Process paper
                _ = paper.title
            session.close()
        
        # Measure memory usage during processing
        mem_usage = memory_usage(process_papers)
        max_memory = max(mem_usage)
        
        print(f"Max memory usage during processing: {max_memory:.1f}MB")
        
        # Should use reasonable memory even with 1000 papers
        assert max_memory < 200  # Less than 200MB
    
    def test_session_cleanup(self, db_manager):
        """Test that database sessions are properly cleaned up"""
        import gc
        from sqlalchemy import inspect
        
        # Track session count
        initial_sessions = len(gc.get_objects())
        
        # Create and close many sessions
        for _ in range(100):
            session = db_manager.get_session()
            # Do some work
            session.query(Paper).first()
            session.close()
        
        # Force garbage collection
        gc.collect()
        
        final_sessions = len(gc.get_objects())
        
        # Should not accumulate sessions
        session_increase = final_sessions - initial_sessions
        assert session_increase < 10  # Minimal object accumulation