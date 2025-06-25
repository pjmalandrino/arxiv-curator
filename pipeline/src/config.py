import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    database_url: str = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@postgres:5432/arxiv_curator')
    ollama_host: str = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
    ollama_model: str = os.getenv('OLLAMA_MODEL', 'gemma3:latest')
    arxiv_categories: List[str] = field(default_factory=lambda: ['cs.CL', 'cs.AI', 'cs.LG'])
    arxiv_keywords: List[str] = field(default_factory=lambda: ['LLM', 'language model', 'transformer', 'GPT', 'BERT'])
    arxiv_max_results: int = 10
    batch_size: int = 5
    log_level: str = 'INFO'
