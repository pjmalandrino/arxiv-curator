"""
Unit tests for keyword scorer
"""
import pytest
from datetime import date, datetime

from src.scoring.keyword_scorer import KeywordScorer
from src.scoring.base import Paper


class TestKeywordScorer:
    """Test KeywordScorer functionality"""
    
    def test_initialization(self):
        """Test KeywordScorer initialization"""
        keywords = ['LLM', 'transformer', 'GPT']
        scorer = KeywordScorer(keywords)
        
        # Keywords should be lowercased
        assert scorer.keywords == ['llm', 'transformer', 'gpt']
    
    def test_initialization_with_boost_terms(self):
        """Test initialization with boost terms"""
        keywords = ['LLM']
        boost_terms = {'GPT': 2.0, 'transformer': 1.5}
        scorer = KeywordScorer(keywords, boost_terms)
        assert scorer.boost_terms == {'gpt': 2.0, 'transformer': 1.5}
    
    @pytest.mark.asyncio
    async def test_score_with_keywords(self):
        """Test scoring papers with keywords"""
        scorer = KeywordScorer(['LLM', 'language model', 'transformer'])
        
        # High relevance paper
        paper1 = Paper(
            arxiv_id='2401.00001',
            title='Advanced LLM with Transformer Architecture',
            abstract='This paper presents a new language model using transformers.',
            authors=['Author A'],
            categories=['cs.CL'],
            published_date=datetime.now(),
            pdf_url='https://arxiv.org/pdf/2401.00001.pdf'
        )
        result1 = await scorer.score(paper1)
        assert result1.score >= 0.8  # Should have high score
        
        # Medium relevance paper
        paper2 = {
            'title': 'Machine Learning Applications',
            'abstract': 'We discuss various ML applications including language models.',
            'authors': ['Author B']
        }
        score2 = scorer.score(paper2)
        assert 4.0 <= score2 <= 7.0  # Should have medium score        
        # Low relevance paper
        paper3 = {
            'title': 'Computer Vision for Robotics',
            'abstract': 'This paper focuses on vision systems for robotic applications.',
            'authors': ['Author C']
        }
        score3 = scorer.score(paper3)
        assert score3 <= 3.0  # Should have low score
    
    def test_case_insensitive_matching(self):
        """Test that keyword matching is case-insensitive"""
        scorer = KeywordScorer(['LLM', 'GPT'])
        
        paper = {
            'title': 'Understanding llm and gpt models',
            'abstract': 'A study of LLMs and GPTs in various forms.',
            'authors': ['Author']
        }
        
        score = scorer.score(paper)
        assert score >= 7.0  # Should match despite case differences
    
    def test_empty_keywords(self):
        """Test scorer with no keywords"""
        scorer = KeywordScorer([])
        
        paper = {
            'title': 'Any Paper Title',
            'abstract': 'Any abstract content',
            'authors': ['Author']
        }
        
        score = scorer.score(paper)
        assert score == 5.0  # Default neutral score
    
    def test_author_bonus(self):
        """Test bonus points for known authors"""
        scorer = KeywordScorer(['LLM'])
        
        paper = {
            'title': 'LLM Research',
            'abstract': 'Abstract about LLMs',
            'authors': ['Ilya Sutskever', 'Other Author']  # Known author
        }
        
        score = scorer.score(paper)
        assert score >= 9.0  # Should get bonus for known author