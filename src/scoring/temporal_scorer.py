"""Temporal scoring based on publication date and trends."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import math

from .base import ScoringStrategy, Paper, ScoringResult


class TemporalScorer(ScoringStrategy):
    """Score papers based on temporal factors and trending topics."""
    
    def __init__(
        self, 
        recency_weight: float = 0.5,
        trend_keywords: Optional[Dict[str, float]] = None,
        peak_freshness_days: int = 30
    ):
        """
        Initialize temporal scorer.
        
        Args:
            recency_weight: Weight for recency (0-1)
            trend_keywords: Keywords with trend multipliers
            peak_freshness_days: Days after publication for peak score
        """
        self.recency_weight = recency_weight
        self.trend_keywords = trend_keywords or {}
        self.peak_freshness_days = peak_freshness_days
    
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """Score paper based on temporal factors."""
        # Calculate recency score
        recency_score = self._calculate_recency_score(paper.published_date)
        
        # Calculate trend score
        trend_score = self._calculate_trend_score(paper.title, paper.abstract)
        
        # Day of week bonus (papers published Mon-Wed often get more attention)
        dow_bonus = self._calculate_dow_bonus(paper.published_date)
        
        # Combine scores
        final_score = (
            self.recency_weight * recency_score +
            (1 - self.recency_weight) * trend_score +
            0.1 * dow_bonus  # Small bonus
        )
        
        # Cap at 1.0
        final_score = min(1.0, final_score)
        
        return ScoringResult(
            score=final_score,
            explanation=self._generate_explanation(recency_score, trend_score, dow_bonus),
            components={
                'recency': recency_score,
                'trending': trend_score,
                'publication_timing': dow_bonus
            },
            metadata={
                'days_old': (datetime.now() - paper.published_date).days,
                'trending_matches': self._find_trending_matches(paper.title, paper.abstract)
            }
        )
    
    def _calculate_recency_score(self, published_date: datetime) -> float:
        """Calculate score based on publication recency."""
        days_old = (datetime.now() - published_date).days
        
        if days_old < 0:  # Future date (error)
            return 0.0
        
        # Exponential decay with peak at peak_freshness_days
        if days_old <= self.peak_freshness_days:
            # Ramp up to peak
            return days_old / self.peak_freshness_days
        else:
            # Decay after peak
            decay_rate = 0.1  # Adjust for faster/slower decay
            return math.exp(-decay_rate * (days_old - self.peak_freshness_days) / 30)
    
    def _calculate_trend_score(self, title: str, abstract: str) -> float:
        """Calculate score based on trending topics."""
        if not self.trend_keywords:
            return 0.5  # Neutral if no trends defined
        
        text = (title + ' ' + abstract).lower()
        
        score = 0.0
        max_possible = sum(self.trend_keywords.values())
        
        for keyword, weight in self.trend_keywords.items():
            if keyword.lower() in text:
                # Count occurrences with diminishing returns
                count = text.count(keyword.lower())
                score += weight * (1 - math.exp(-count))
        
        # Normalize to 0-1
        if max_possible > 0:
            score = score / max_possible
        
        return min(1.0, score)
    
    def _calculate_dow_bonus(self, published_date: datetime) -> float:
        """Calculate bonus based on day of week."""
        # Monday = 0, Sunday = 6
        dow = published_date.weekday()
        
        # Papers published early in week often get more visibility
        dow_scores = {
            0: 1.0,   # Monday
            1: 0.9,   # Tuesday
            2: 0.8,   # Wednesday
            3: 0.6,   # Thursday
            4: 0.4,   # Friday
            5: 0.2,   # Saturday
            6: 0.3    # Sunday
        }
        
        return dow_scores.get(dow, 0.5)
    
    def _find_trending_matches(self, title: str, abstract: str) -> List[str]:
        """Find which trending keywords matched."""
        if not self.trend_keywords:
            return []
        
        text = (title + ' ' + abstract).lower()
        matches = []
        
        for keyword in self.trend_keywords:
            if keyword.lower() in text:
                matches.append(keyword)
        
        return matches
    
    def _generate_explanation(self, recency: float, trend: float, dow: float) -> str:
        """Generate explanation for temporal scores."""
        parts = []
        
        if recency > 0.8:
            parts.append("Very recent publication")
        elif recency > 0.5:
            parts.append("Recent publication")
        elif recency < 0.2:
            parts.append("Older publication")
        
        if trend > 0.7:
            parts.append("highly trending topics")
        elif trend > 0.4:
            parts.append("some trending elements")
        
        if dow > 0.8:
            parts.append("optimal publication timing")
        
        return "; ".join(parts) if parts else "Standard temporal scoring"
    
    @property
    def name(self) -> str:
        return "temporal_scorer"
