"""Flask application factory."""

import logging
from flask import Flask
from flask_cors import CORS

from ..core.config import Config
from ..infrastructure import DatabaseSession, DatabaseManager
from .routes import papers_bp, api_bp

logger = logging.getLogger(__name__)


def create_app(config: Config = None) -> Flask:
    """Create and configure Flask application.
    
    Args:
        config: Application configuration
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = Config.from_environment()
    
    # Configure Flask
    app.config['SECRET_KEY'] = 'arxiv-curator-secret-key'  # Should be in env
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db_session = DatabaseSession(config.database)
    db_manager = DatabaseManager(db_session)
    
    # Store in app context
    app.config['db_manager'] = db_manager
    app.config['app_config'] = config
    
    # Register blueprints
    app.register_blueprint(papers_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500
    
    logger.info("Flask application created successfully")
    return app
