import os
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    database_url: str = os.getenv('DATABASE_URL', 'postgresql://curator:password@localhost:5432/arxiv_curator')
    ollama_host: str = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    ollama_model: str = os.getenv('OLLAMA_MODEL', 'gemma2:9b')
    arxiv_categories: List[str] = ['cs.CL', 'cs.AI', 'cs.LG']
    arxiv_keywords: List[str] = ['LLM', 'language model', 'transformer', 'GPT', 'BERT']
    arxiv_max_results: int = 50
    batch_size: int = 10
    log_level: str = 'INFO'
