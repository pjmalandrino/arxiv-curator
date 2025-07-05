"""Keyword-based scoring using TF-IDF and semantic matching."""

import re
from typing import Dict, Any, Optional, List, Set
from collections import Counter
import math

from .base import ScoringStrategy, Paper, ScoringResult


class KeywordScorer(ScoringStrategy):
    """Score papers based on keyword relevance and semantic matching."""
    
    def __init__(self, keywords: Optional[List[str]] = None, boost_terms: Optional[Dict[str, float]] = None):
        """
        Initialize keyword scorer.
        
        Args:
            keywords: List of relevant keywords/phrases
            boost_terms: Dictionary of terms with boost multipliers
        """
        self.keywords = [k.lower() for k in (keywords or [])]
        self.boost_terms = {k.lower(): v for k, v in (boost_terms or {}).items()}
        
        # Common stop words to ignore
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that'
        }
    
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """Score paper based on keyword matching."""
        # Combine title and abstract for analysis
        text = f"{paper.title} {paper.abstract}".lower()
        
        # Extract terms from context if provided
        context_keywords = []
        if context and 'keywords' in context:
            context_keywords = [k.lower() for k in context['keywords']]
        
        all_keywords = self.keywords + context_keywords
        
        if not all_keywords:
            return ScoringResult(
                score=0.5,
                explanation="No keywords configured for matching",
                components={},
                metadata={'warning': 'no_keywords'}
            )
        
        # Calculate scores
        keyword_score = self._calculate_keyword_score(text, all_keywords)
        boost_score = self._calculate_boost_score(text)
        category_score = self._calculate_category_score(paper.categories, all_keywords)
        
        # Weighted combination
        final_score = (0.5 * keyword_score + 0.3 * boost_score + 0.2 * category_score)
        
        return ScoringResult(
            score=min(1.0, final_score),  # Cap at 1.0
            explanation=self._generate_explanation(keyword_score, boost_score, category_score),
            components={
                'keyword_match': keyword_score,
                'boost_terms': boost_score,
                'category_relevance': category_score
            },
            metadata={'matched_keywords': self._find_matched_keywords(text, all_keywords)}
        )
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate score based on keyword matches."""
        if not keywords:
            return 0.0
        
        # Count exact and partial matches
        exact_matches = 0
        partial_matches = 0
        
        for keyword in keywords:
            # Exact word match
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                exact_matches += 1
            # Partial match
            elif keyword in text:
                partial_matches += 1
        
        # Calculate score (exact matches worth more)
        total_keywords = len(keywords)
        score = (exact_matches + 0.5 * partial_matches) / total_keywords
        
        return min(1.0, score)
    
    def _calculate_boost_score(self, text: str) -> float:
        """Calculate score based on boost terms."""
        if not self.boost_terms:
            return 0.5  # Neutral score if no boost terms
        
        score = 0.0
        for term, boost in self.boost_terms.items():
            if term in text:
                # Count occurrences
                count = text.count(term)
                # Logarithmic scaling to prevent over-boosting
                score += boost * math.log(1 + count)
        
        # Normalize to 0-1 range
        max_possible = sum(abs(b) for b in self.boost_terms.values())
        if max_possible > 0:
            score = (score + max_possible) / (2 * max_possible)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_category_score(self, categories: List[str], keywords: List[str]) -> float:
        """Score based on category-keyword overlap."""
        if not categories or not keywords:
            return 0.5
        
        # Extract meaningful terms from categories
        category_terms = []
        for cat in categories:
            # Split on dots and extract terms
            parts = cat.lower().split('.')
            category_terms.extend(parts)
        
        # Check overlap with keywords
        matches = 0
        for keyword in keywords:
            for term in category_terms:
                if keyword in term or term in keyword:
                    matches += 1
                    break
        
        return min(1.0, matches / len(keywords))
    
    def _find_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords matched in the text."""
        matched = []
        for keyword in keywords:
            if keyword in text:
                matched.append(keyword)
        return matched
    
    def _generate_explanation(self, keyword_score: float, boost_score: float, category_score: float) -> str:
        """Generate explanation for the scores."""
        parts = []
        
        if keyword_score > 0.7:
            parts.append("Strong keyword relevance")
        elif keyword_score > 0.3:
            parts.append("Moderate keyword relevance")
        else:
            parts.append("Low keyword relevance")
        
        if boost_score > 0.7:
            parts.append("contains important boost terms")
        
        if category_score > 0.5:
            parts.append("relevant categories")
        
        return "; ".join(parts) if parts else "Limited keyword matching"
    
    @property
    def name(self) -> str:
        return "keyword_scorer"
