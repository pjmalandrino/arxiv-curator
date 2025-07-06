"""Configuration management for ArXiv Curator."""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from .exceptions import ConfigurationError


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class ArxivConfig:
    """ArXiv API configuration settings."""
    categories: List[str]
    keywords: List[str]
    max_results: int = 10
    rate_limit_delay: float = 3.0  # seconds between requests


@dataclass
class HuggingFaceConfig:
    """HuggingFace API configuration settings."""
    api_key: str
    model: str = "facebook/bart-large-cnn"
    max_length: int = 1024
    min_length: int = 56
    timeout: int = 30


@dataclass
class OllamaConfig:
    """Ollama configuration for local LLM scoring."""
    host: str = "http://localhost:11434"
    model: str = "gemma3:4b"
    timeout: int = 60


@dataclass
class ProcessingConfig:
    """Processing pipeline configuration."""
    batch_size: int = 5
    min_relevance_score: float = 0.4
    days_lookback: int = 7
    retry_attempts: int = 3
    retry_delay: float = 5.0


@dataclass
class Config:
    """Main application configuration."""
    database: DatabaseConfig
    arxiv: ArxivConfig
    huggingface: HuggingFaceConfig
    ollama: OllamaConfig
    processing: ProcessingConfig
    log_level: str = "INFO"
    log_dir: Optional[Path] = None

    @classmethod
    def from_environment(cls) -> "Config":
        """Create configuration from environment variables.
        
        Returns:
            Config: Application configuration
            
        Raises:
            ConfigurationError: If required environment variables are missing
        """
        # Database configuration
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ConfigurationError("DATABASE_URL environment variable is required")

        # HuggingFace configuration
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ConfigurationError("HF_TOKEN environment variable is required")

        # Create configuration objects
        database = DatabaseConfig(
            url=database_url,
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )

        arxiv = ArxivConfig(
            categories=os.getenv("ARXIV_CATEGORIES", "cs.CL,cs.AI,cs.LG").split(","),
            keywords=os.getenv("ARXIV_KEYWORDS", "LLM,language model,transformer,GPT,BERT").split(","),
            max_results=int(os.getenv("ARXIV_MAX_RESULTS", "10")),
            rate_limit_delay=float(os.getenv("ARXIV_RATE_LIMIT", "3.0"))
        )

        huggingface = HuggingFaceConfig(
            api_key=hf_token,
            model=os.getenv("HF_MODEL", "facebook/bart-large-cnn"),
            max_length=int(os.getenv("HF_MAX_LENGTH", "1024")),
            min_length=int(os.getenv("HF_MIN_LENGTH", "56")),
            timeout=int(os.getenv("HF_TIMEOUT", "30"))
        )

        ollama = OllamaConfig(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "60"))
        )

        processing = ProcessingConfig(
            batch_size=int(os.getenv("BATCH_SIZE", "5")),
            min_relevance_score=float(os.getenv("MIN_RELEVANCE_SCORE", "0.4")),
            days_lookback=int(os.getenv("DAYS_LOOKBACK", "7")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "5.0"))
        )

        log_dir = os.getenv("LOG_DIR")
        
        return cls(
            database=database,
            arxiv=arxiv,
            huggingface=huggingface,
            ollama=ollama,
            processing=processing,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_dir=Path(log_dir) if log_dir else None
        )

    def validate(self) -> None:
        """Validate configuration settings.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self.processing.batch_size <= 0:
            raise ConfigurationError("Batch size must be positive")
            
        if not (0 <= self.processing.min_relevance_score <= 1):
            raise ConfigurationError("Relevance score must be between 0 and 1")
            
        if self.processing.days_lookback <= 0:
            raise ConfigurationError("Days lookback must be positive")
