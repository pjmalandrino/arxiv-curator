"""
Performance tests for batch processing
"""
import pytest
import time
from datetime import date
from concurrent.futures import ThreadPoolExecutor

from src.database import DatabaseManager
from tests.fixtures.factories import PaperFactory, LLMPaperFactory


class TestBatchProcessing:
    """Test batch processing performance"""
    
    def test_bulk_paper_insertion(self, db_manager):
        """Test inserting large number of papers"""
        papers_data = [PaperFactory() for _ in range(100)]
        
        start_time = time.time()
        
        for paper_data in papers_data:
            db_manager.save_paper(paper_data)
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        assert elapsed < 10.0  # 10 seconds for 100 papers
        
        # Verify all saved
        session = db_manager.get_session()
        count = session.query(Paper).count()
        assert count == 100
        session.close()
        
        print(f"Inserted 100 papers in {elapsed:.2f} seconds")
    
    def test_bulk_query_performance(self, db_manager):
        """Test performance of bulk queries"""
        # Insert test data
        papers_data = [LLMPaperFactory() for _ in range(50)]
        for paper_data in papers_data:
            db_manager.save_paper(paper_data)
        
        session = db_manager.get_session()
        
        # Test query performance
        start_time = time.time()
        
        # Complex query with filters
        papers = session.query(Paper).filter(
            Paper.categories.contains(['cs.CL']),
            Paper.published_date >= date(2024, 1, 1)
        ).order_by(Paper.published_date.desc()).all()
        
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # Should be fast
        assert len(papers) == 50
        session.close()
        
        print(f"Complex query completed in {elapsed:.2f} seconds")    
    def test_concurrent_summarization(self, db_manager):
        """Test concurrent paper summarization"""
        from unittest.mock import Mock
        
        # Create mock HF client that simulates delay
        mock_hf = Mock()
        mock_hf.summarize_paper = Mock(side_effect=lambda p: {
            'summary': f"Summary of {p['title']}",
            'key_points': ['Point 1', 'Point 2'],
            'relevance_score': 7.5
        })
        
        # Insert papers
        papers_data = [LLMPaperFactory() for _ in range(20)]
        paper_ids = []
        for paper_data in papers_data:
            paper = db_manager.save_paper(paper_data)
            if paper:
                paper_ids.append(paper.id)
        
        # Summarize concurrently
        start_time = time.time()
        
        def summarize_paper(paper_id):
            session = db_manager.get_session()
            paper = session.query(Paper).get(paper_id)
            if paper:
                result = mock_hf.summarize_paper({
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'authors': paper.authors
                })
                if result:
                    db_manager.save_summary(paper_id, result)
            session.close()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(summarize_paper, paper_ids)
        
        elapsed = time.time() - start_time
        
        # Verify all summaries created
        session = db_manager.get_session()
        summary_count = session.query(Summary).count()
        assert summary_count == 20
        session.close()
        
        print(f"Summarized 20 papers concurrently in {elapsed:.2f} seconds")