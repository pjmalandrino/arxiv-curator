"""
End-to-end tests for the web interface
"""
import pytest
import json
from flask import url_for
from datetime import date
from unittest.mock import Mock, patch

from src.web_app import create_app
from src.models import Paper, Summary
from tests.fixtures.test_data import TEST_PAPERS, TEST_SUMMARIES


class TestWebInterface:
    """Test Flask web application endpoints"""
    
    @pytest.fixture
    def app(self, db_manager):
        """Create Flask app for testing"""
        app = create_app(db_manager)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create Flask test client"""
        return app.test_client()
    
    def test_home_page(self, client):
        """Test home page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ArXiv Curator' in response.data
    
    def test_papers_list_empty(self, client):
        """Test papers list when database is empty"""
        response = client.get('/papers')
        assert response.status_code == 200
        assert b'No papers found' in response.data or b'[]' in response.data
    
    def test_papers_list_with_data(self, client, db_manager):
        """Test papers list with data"""
        # Add test papers
        for paper_data in TEST_PAPERS[:2]:
            db_manager.save_paper(paper_data)
        
        response = client.get('/papers')
        assert response.status_code == 200
        assert b'2401.00001' in response.data
        assert b'2401.00002' in response.data    
    def test_paper_detail(self, client, db_manager):
        """Test individual paper detail page"""
        # Add a paper with summary
        paper = db_manager.save_paper(TEST_PAPERS[0])
        summary_data = TEST_SUMMARIES['2401.00001']
        db_manager.save_summary(paper.id, summary_data)
        
        response = client.get(f'/paper/{paper.id}')
        assert response.status_code == 200
        assert TEST_PAPERS[0]['title'].encode() in response.data
        assert b'Summary' in response.data
        assert summary_data['summary'].encode() in response.data
    
    def test_api_papers_endpoint(self, client, db_manager):
        """Test API endpoint for papers"""
        # Add test data
        for paper_data in TEST_PAPERS:
            db_manager.save_paper(paper_data)
        
        response = client.get('/api/papers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'papers' in data
        assert len(data['papers']) == 3
        assert data['papers'][0]['arxiv_id'] in ['2401.00001', '2401.00002', '2401.00003']
    
    def test_api_papers_with_filters(self, client, db_manager):
        """Test API with category and date filters"""
        # Add papers
        for paper_data in TEST_PAPERS:
            db_manager.save_paper(paper_data)
        
        # Filter by category
        response = client.get('/api/papers?category=cs.CV')
        data = json.loads(response.data)
        assert len(data['papers']) >= 1
        assert any('cs.CV' in p['categories'] for p in data['papers'])    
    def test_search_functionality(self, client, db_manager):
        """Test search functionality"""
        # Add papers
        for paper_data in TEST_PAPERS:
            db_manager.save_paper(paper_data)
        
        # Search for LLM
        response = client.get('/search?q=LLM')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should find papers with LLM in title/abstract
        assert len(data['results']) >= 1
        assert any('LLM' in p['title'] or 'LLM' in p['abstract'] 
                  for p in data['results'])
    
    def test_refresh_papers_endpoint(self, client):
        """Test manual paper refresh endpoint"""
        response = client.post('/refresh')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_error_handling(self, client):
        """Test error handling for invalid requests"""
        # Non-existent paper
        response = client.get('/paper/invalid-uuid')
        assert response.status_code == 404
        
        # Invalid API endpoint
        response = client.get('/api/invalid')
        assert response.status_code == 404