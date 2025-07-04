import os
import requests
from typing import Dict, List, Optional
import logging
import json
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseSummarizer(ABC):
    """Base class for different summarization strategies"""
    
    @abstractmethod
    def summarize(self, paper: Dict) -> Dict:
        pass

class BARTSummarizer(BaseSummarizer):
    """BART-based summarizer for when only BART is available"""
    
    def __init__(self, api_url: str, headers: dict):
        self.api_url = api_url
        self.headers = headers
    
    def summarize(self, paper: Dict) -> Dict:
        # Prepare input text
        input_text = f"Title: {paper['title']}\n\nAuthors: {', '.join(paper['authors'])}\n\nAbstract: {paper['abstract']}"
        
        # Truncate if too long
        if len(input_text) > 1024:
            input_text = input_text[:1024]
        
        summary = self._get_summary(input_text)
        if not summary:
            return None
        
        key_points = self._extract_key_points(paper['abstract'])
        relevance_score = self._estimate_relevance_score(paper)
        
        return {
            'summary': summary,
            'key_points': key_points,
            'relevance_score': relevance_score
        }
    
    def _get_summary(self, text: str, max_retries: int = 3) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                payload = {
                    "inputs": text,
                    "parameters": {
                        "max_length": 150,
                        "min_length": 50,
                        "do_sample": False
                    }
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 503:
                    wait_time = 20 * (attempt + 1)
                    logger.warning(f"Model is loading. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary = result[0].get('summary_text', '')
                else:
                    summary = result.get('summary_text', '')
                
                return summary.strip() if summary else None
                
            except Exception as e:
                logger.error(f"Error getting summary: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
        
        return None
    
    def _extract_key_points(self, abstract: str) -> List[str]:
        sentences = abstract.split('. ')
        key_points = []
        
        for i, sentence in enumerate(sentences[:3]):
            if sentence.strip():
                key_points.append(sentence.strip() + ('.' if not sentence.endswith('.') else ''))
        
        return key_points
    
    def _estimate_relevance_score(self, paper: Dict) -> float:
        llm_keywords = [
            'language model', 'llm', 'transformer', 'gpt', 'bert', 
            'attention', 'pre-train', 'fine-tun', 'prompt', 'instruction',
            'in-context', 'few-shot', 'zero-shot', 'emergence', 'scaling'
        ]
        
        text = f"{paper['title']} {paper['abstract']}".lower()
        matches = sum(1 for keyword in llm_keywords if keyword in text)
        score = min(10, (matches / len(llm_keywords)) * 20)
        
        return round(score, 1)

class InstructionSummarizer(BaseSummarizer):
    """Instruction-based summarizer for models like Mistral, Llama, etc."""
    
    def __init__(self, api_url: str, headers: dict, model_name: str):
        self.api_url = api_url
        self.headers = headers
        self.model_name = model_name
    
    def summarize(self, paper: Dict) -> Dict:
        prompt = self._build_prompt(paper)
        
        # Format based on model type
        if "instruct" in self.model_name.lower() or "chat" in self.model_name.lower():
            formatted_input = f"<s>[INST] {prompt} [/INST]"
        else:
            formatted_input = prompt
        
        response_text = self._get_completion(formatted_input)
        if not response_text:
            return None
        
        # Parse structured response
        summary_data = self._parse_response(response_text)
        
        return {
            'summary': summary_data.get('summary', ''),
            'key_points': summary_data.get('key_points', []),
            'relevance_score': summary_data.get('relevance_score', 0.0)
        }
    
    def _build_prompt(self, paper: Dict) -> str:
        return f"""You are an AI research assistant. Analyze this paper and provide a structured summary.

Title: {paper['title']}
Authors: {', '.join(paper['authors'])}
Abstract: {paper['abstract']}

Provide:
1. A concise summary (2-3 sentences)
2. Three key points
3. A relevance score (0-10) for LLM research

Format:
SUMMARY: [summary]
KEY_POINTS:
- [point 1]
- [point 2]
- [point 3]
RELEVANCE_SCORE: [score]/10"""
    
    def _get_completion(self, text: str) -> Optional[str]:
        # Implementation would be similar to BART but for text generation
        pass
    
    def _parse_response(self, text: str) -> Dict:
        # Parse structured response
        pass

class HuggingFaceClient:
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or os.getenv('HF_MODEL', 'facebook/bart-large-cnn')
        self.api_key = api_key or os.getenv('HF_TOKEN')
        
        if not self.api_key:
            raise ValueError("HuggingFace API key not found. Set HF_TOKEN environment variable.")
        
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Select appropriate summarizer based on model
        if "bart" in self.model.lower():
            self.summarizer = BARTSummarizer(self.api_url, self.headers)
        else:
            # For future instruction-following models
            self.summarizer = BARTSummarizer(self.api_url, self.headers)  # Fallback to BART for now

    def summarize_paper(self, paper: Dict) -> Dict:
        """Génère un résumé structuré d'un papier"""
        try:
            result = self.summarizer.summarize(paper)
            if result:
                result['model_used'] = self.model
            return result
        except Exception as e:
            logger.error(f"Error summarizing paper {paper.get('title')}: {e}")
            return None
