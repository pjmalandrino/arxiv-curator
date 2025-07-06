"""
Integration tests for the complete scoring system
"""
import pytest
from datetime import date, timedelta

from src.scoring.composite_scorer import CompositeScorer
from src.scoring.keyword_scorer import KeywordScorer
from src.scoring.temporal_scorer import TemporalScorer
from src.scoring.author_scorer import AuthorScorer
from tests.fixtures.test_data import TEST_PAPERS, SCORING_TEST_CASES


class TestScoringSystem:
    """Test the integrated scoring system"""
    
    def test_composite_scorer_integration(self):
        """Test composite scorer with multiple components"""
        # Initialize scorers
        keyword_scorer = KeywordScorer(['LLM', 'language model', 'transformer'], weight=2.0)
        temporal_scorer = TemporalScorer(weight=1.0)
        author_scorer = AuthorScorer(['Ilya Sutskever', 'Sam Altman'], weight=1.5)
        
        # Create composite scorer
        composite = CompositeScorer([keyword_scorer, temporal_scorer, author_scorer])
        
        # Test with high-relevance paper
        paper = {
            'title': 'Revolutionary LLM Architecture by GPT Team',
            'abstract': 'We present a new transformer-based language model that achieves SOTA.',
            'authors': ['Sam Altman', 'Other Researcher'],
            'published_date': date.today() - timedelta(days=2)
        }
        
        score = composite.score(paper)
        assert score >= 8.0  # Should have very high score
        
        # Verify individual components
        components = composite.get_component_scores(paper)
        assert 'KeywordScorer' in components
        assert 'TemporalScorer' in components
        assert 'AuthorScorer' in components
        assert components['KeywordScorer'] >= 8.0
        assert components['TemporalScorer'] >= 9.0
        assert components['AuthorScorer'] >= 7.0    
    def test_scoring_with_real_papers(self):
        """Test scoring with realistic paper data"""
        composite = CompositeScorer([
            KeywordScorer(['LLM', 'GPT', 'transformer', 'language model'], weight=2.0),
            TemporalScorer(weight=1.0),
            AuthorScorer(['Ilya Sutskever', 'Sam Altman', 'Yann LeCun'], weight=1.5)
        ])
        
        results = []
        for test_case in SCORING_TEST_CASES:
            paper = test_case['paper']
            score = composite.score(paper)
            results.append({
                'title': paper['title'],
                'score': score,
                'expected_range': (
                    test_case['expected_scores']['composite_score'] - 1.0,
                    test_case['expected_scores']['composite_score'] + 1.0
                )
            })
        
        # Verify scores are in expected ranges
        for result in results:
            assert result['expected_range'][0] <= result['score'] <= result['expected_range'][1]
    
    def test_scorer_weights(self):
        """Test that scorer weights are properly applied"""
        paper = TEST_PAPERS[0]  # High relevance LLM paper
        
        # Equal weights
        scorer_equal = CompositeScorer([
            KeywordScorer(['LLM'], weight=1.0),
            TemporalScorer(weight=1.0)
        ])
        score_equal = scorer_equal.score(paper)        
        # Heavy keyword weight
        scorer_keyword = CompositeScorer([
            KeywordScorer(['LLM'], weight=5.0),
            TemporalScorer(weight=1.0)
        ])
        score_keyword = scorer_keyword.score(paper)
        
        # Heavy temporal weight
        scorer_temporal = CompositeScorer([
            KeywordScorer(['LLM'], weight=1.0),
            TemporalScorer(weight=5.0)
        ])
        score_temporal = scorer_temporal.score(paper)
        
        # Keyword-weighted should be higher for LLM paper
        assert score_keyword > score_equal
        assert score_keyword > score_temporal
    
    def test_empty_scorers(self):
        """Test composite scorer with no components"""
        composite = CompositeScorer([])
        
        paper = TEST_PAPERS[0]
        score = composite.score(paper)
        
        assert score == 5.0  # Default neutral score
    
    def test_scorer_robustness(self):
        """Test scorer handles edge cases"""
        composite = CompositeScorer([
            KeywordScorer(['LLM']),
            TemporalScorer()
        ])
        
        # Paper with minimal data
        minimal_paper = {
            'title': '',
            'abstract': '',
            'authors': [],
            'published_date': date.today()
        }
        
        score = composite.score(minimal_paper)
        assert 0 <= score <= 10  # Should still produce valid score