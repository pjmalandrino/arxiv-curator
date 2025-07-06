"""Main application entry point."""

import logging
import sys
from pathlib import Path

from .core.config import Config
from .core.exceptions import ConfigurationError, ArxivCuratorError
from .infrastructure import (
    DatabaseSession,
    DatabaseManager,
    ArxivClient,
    HuggingFaceClient,
    OllamaClient
)
from .services import CurationService, PipelineService
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)


def initialize_components(config: Config):
    """Initialize all application components.
    
    Args:
        config: Application configuration
        
    Returns:
        tuple: Initialized components (db_manager, curation_service, pipeline_service)
    """
    # Initialize database
    db_session = DatabaseSession(config.database)
    db_session.create_tables()
    db_manager = DatabaseManager(db_session)
    
    # Initialize clients
    arxiv_client = ArxivClient(config.arxiv)
    hf_client = HuggingFaceClient(config.huggingface)
    
    # Initialize Ollama client if configured
    ollama_client = None
    try:
        ollama_client = OllamaClient(config.ollama)
        logger.info("Ollama client initialized for enhanced scoring")
    except Exception as e:
        logger.warning(f"Ollama client not available: {e}")
    
    # Initialize services
    curation_service = CurationService(
        db_manager=db_manager,
        arxiv_client=arxiv_client,
        hf_client=hf_client,
        ollama_client=ollama_client
    )
    
    pipeline_service = PipelineService(
        curation_service=curation_service,
        processing_config=config.processing
    )
    
    return db_manager, curation_service, pipeline_service

def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = Config.from_environment()
        config.validate()
        
        # Setup logging
        setup_logging(config.log_level, config.log_dir)
        
        logger.info("ArXiv Curator starting...")
        logger.info(f"Configuration loaded: {config.arxiv.categories}")
        
        # Initialize components
        db_manager, curation_service, pipeline_service = initialize_components(config)
        
        # Run pipeline
        results = pipeline_service.run_pipeline()
        
        # Log results
        logger.info("Pipeline execution completed")
        logger.info(f"Results: {results}")
        
        return 0
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return 1
        
    except ArxivCuratorError as e:
        logger.error(f"Application error: {e}")
        return 2
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 3
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 4


if __name__ == "__main__":
    sys.exit(main())
