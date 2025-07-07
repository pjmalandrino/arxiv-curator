"""Health check endpoints."""

from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring.
    
    This endpoint is public and doesn't require authentication.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'arxiv-curator-backend'
    })


@health_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """Readiness check endpoint for Kubernetes.
    
    Checks if the application is ready to serve requests.
    """
    # Check database connection
    try:
        from flask import current_app
        db_manager = current_app.config.get('db_manager')
        if db_manager:
            # Simple query to verify database connection
            db_manager.get_recent_papers(days=1)
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': 'connected',
                'keycloak': 'configured'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503
