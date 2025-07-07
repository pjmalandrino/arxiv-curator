"""Flask application factory."""

import logging
import os
from flask import Flask
from flask_cors import CORS

from ..core.config import Config
from ..infrastructure import DatabaseSession, DatabaseManager
from ..auth import JWTService, AuthenticationMiddleware
from .routes import papers_bp, api_bp
from .auth_routes import auth_bp
from .public_routes_flask import public_bp
from .health import health_bp

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
    app.config['SECRET_KEY'] = config.secret_key
    app.config['JSON_SORT_KEYS'] = False
    
    # Enhanced CORS configuration for Keycloak
    CORS(app, 
         origins=[
             "http://localhost:3000",  # Frontend dev
             "http://localhost:8080",  # Keycloak
         ],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True)
    
    # Initialize services
    db_session = DatabaseSession(config.database)
    db_manager = DatabaseManager(db_session)
    jwt_service = JWTService(config)
    
    # Store in app context
    app.config['db_manager'] = db_manager
    app.config['app_config'] = config
    app.config['jwt_service'] = jwt_service
    
    # Initialize authentication middleware
    # Define public paths that don't require authentication
    public_paths = [
        '/health',  # Health check endpoint
        '/api/auth/login',  # Login endpoint should be public
        '/api/auth/logout',  # Logout endpoint
        '/realms/',  # Keycloak metadata endpoints
        '/.well-known/',  # OpenID Connect discovery
        '/api/public/',  # All public API endpoints
    ]
    
    # Add debug mode public paths for development
    flask_env = os.getenv('FLASK_ENV', 'production')
    if flask_env == 'development':
        public_paths.extend([
            '/docs',  # API documentation
            '/swagger',  # Swagger UI
        ])
    
    # Initialize authentication middleware
    auth_middleware = AuthenticationMiddleware(app, public_paths=public_paths)
    
    # Register blueprints
    app.register_blueprint(health_bp)  # Health check endpoints (public)
    app.register_blueprint(papers_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(public_bp)  # Public routes already have prefix
    
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
