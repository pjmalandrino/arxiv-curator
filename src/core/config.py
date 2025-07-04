import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://curator:password@localhost:5432/arxiv_curator"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma2:9b"
    arxiv_categories: List[str] = ["cs.CL", "cs.AI", "cs.LG"]
    arxiv_keywords: List[str] = ["LLM", "language model", "transformer"]
    arxiv_max_results: int = 10
    batch_size: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
