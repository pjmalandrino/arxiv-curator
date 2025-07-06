"""
Unit tests for temporal scorer
"""
import pytest
from datetime import date, timedelta

from src.scoring.temporal_scorer import TemporalScorer


class TestTemporalScorer:
    """Test TemporalScorer functionality"""
    
    def test_initialization(self):
        """Test TemporalScorer initialization"""
        scorer = TemporalScorer()
        assert scorer.weight == 1.0
        assert scorer.decay_rate > 0
    
    def test_recent_paper_score(self):
        """Test scoring of recent papers"""
        scorer = TemporalScorer()
        
        # Paper published today
        today_paper = {
            'published_date': date.today(),
            'title': 'Recent Paper',
            'abstract': 'Abstract'
        }
        score_today = scorer.score(today_paper)
        assert score_today >= 9.5  # Should be very high
        
        # Paper published 7 days ago
        week_old_paper = {
            'published_date': date.today() - timedelta(days=7),
            'title': 'Week Old Paper',
            'abstract': 'Abstract'
        }
        score_week = scorer.score(week_old_paper)
        assert 7.0 <= score_week <= 9.0
        
        # Paper published 30 days ago
        month_old_paper = {
            'published_date': date.today() - timedelta(days=30),
            'title': 'Month Old Paper',
            'abstract': 'Abstract'
        }
        score_month = scorer.score(month_old_paper)
        assert 5.0 <= score_month <= 7.0    
    def test_old_paper_score(self):
        """Test scoring of old papers"""
        scorer = TemporalScorer()
        
        # Paper published 6 months ago
        old_paper = {
            'published_date': date.today() - timedelta(days=180),
            'title': 'Old Paper',
            'abstract': 'Abstract'
        }
        score = scorer.score(old_paper)
        assert score <= 3.0  # Should have low score
    
    def test_decay_function(self):
        """Test that scores decay properly over time"""
        scorer = TemporalScorer()
        
        scores = []
        for days in [0, 1, 7, 14, 30, 60, 90]:
            paper = {
                'published_date': date.today() - timedelta(days=days),
                'title': 'Test Paper',
                'abstract': 'Abstract'
            }
            scores.append(scorer.score(paper))
        
        # Scores should monotonically decrease
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]
    
    def test_custom_decay_rate(self):
        """Test scorer with custom decay rate"""
        scorer_fast = TemporalScorer(decay_rate=0.1)  # Fast decay
        scorer_slow = TemporalScorer(decay_rate=0.01)  # Slow decay
        
        paper = {
            'published_date': date.today() - timedelta(days=30),
            'title': 'Test Paper',
            'abstract': 'Abstract'
        }
        
        score_fast = scorer_fast.score(paper)
        score_slow = scorer_slow.score(paper)
        
        assert score_slow > score_fast  # Slow decay should give higher score