"""LLM-based scoring using Ollama or other LLM providers."""

import os
import json
from typing import Dict, Any, Optional
import aiohttp

from .base import ScoringStrategy, Paper, ScoringResult


class LLMScorer(ScoringStrategy):
    """Score papers using LLM analysis."""
    
    def __init__(self, ollama_host: Optional[str] = None, model: Optional[str] = None):
        self.ollama_host = ollama_host or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'gemma3:4b')
    
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """Score paper using LLM analysis."""
        prompt = self._build_prompt(paper, context)
        
        try:
            score_data = await self._query_ollama(prompt)
            return self._parse_response(score_data)
        except Exception as e:
            # Fallback scoring based on basic heuristics
            return self._fallback_score(paper, str(e))
    
    def _build_prompt(self, paper: Paper, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt for LLM scoring."""
        research_interests = ""
        if context and 'research_interests' in context:
            interests = context['research_interests']
            research_interests = f"\nResearch Interests: {', '.join(interests)}"
        
        prompt = f"""Analyze this research paper and provide a relevance score.

Title: {paper.title}
Abstract: {paper.abstract}
Categories: {', '.join(paper.categories)}
Authors: {', '.join(paper.authors[:5])}  # Show first 5 authors
{research_interests}

Provide a JSON response with:
1. relevance_score: 0.0 to 1.0 based on novelty, impact, and quality
2. novelty_score: 0.0 to 1.0 for how novel/groundbreaking the work is
3. technical_quality: 0.0 to 1.0 for technical rigor and clarity
4. potential_impact: 0.0 to 1.0 for potential research/industry impact
5. explanation: Brief explanation of the scores

Response format:
{{
    "relevance_score": 0.0-1.0,
    "novelty_score": 0.0-1.0,
    "technical_quality": 0.0-1.0,
    "potential_impact": 0.0-1.0,
    "explanation": "explanation text"
}}"""
        return prompt
    
    async def _query_ollama(self, prompt: str) -> Dict[str, Any]:
        """Query Ollama for scoring."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            async with session.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.loads(data.get('response', '{}'))
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    def _parse_response(self, response: Dict[str, Any]) -> ScoringResult:
        """Parse LLM response into ScoringResult."""
        score = response.get('relevance_score', 0.5)
        explanation = response.get('explanation', 'No explanation provided')
        
        components = {
            'novelty': response.get('novelty_score', 0.5),
            'technical_quality': response.get('technical_quality', 0.5),
            'potential_impact': response.get('potential_impact', 0.5)
        }
        
        return ScoringResult(
            score=max(0.0, min(1.0, score)),  # Ensure 0-1 range
            explanation=explanation,
            components=components,
            metadata={'model': self.model}
        )
    
    def _fallback_score(self, paper: Paper, error: str) -> ScoringResult:
        """Simple fallback scoring when LLM fails."""
        # Basic heuristic based on abstract length and category count
        abstract_score = min(1.0, len(paper.abstract) / 1000)
        category_score = min(1.0, len(paper.categories) / 3)
        score = (abstract_score + category_score) / 2
        
        return ScoringResult(
            score=score,
            explanation=f"Fallback scoring due to LLM error: {error}",
            components={'abstract_length': abstract_score, 'categories': category_score},
            metadata={'fallback': True, 'error': error}
        )
    
    @property
    def name(self) -> str:
        return "llm_scorer"
