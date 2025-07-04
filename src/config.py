import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    database_url: str = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@postgres:5432/arxiv_curator')
    
    # HuggingFace settings
    hf_token: str = os.getenv('HF_TOKEN', '')
    hf_model: str = os.getenv('HF_MODEL', 'deepseek-ai/DeepSeek-R1')
    
    # ArXiv settings
    arxiv_categories: List[str] = field(default_factory=lambda: ['cs.CL', 'cs.AI', 'cs.LG'])
    arxiv_keywords: List[str] = field(default_factory=lambda: ['LLM', 'language model', 'transformer', 'GPT', 'BERT'])
    arxiv_max_results: int = 10
    
    # Processing settings
    batch_size: int = 5
    log_level: str = 'INFO'
