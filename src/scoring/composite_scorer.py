"""Composite scorer that combines multiple scoring strategies."""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
from dataclasses import dataclass

from .base import ScoringStrategy, Paper, ScoringResult


@dataclass
class ScorerWeight:
    """Weight configuration for a scorer."""
    scorer: ScoringStrategy
    weight: float
    required: bool = True  # If False, failures won't break the composite score


class CompositeScorer(ScoringStrategy):
    """Combines multiple scoring strategies with weighted averaging."""
    
    def __init__(self, scorer_weights: List[ScorerWeight]):
        """
        Initialize with weighted scorers.
        
        Args:
            scorer_weights: List of ScorerWeight configurations
        """
        self.scorer_weights = scorer_weights
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1.0."""
        total_weight = sum(sw.weight for sw in self.scorer_weights)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Scorer weights must sum to 1.0, got {total_weight}")
    
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """Score paper using all configured scorers."""
        # Run all scorers concurrently
        scoring_tasks = []
        for scorer_weight in self.scorer_weights:
            task = self._score_with_fallback(
                scorer_weight.scorer, paper, context, scorer_weight.required
            )
            scoring_tasks.append((scorer_weight, task))
        
        # Gather results
        results = []
        for scorer_weight, task in scoring_tasks:
            result = await task
            if result is not None:
                results.append((scorer_weight, result))
        
        # Calculate weighted average
        if not results:
            return ScoringResult(
                score=0.0,
                explanation="No scorers produced valid results",
                components={},
                metadata={"error": "all_scorers_failed"}
            )
        
        # Normalize weights if some scorers failed
        total_weight = sum(sw.weight for sw, _ in results)
        weighted_score = 0.0
        components = {}
        explanations = []
        
        for scorer_weight, result in results:
            normalized_weight = scorer_weight.weight / total_weight
            weighted_score += result.score * normalized_weight
            components[scorer_weight.scorer.name] = {
                "score": result.score,
                "weight": normalized_weight,
                "explanation": result.explanation
            }
            explanations.append(f"{scorer_weight.scorer.name}: {result.explanation}")
        
        return ScoringResult(
            score=weighted_score,
            explanation=f"Composite score from {len(results)} scorers. " + "; ".join(explanations),
            components=components,
            metadata={
                "scorer_count": len(results),
                "total_weight": total_weight
            }
        )
    
    async def _score_with_fallback(
        self, scorer: ScoringStrategy, paper: Paper, 
        context: Optional[Dict[str, Any]], required: bool
    ) -> Optional[ScoringResult]:
        """Score with a single scorer, handling failures."""
        try:
            return await scorer.score(paper, context)
        except Exception as e:
            if required:
                raise
            # Log error but continue for non-required scorers
            print(f"Warning: {scorer.name} failed with error: {e}")
            return None
    
    @property
    def name(self) -> str:
        return "composite_scorer"
