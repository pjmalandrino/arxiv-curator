"""Author-based scoring using reputation and collaboration patterns."""

from typing import Dict, Any, Optional, List, Set
from collections import Counter

from .base import ScoringStrategy, Paper, ScoringResult


class AuthorScorer(ScoringStrategy):
    """Score papers based on author reputation and collaboration."""
    
    def __init__(
        self,
        known_authors: Optional[Dict[str, float]] = None,
        institution_scores: Optional[Dict[str, float]] = None,
        collaboration_bonus: float = 0.1
    ):
        """
        Initialize author scorer.
        
        Args:
            known_authors: Dict mapping author names to reputation scores
            institution_scores: Dict mapping institutions to scores
            collaboration_bonus: Bonus for multi-institution collaboration
        """
        self.known_authors = known_authors or {}
        self.institution_scores = institution_scores or {}
        self.collaboration_bonus = collaboration_bonus
        
        # Common prestigious institutions (fallback)
        self.default_institutions = {
            'mit': 0.9, 'stanford': 0.9, 'berkeley': 0.9, 'cmu': 0.9,
            'oxford': 0.9, 'cambridge': 0.9, 'eth': 0.9, 'epfl': 0.85,
            'google': 0.85, 'deepmind': 0.9, 'openai': 0.9, 'microsoft': 0.8,
            'facebook': 0.8, 'meta': 0.8, 'amazon': 0.8, 'apple': 0.8
        }
    
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """Score paper based on author analysis."""
        # Author reputation score
        author_score = self._calculate_author_score(paper.authors)
        
        # Team size score (optimal team size is 3-5)
        team_score = self._calculate_team_score(len(paper.authors))
        
        # Collaboration diversity
        collab_score = self._estimate_collaboration_score(paper.authors)
        
        # Institution quality (if extractable)
        inst_score = self._estimate_institution_score(paper.authors, paper.abstract)
        
        # Combine scores
        final_score = (
            0.4 * author_score +
            0.2 * team_score +
            0.2 * collab_score +
            0.2 * inst_score
        )
        
        return ScoringResult(
            score=final_score,
            explanation=self._generate_explanation(
                author_score, team_score, collab_score, inst_score, len(paper.authors)
            ),
            components={
                'author_reputation': author_score,
                'team_composition': team_score,
                'collaboration_diversity': collab_score,
                'institutional_quality': inst_score
            },
            metadata={
                'team_size': len(paper.authors),
                'known_authors': self._find_known_authors(paper.authors)
            }
        )
    
    def _calculate_author_score(self, authors: List[str]) -> float:
        """Calculate score based on known author reputation."""
        if not authors:
            return 0.0
        
        scores = []
        for author in authors:
            # Check exact match first
            if author in self.known_authors:
                scores.append(self.known_authors[author])
            else:
                # Check partial match (last name)
                last_name = author.split()[-1] if author.split() else ""
                found = False
                for known_author, score in self.known_authors.items():
                    if last_name and last_name in known_author:
                        scores.append(score * 0.8)  # Partial match penalty
                        found = True
                        break
                if not found:
                    scores.append(0.5)  # Unknown author default
        
        # Return average of top 3 authors (if available)
        top_scores = sorted(scores, reverse=True)[:3]
        return sum(top_scores) / len(top_scores) if top_scores else 0.5
    
    def _calculate_team_score(self, team_size: int) -> float:
        """Calculate score based on team size."""
        if team_size == 0:
            return 0.0
        elif team_size == 1:
            return 0.6  # Single author papers can be good but often less reviewed
        elif 2 <= team_size <= 5:
            return 1.0  # Optimal team size
        elif 6 <= team_size <= 10:
            return 0.8  # Large team
        else:
            return 0.6  # Very large team (might indicate less individual contribution)
    
    def _estimate_collaboration_score(self, authors: List[str]) -> float:
        """Estimate collaboration diversity from author names."""
        if len(authors) < 2:
            return 0.5  # No collaboration
        
        # Simple heuristic: look for different naming patterns
        # (suggesting different cultural backgrounds)
        patterns = set()
        for author in authors:
            if ',' in author:  # "Last, First" format
                patterns.add('western')
            elif len(author.split()) == 1:  # Single name
                patterns.add('single')
            elif any(char.isdigit() for char in author):  # Contains numbers
                patterns.add('numbered')
            else:
                # Check for common patterns
                parts = author.split()
                if len(parts) >= 2 and len(parts[-1]) <= 3:
                    patterns.add('abbreviated')
                else:
                    patterns.add('standard')
        
        # More patterns suggest more diverse collaboration
        diversity_score = len(patterns) / 3.0  # Normalize to 0-1
        
        return min(1.0, diversity_score + self.collaboration_bonus)
    
    def _estimate_institution_score(self, authors: List[str], abstract: str) -> float:
        """Estimate institutional quality from text."""
        text = abstract.lower()
        
        # Combine default and custom institution scores
        all_institutions = {**self.default_institutions, **self.institution_scores}
        
        found_scores = []
        for inst, score in all_institutions.items():
            if inst.lower() in text:
                found_scores.append(score)
        
        if found_scores:
            # Return the highest institution score found
            return max(found_scores)
        
        # Check for university mentions
        if any(term in text for term in ['university', 'institute', 'laboratory', 'lab']):
            return 0.7  # Generic academic institution
        
        return 0.5  # No institution info found
    
    def _find_known_authors(self, authors: List[str]) -> List[str]:
        """Find which authors are in the known list."""
        known = []
        for author in authors:
            if author in self.known_authors:
                known.append(author)
        return known
    
    def _generate_explanation(
        self, author_score: float, team_score: float, 
        collab_score: float, inst_score: float, team_size: int
    ) -> str:
        """Generate explanation for author scores."""
        parts = []
        
        if author_score > 0.8:
            parts.append("High-reputation authors")
        elif author_score > 0.6:
            parts.append("Recognized authors")
        
        if team_score >= 1.0:
            parts.append(f"optimal team size ({team_size})")
        elif team_size == 1:
            parts.append("single author")
        elif team_size > 10:
            parts.append(f"very large team ({team_size})")
        
        if collab_score > 0.8:
            parts.append("diverse collaboration")
        
        if inst_score > 0.8:
            parts.append("prestigious institution(s)")
        
        return "; ".join(parts) if parts else "Standard author profile"
    
    @property
    def name(self) -> str:
        return "author_scorer"
