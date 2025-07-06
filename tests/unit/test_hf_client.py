"""
Unit tests for HuggingFaceClient
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from src.hf_client import HuggingFaceClient


class TestHuggingFaceClient:
    """Test HuggingFaceClient functionality"""
    
    @patch.dict(os.environ, {'HF_TOKEN': 'test-token', 'HF_MODEL': 'facebook/bart-large-cnn'})
    def test_client_initialization(self):
        """Test HuggingFaceClient initialization"""
        client = HuggingFaceClient()
        
        assert client.model == 'facebook/bart-large-cnn'
        assert hasattr(client, 'summarizer')  # Should have a summarizer
    
    @patch.dict(os.environ, {}, clear=True)
    def test_client_initialization_no_token(self):
        """Test initialization without HF_TOKEN"""
        with pytest.raises(ValueError, match="HF_TOKEN"):
            HuggingFaceClient()
    
    @patch('requests.post')
    @patch.dict(os.environ, {'HF_TOKEN': 'test-token', 'HF_MODEL': 'facebook/bart-large-cnn'})
    def test_summarize_paper_success(self, mock_post):
        """Test successful paper summarization"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'summary_text': 'This paper presents novel LLM architectures with improved performance.'}
        ]
        mock_post.return_value = mock_response        
        client = HuggingFaceClient()
        paper = {
            'title': 'Test LLM Paper',
            'authors': ['Author One', 'Author Two'],
            'abstract': 'This is a long abstract about large language models...' * 10
        }
        
        result = client.summarize_paper(paper)
        
        assert result is not None
        assert 'summary' in result
        assert 'key_points' in result
        assert 'relevance_score' in result
        assert result['summary'] == 'This paper presents novel LLM architectures with improved performance.'
        assert isinstance(result['key_points'], list)
        assert isinstance(result['relevance_score'], (int, float))
        assert 0 <= result['relevance_score'] <= 10
    
    @patch('requests.post')
    @patch.dict(os.environ, {'HF_TOKEN': 'test-token', 'HF_MODEL': 'facebook/bart-large-cnn'})
    def test_summarize_paper_api_error(self, mock_post):
        """Test handling of API errors"""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = 'Service Unavailable'
        mock_post.return_value = mock_response
        
        client = HuggingFaceClient()
        paper = {'title': 'Test', 'authors': ['Author'], 'abstract': 'Abstract'}
        
        result = client.summarize_paper(paper)
        
        assert result is None  # Should return None on error    
    @patch('requests.post')
    @patch.dict(os.environ, {'HF_TOKEN': 'test-token', 'HF_MODEL': 'facebook/bart-large-cnn'})
    def test_extract_key_points(self, mock_post):
        """Test key points extraction"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'summary_text': 'Summary with multiple points. First finding. Second finding. Final conclusion.'}
        ]
        mock_post.return_value = mock_response
        
        client = HuggingFaceClient()
        paper = {'title': 'Test', 'authors': ['Author'], 'abstract': 'Long abstract' * 50}
        
        result = client.summarize_paper(paper)
        
        assert len(result['key_points']) > 0
        assert all(isinstance(point, str) for point in result['key_points'])
        assert all(len(point) > 0 for point in result['key_points'])
    
    @patch('requests.post')
    @patch.dict(os.environ, {'HF_TOKEN': 'test-token', 'HF_MODEL': 'facebook/bart-large-cnn'})
    def test_relevance_scoring(self, mock_post):
        """Test relevance score calculation"""
        # High relevance paper
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'summary_text': 'Revolutionary LLM transformer language model breakthrough.'}
        ]
        mock_post.return_value = mock_response        
        client = HuggingFaceClient()
        paper = {
            'title': 'LLM Transformer Advances',
            'authors': ['Sam Altman'],
            'abstract': 'Large language model transformer GPT architecture improvements.'
        }
        
        result = client.summarize_paper(paper)
        
        assert result['relevance_score'] >= 7  # Should be high for LLM paper
    
    @patch('requests.post')
    @patch.dict(os.environ, {'HF_TOKEN': 'test-token', 'HF_MODEL': 'facebook/bart-large-cnn'})
    def test_rate_limiting(self, mock_post):
        """Test handling of rate limiting"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'retry-after': '60'}
        mock_post.return_value = mock_response
        
        client = HuggingFaceClient()
        paper = {'title': 'Test', 'authors': ['Author'], 'abstract': 'Abstract'}
        
        result = client.summarize_paper(paper)
        
        assert result is None  # Should handle rate limiting gracefully