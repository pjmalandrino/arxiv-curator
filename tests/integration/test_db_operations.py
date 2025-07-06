"""
Integration tests for database operations
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError

from src.database import DatabaseManager
from src.models import Paper, Summary
from tests.fixtures.test_data import TEST_PAPERS, TEST_SUMMARIES


class TestDatabaseOperations:
    """Test database operations with real database"""
    
    def test_batch_insert_papers(self, db_manager):
        """Test inserting multiple papers efficiently"""
        papers_data = TEST_PAPERS[:3]
        
        saved_papers = []
        for paper_data in papers_data:
            paper = db_manager.save_paper(paper_data)
            if paper:
                saved_papers.append(paper)
        
        assert len(saved_papers) == 3
        
        # Verify all papers are in database
        session = db_manager.get_session()
        db_papers = session.query(Paper).all()
        assert len(db_papers) == 3
        
        # Verify data integrity
        arxiv_ids = [p.arxiv_id for p in db_papers]
        assert '2401.00001' in arxiv_ids
        assert '2401.00002' in arxiv_ids
        assert '2401.00003' in arxiv_ids
        session.close()
    
    def test_transaction_rollback(self, db_manager):
        """Test transaction rollback on error"""
        session = db_manager.get_session()
        
        try:
            # Start transaction
            paper1 = Paper(**TEST_PAPERS[0])
            session.add(paper1)
            
            # This should fail (duplicate arxiv_id)
            paper2 = Paper(**TEST_PAPERS[0])
            session.add(paper2)
            
            session.commit()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()
        
        # Verify no papers were saved
        session = db_manager.get_session()
        count = session.query(Paper).count()
        assert count == 0
        session.close()    
    def test_complex_queries(self, db_manager):
        """Test complex database queries"""
        # Insert test data
        for paper_data in TEST_PAPERS:
            db_manager.save_paper(paper_data)
        
        session = db_manager.get_session()
        
        # Query papers with summaries
        papers_with_summaries = session.query(Paper).join(Summary).all()
        assert len(papers_with_summaries) == 0  # No summaries yet
        
        # Add summaries
        papers = session.query(Paper).all()
        for paper in papers[:2]:
            summary_data = TEST_SUMMARIES.get(paper.arxiv_id, {
                'summary': 'Test summary',
                'key_points': ['Point 1'],
                'relevance_score': 5.0,
                'model_used': 'test-model'
            })
            db_manager.save_summary(paper.id, summary_data)
        
        # Query again
        papers_with_summaries = session.query(Paper).join(Summary).all()
        assert len(papers_with_summaries) == 2
        
        # Query papers by date range
        recent_date = date.today() - timedelta(days=10)
        recent_papers = session.query(Paper).filter(
            Paper.published_date >= recent_date
        ).all()
        assert len(recent_papers) == 3  # All test papers are recent
        
        session.close()    
    def test_concurrent_access(self, db_manager):
        """Test handling concurrent database access"""
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        def save_paper(paper_data):
            return db_manager.save_paper(paper_data)
        
        # Create multiple papers with unique IDs
        papers_data = []
        for i in range(10):
            paper = TEST_PAPERS[0].copy()
            paper['arxiv_id'] = f'2401.{i:05d}'
            paper['title'] = f'Concurrent Paper {i}'
            papers_data.append(paper)
        
        # Save papers concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(save_paper, papers_data))
        
        # All should succeed
        assert all(r is not None for r in results)
        
        # Verify all papers saved
        session = db_manager.get_session()
        count = session.query(Paper).count()
        assert count == 10
        session.close()
    
    def test_database_constraints(self, db_manager):
        """Test database constraints are properly enforced"""
        session = db_manager.get_session()
        
        # Test NOT NULL constraints
        with pytest.raises(IntegrityError):
            paper = Paper(arxiv_id='2401.99999')  # Missing required fields
            session.add(paper)
            session.commit()
        
        session.rollback()
        session.close()