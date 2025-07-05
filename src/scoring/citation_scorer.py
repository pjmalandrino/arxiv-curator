"""Citation-based scoring using reference analysis."""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import ScoringStrategy, Paper, ScoringResult


class CitationScorer(ScoringStrategy):
    """Score papers based on citation patterns and reference quality."""
    
    def __init__(self, min_citations: int = 5, recent_years: int = 3):
        """
        Initialize citation scorer.
        
        Args:
            min_citations: Minimum expected citations for good score
            recent_years: Years to consider for recency bonus
        """
        self.min_citations = min_citations
        self.recent_years = recent_years
        
        # High-impact venues/conferences
        self.high_impact_venues = {
            'neurips', 'icml', 'iclr', 'cvpr', 'eccv', 'iccv', 'aaai', 'ijcai',
            'acl', 'emnlp', 'naacl', 'nature', 'science', 'pnas', 'cell'
        }
    
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """Score paper based on citation analysis."""
        # Extract citations from abstract (simple heuristic)
        citation_count = self._estimate_citations(paper.abstract)
        
        # Check for high-impact venue mentions
        venue_score = self._calculate_venue_score(paper.abstract, paper.title)
        
        # Self-citation check
        self_citation_ratio = self._estimate_self_citations(paper.abstract, paper.authors)
        
        # Reference quality (looking for arxiv vs published papers)
        ref_quality = self._assess_reference_quality(paper.abstract)
        
        # Calculate final score
        citation_score = min(1.0, citation_count / self.min_citations)
        self_cite_penalty = max(0.0, 1.0 - self_citation_ratio)
        
        final_score = (
            0.4 * citation_score +
            0.3 * venue_score +
            0.2 * ref_quality +
            0.1 * self_cite_penalty
        )
        
        return ScoringResult(
            score=final_score,
            explanation=self._generate_explanation(
                citation_count, venue_score, self_citation_ratio, ref_quality
            ),
            components={
                'citation_density': citation_score,
                'venue_impact': venue_score,
                'reference_quality': ref_quality,
                'self_citation_penalty': self_cite_penalty
            },
            metadata={
                'estimated_citations': citation_count,
                'self_citation_ratio': self_citation_ratio
            }
        )
    
    def _estimate_citations(self, abstract: str) -> int:
        """Estimate citation count from abstract text."""
        # Look for citation patterns like [1], [2,3], etc.
        bracket_citations = re.findall(r'\[\d+(?:,\s*\d+)*\]', abstract)
        
        # Look for author-year patterns like (Smith et al., 2023)
        paren_citations = re.findall(r'\([A-Z][a-z]+ et al\.,? \d{4}\)', abstract)
        
        # Estimate total unique citations
        total = len(bracket_citations) + len(paren_citations)
        
        # Also count "et al." occurrences as indicator
        et_al_count = abstract.count('et al.')
        
        return max(total, et_al_count)
    
    def _calculate_venue_score(self, abstract: str, title: str) -> float:
        """Calculate score based on high-impact venue mentions."""
        text = (abstract + ' ' + title).lower()
        
        mentioned_venues = 0
        for venue in self.high_impact_venues:
            if venue in text:
                mentioned_venues += 1
        
        # Normalize to 0-1
        if mentioned_venues == 0:
            return 0.3  # Base score
        elif mentioned_venues == 1:
            return 0.7
        else:
            return 1.0  # Multiple high-impact venues mentioned
    
    def _estimate_self_citations(self, abstract: str, authors: List[str]) -> float:
        """Estimate ratio of self-citations."""
        if not authors:
            return 0.0
        
        # Extract last names
        last_names = []
        for author in authors:
            parts = author.strip().split()
            if parts:
                last_names.append(parts[-1].lower())
        
        # Count author mentions in abstract
        text = abstract.lower()
        self_mentions = 0
        total_citations = self._estimate_citations(abstract)
        
        for name in last_names:
            self_mentions += text.count(name)
        
        if total_citations == 0:
            return 0.0
        
        # Rough estimate: each self-mention might be a self-citation
        return min(1.0, self_mentions / max(1, total_citations))
    
    def _assess_reference_quality(self, abstract: str) -> float:
        """Assess quality of references mentioned."""
        text = abstract.lower()
        
        # Positive indicators
        published_indicators = ['journal', 'conference', 'proceedings', 'transactions']
        arxiv_count = text.count('arxiv')
        
        published_count = sum(text.count(ind) for ind in published_indicators)
        
        if published_count + arxiv_count == 0:
            return 0.5  # No clear indicators
        
        # Higher score for more published references vs arxiv
        ratio = published_count / (published_count + arxiv_count)
        return ratio
    
    def _generate_explanation(
        self, citations: int, venue_score: float, 
        self_ratio: float, ref_quality: float
    ) -> str:
        """Generate explanation for citation scores."""
        parts = []
        
        if citations >= self.min_citations:
            parts.append(f"Good citation density ({citations} references)")
        else:
            parts.append(f"Low citation density ({citations} references)")
        
        if venue_score > 0.7:
            parts.append("references high-impact venues")
        
        if self_ratio > 0.3:
            parts.append(f"high self-citation ratio ({self_ratio:.1%})")
        
        if ref_quality > 0.7:
            parts.append("high-quality references")
        elif ref_quality < 0.3:
            parts.append("many unpublished references")
        
        return "; ".join(parts) if parts else "Standard citation pattern"
    
    @property
    def name(self) -> str:
        return "citation_scorer"
