"""
Integration tests for the complete paper processing pipeline
"""
import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock

from src.main import ArxivCurationPipeline
from src.database import DatabaseManager
from src.arxiv_client import ArxivClient
from src.hf_client import HuggingFaceClient
from src.models import Paper, Summary
from src.config import Config


class TestPaperPipeline:
    """Test the complete paper processing pipeline"""
    
    @patch('src.arxiv_client.arxiv.Search')
    @patch('src.hf_client.requests.post')
    def test_full_pipeline(self, mock_hf_post, mock_arxiv_search, db_manager):
        """Test complete pipeline from fetching to storing"""
        # Mock ArXiv response
        mock_author = Mock()
        mock_author.name = 'Test Author'
        
        mock_paper = Mock()
        mock_paper.entry_id = 'http://arxiv.org/abs/2401.00001v1'
        mock_paper.title = 'Test LLM Paper'
        mock_paper.authors = [mock_author]
        mock_paper.summary = 'This paper about LLM is groundbreaking.'
        mock_paper.published = datetime(2024, 1, 20)
        mock_paper.categories = ['cs.CL', 'cs.AI']
        mock_paper.pdf_url = 'https://arxiv.org/pdf/2401.00001v1.pdf'
        
        mock_search = Mock()
        mock_search.results.return_value = [mock_paper]
        mock_arxiv_search.return_value = mock_search
        
        # Mock HuggingFace response
        mock_hf_response = Mock()
        mock_hf_response.status_code = 200
        mock_hf_response.json.return_value = [
            {'summary_text': 'Groundbreaking LLM research with novel approaches.'}
        ]
        mock_hf_post.return_value = mock_hf_response        
        # Initialize pipeline
        config = Config()
        config.database_url = db_manager.engine.url
        pipeline = ArxivCurationPipeline(config)
        
        # Run pipeline
        pipeline.run(days_back=7)
        
        # Verify paper was saved
        session = db_manager.get_session()
        papers = session.query(Paper).all()
        assert len(papers) == 1
        
        paper = papers[0]
        assert paper.arxiv_id == '2401.00001v1'
        assert paper.title == 'Test LLM Paper'
        assert len(paper.authors) == 1
        
        # Verify summary was saved
        summaries = session.query(Summary).all()
        assert len(summaries) == 1
        
        summary = summaries[0]
        assert summary.paper_id == paper.id
        assert summary.summary == 'Groundbreaking LLM research with novel approaches.'
        assert summary.relevance_score > 0
        assert len(summary.key_points) > 0
        
        session.close()
    
    @patch('src.arxiv_client.arxiv.Search')
    def test_duplicate_paper_handling(self, mock_arxiv_search, db_manager):
        """Test that duplicate papers are not processed twice"""
        # First, manually insert a paper
        session = db_manager.get_session()
        existing_paper = Paper(
            arxiv_id='2401.00001',
            title='Existing Paper',
            authors=['Author'],
            abstract='Abstract',
            published_date=date(2024, 1, 20),
            categories=['cs.CL'],
            pdf_url='https://arxiv.org/pdf/2401.00001.pdf'
        )
        session.add(existing_paper)
        session.commit()
        session.close()        
        # Mock ArXiv to return the same paper
        mock_paper = Mock()
        mock_paper.entry_id = 'http://arxiv.org/abs/2401.00001v1'
        mock_paper.title = 'Existing Paper Updated'  # Different title
        mock_paper.authors = [Mock(name='Author')]
        mock_paper.summary = 'Abstract'
        mock_paper.published = datetime(2024, 1, 20)
        mock_paper.categories = ['cs.CL']
        mock_paper.pdf_url = 'https://arxiv.org/pdf/2401.00001v1.pdf'
        
        mock_search = Mock()
        mock_search.results.return_value = [mock_paper]
        mock_arxiv_search.return_value = mock_search
        
        # Initialize pipeline
        config = Config()
        config.database_url = db_manager.engine.url
        pipeline = ArxivCurationPipeline(config)
        
        # Run pipeline
        pipeline.run(days_back=7)
        
        # Verify only one paper exists
        session = db_manager.get_session()
        papers = session.query(Paper).all()
        assert len(papers) == 1
        assert papers[0].title == 'Existing Paper'  # Should keep original
        session.close()
    
    @patch('src.hf_client.requests.post')
    def test_pipeline_error_handling(self, mock_hf_post, db_manager):
        """Test pipeline handles errors gracefully"""
        # Mock HF to fail
        mock_hf_response = Mock()
        mock_hf_response.status_code = 500
        mock_hf_post.return_value = mock_hf_response
        
        # Create a paper manually
        session = db_manager.get_session()
        paper = Paper(
            arxiv_id='2401.00002',
            title='Test Paper',
            authors=['Author'],
            abstract='Abstract',
            published_date=date(2024, 1, 20),
            categories=['cs.CL'],
            pdf_url='https://arxiv.org/pdf/2401.00002.pdf'
        )
        session.add(paper)
        session.commit()
        paper_id = paper.id
        
        # Initialize pipeline with mocked HF client
        config = Config()
        config.database_url = db_manager.engine.url
        pipeline = ArxivCurationPipeline(config)
        
        # Try to summarize - should handle error gracefully
        summary_data = pipeline.hf_client.summarize_paper({
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract
        })
        
        # Should return None on error
        assert summary_data is None
        
        # Paper should still exist, but no summary
        summaries = session.query(Summary).filter_by(paper_id=paper_id).all()
        assert len(summaries) == 0
        session.close()