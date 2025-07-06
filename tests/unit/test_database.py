"""
Unit tests for DatabaseManager
"""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from src.database import DatabaseManager
from src.models import Paper, Summary


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    def test_db_manager_initialization(self, test_db):
        """Test DatabaseManager initialization"""
        db_manager = DatabaseManager(test_db)
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None
    
    def test_get_session(self, db_manager):
        """Test getting a database session"""
        session = db_manager.get_session()
        assert session is not None
        
        # Test session works
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
        
        session.close()
    
    def test_save_paper(self, db_manager, sample_paper_data):
        """Test saving a paper through DatabaseManager"""
        paper = db_manager.save_paper(sample_paper_data)
        
        assert paper.id is not None
        assert paper.arxiv_id == sample_paper_data['arxiv_id']
        
        # Verify it's in the database
        session = db_manager.get_session()
        db_paper = session.query(Paper).filter_by(arxiv_id=sample_paper_data['arxiv_id']).first()
        assert db_paper is not None
        assert db_paper.title == sample_paper_data['title']
        session.close()    
    def test_save_duplicate_paper(self, db_manager, sample_paper_data):
        """Test that saving duplicate paper returns existing paper"""
        # Save first paper
        paper1 = db_manager.save_paper(sample_paper_data)
        assert paper1 is not None
        
        # Try to save duplicate
        paper2 = db_manager.save_paper(sample_paper_data)
        assert paper2 is not None  # Should return existing paper
        assert paper2.id == paper1.id  # Should be the same paper
    
    def test_get_paper_by_arxiv_id(self, db_manager, sample_paper_data):
        """Test retrieving paper by arxiv_id"""
        # Save paper first
        saved_paper = db_manager.save_paper(sample_paper_data)
        
        # Retrieve it
        paper = db_manager.get_paper_by_arxiv_id(sample_paper_data['arxiv_id'])
        assert paper is not None
        assert paper.id == saved_paper.id
        assert paper.title == sample_paper_data['title']
        
        # Test non-existent paper
        non_existent = db_manager.get_paper_by_arxiv_id('9999.99999')
        assert non_existent is None
    
    def test_save_summary(self, db_manager, sample_paper_data, sample_summary_data):
        """Test saving a summary"""
        # First save a paper
        paper = db_manager.save_paper(sample_paper_data)
        
        # Save summary
        summary = db_manager.save_summary(paper.id, sample_summary_data)
        assert summary is not None
        
        # Verify in database
        session = db_manager.get_session()
        db_summary = session.query(Summary).filter_by(paper_id=paper.id).first()
        assert db_summary is not None
        assert db_summary.summary == sample_summary_data['summary']
        session.close()    
    @pytest.mark.skip(reason="ARRAY operations not supported in SQLite")
    def test_get_recent_papers(self, db_manager):
        """Test retrieving recent papers"""
        # Create papers with different dates
        papers_data = [
            {
                'arxiv_id': '2401.00001',
                'title': 'Recent Paper 1',
                'authors': ['Author A'],
                'abstract': 'Abstract 1',
                'published_date': date(2024, 1, 20),
                'categories': ['cs.CL'],
                'pdf_url': 'https://arxiv.org/pdf/2401.00001.pdf'
            },
            {
                'arxiv_id': '2401.00002',
                'title': 'Recent Paper 2',
                'authors': ['Author B'],
                'abstract': 'Abstract 2',
                'published_date': date(2024, 1, 15),
                'categories': ['cs.AI'],
                'pdf_url': 'https://arxiv.org/pdf/2401.00002.pdf'
            },
            {
                'arxiv_id': '2023.99999',
                'title': 'Old Paper',
                'authors': ['Author C'],
                'abstract': 'Abstract 3',
                'published_date': date(2023, 12, 1),
                'categories': ['cs.LG'],
                'pdf_url': 'https://arxiv.org/pdf/2023.99999.pdf'
            }
        ]        
        # Save all papers in this test
        saved_papers = []
        for paper_data in papers_data:
            paper = db_manager.save_paper(paper_data)
            if paper:
                saved_papers.append(paper)
        
        assert len(saved_papers) == 3  # All papers should be saved
        
        # Get recent papers (last 30 days)
        recent_papers = db_manager.get_recent_papers(days=30)
        assert len(recent_papers) >= 2  # Should get the two 2024 papers
        
        # Check ordering (most recent first)
        if len(recent_papers) >= 2:
            assert recent_papers[0].published_date >= recent_papers[1].published_date
    
    @pytest.mark.skip(reason="ARRAY operations not supported in SQLite")
    def test_get_papers_by_category(self, db_manager):
        """Test retrieving papers by category"""
        # Create papers with different categories
        papers_data = [
            {
                'arxiv_id': '2401.10001',
                'title': 'NLP Paper',
                'authors': ['Author X'],
                'abstract': 'NLP research',
                'published_date': date(2024, 1, 20),
                'categories': ['cs.CL', 'cs.AI'],
                'pdf_url': 'https://arxiv.org/pdf/2401.10001.pdf'
            },
            {
                'arxiv_id': '2401.10002',
                'title': 'CV Paper',
                'authors': ['Author Y'],
                'abstract': 'Computer vision research',
                'published_date': date(2024, 1, 19),
                'categories': ['cs.CV', 'cs.LG'],
                'pdf_url': 'https://arxiv.org/pdf/2401.10002.pdf'
            }
        ]        
        # Save papers in this test
        saved_papers = []
        for paper_data in papers_data:
            paper = db_manager.save_paper(paper_data)
            if paper:
                saved_papers.append(paper)
        
        assert len(saved_papers) == 2  # Both papers should be saved
        
        # Get papers by category
        cl_papers = db_manager.get_papers_by_category('cs.CL')
        assert len(cl_papers) >= 1
        assert any(p.arxiv_id == '2401.10001' for p in cl_papers)
        
        cv_papers = db_manager.get_papers_by_category('cs.CV')
        assert len(cv_papers) >= 1
        assert any(p.arxiv_id == '2401.10002' for p in cv_papers)