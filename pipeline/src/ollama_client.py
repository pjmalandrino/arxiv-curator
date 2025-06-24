import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, host: str, model: str):
        self.host = host
        self.model = model
        self.api_url = f"{host}/api/generate"

    def summarize_paper(self, paper: Dict) -> Dict:
        """Génère un résumé structuré d'un papier"""
        prompt = self._build_prompt(paper)

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                }
            )
            response.raise_for_status()

            result = response.json()
            summary_text = result.get('response', '')

            # Parse le résumé structuré
            summary_data = self._parse_summary(summary_text)

            return {
                'summary': summary_data.get('summary', ''),
                'key_points': summary_data.get('key_points', []),
                'relevance_score': summary_data.get('relevance_score', 0.0),
                'model_used': self.model
            }

        except Exception as e:
            logger.error(f"Error summarizing paper {paper.get('title')}: {e}")
            return None

    def _build_prompt(self, paper: Dict) -> str:
        """Construit le prompt pour la génération du résumé"""
        return f"""You are an AI research assistant specializing in Large Language Models (LLMs).
Please analyze this academic paper and provide a structured summary.

Title: {paper['title']}
Authors: {', '.join(paper['authors'])}
Abstract: {paper['abstract']}

Please provide:
1. A concise summary (2-3 sentences) of the main contribution
2. Three key points or findings
3. A relevance score (0-10) for LLM research

Format your response as:
SUMMARY: [your summary here]
KEY_POINTS:
- [point 1]
- [point 2]
- [point 3]
RELEVANCE_SCORE: [score]/10
"""

    def _parse_summary(self, text: str) -> Dict:
        """Parse la réponse structurée du LLM"""
        lines = text.strip().split('\n')
        summary = ""
        key_points = []
        relevance_score = 0.0

        current_section = None

        for line in lines:
            if line.startswith("SUMMARY:"):
                current_section = "summary"
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("KEY_POINTS:"):
                current_section = "key_points"
            elif line.startswith("RELEVANCE_SCORE:"):
                try:
                    score_text = line.replace("RELEVANCE_SCORE:", "").strip()
                    relevance_score = float(score_text.split('/')[0])
                except:
                    relevance_score = 0.0
            elif current_section == "key_points" and line.strip().startswith('-'):
                key_points.append(line.strip()[1:].strip())

        return {
            'summary': summary,
            'key_points': key_points,
            'relevance_score': relevance_score
        }