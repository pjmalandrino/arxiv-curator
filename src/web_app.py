"""Web application entry point."""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Config
from src.utils.logging import setup_logging
from src.web.app import create_app

logger = logging.getLogger(__name__)


def main():
    """Run the web application."""
    try:
        # Load configuration
        config = Config.from_environment()
        config.validate()
        
        # Setup logging
        setup_logging(config.log_level, config.log_dir)
        
        # Create Flask app
        app = create_app(config)
        
        # Run the application
        host = '0.0.0.0'  # Bind to all interfaces in container
        port = 5000
        debug = config.log_level == 'DEBUG'
        
        logger.info(f"Starting web server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.exception(f"Failed to start web application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
