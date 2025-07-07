"""Web application routes."""

from flask import Blueprint, render_template, jsonify, request, current_app
from datetime import datetime, timedelta
from ..auth import require_auth, require_admin, get_current_user

papers_bp = Blueprint('papers', __name__)
api_bp = Blueprint('api', __name__)


@papers_bp.route('/')
def index():
    """API info page."""
    return jsonify({
        'message': 'ArXiv Curator API',
        'version': '1.0.0',
        'endpoints': {
            'papers': '/api/papers',
            'stats': '/api/stats',
            'auth': '/api/auth/me'
        },
        'frontend': 'http://localhost:3000'
    })


@papers_bp.route('/papers')
def papers_list():
    """Redirect to API."""
    return jsonify({'message': 'Use /api/papers for JSON data'})


@papers_bp.route('/paper/<arxiv_id>')
def paper_detail(arxiv_id):
    """Redirect to API."""
    return jsonify({'message': f'Use /api/paper/{arxiv_id} for JSON data'})


@api_bp.route('/papers', methods=['GET'])
@require_auth
def get_papers():
    """API endpoint to get papers.
    
    Query parameters:
    - days: Number of days to look back (default: 7)
    - limit: Maximum number of papers (default: 50)
    - min_score: Minimum relevance score (default: 0.0)
    """
    db_manager = current_app.config['db_manager']
    
    # Parse query parameters
    days = int(request.args.get('days', 7))
    limit = int(request.args.get('limit', 50))
    min_score = float(request.args.get('min_score', 0.0))
    
    try:
        # Get recent papers
        papers = db_manager.get_recent_papers(days=days)
        
        # Convert to JSON-serializable format
        papers_data = []
        for paper in papers[:limit]:
            paper_dict = {
                'id': str(paper.id),
                'arxiv_id': paper.metadata.arxiv_id,
                'title': paper.metadata.title,
                'authors': paper.metadata.authors,
                'abstract': paper.metadata.abstract[:500] + '...',
                'published_date': paper.metadata.published_date.isoformat(),
                'categories': paper.metadata.categories,
                'pdf_url': paper.metadata.pdf_url,
                'created_at': paper.created_at.isoformat()
            }
            papers_data.append(paper_dict)
        
        return jsonify({
            'papers': papers_data,
            'count': len(papers_data),
            'query': {
                'days': days,
                'limit': limit,
                'min_score': min_score
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/paper/<arxiv_id>', methods=['GET'])
@require_auth
def get_paper(arxiv_id):
    """API endpoint to get a specific paper."""
    db_manager = current_app.config['db_manager']
    
    try:
        # This would need to be implemented in DatabaseManager
        # For now, return a placeholder
        return jsonify({
            'error': 'Not implemented yet',
            'arxiv_id': arxiv_id
        }), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """API endpoint to get curation statistics."""
    db_manager = current_app.config['db_manager']
    
    try:
        # Get statistics
        total_papers = len(db_manager.get_recent_papers(days=365))
        recent_papers = len(db_manager.get_recent_papers(days=7))
        
        return jsonify({
            'total_papers': total_papers,
            'recent_papers': recent_papers,
            'average_score': 0.75,  # Placeholder value
            'last_update': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/public/stats', methods=['GET'])
def get_public_stats():
    """Public API endpoint to get basic statistics."""
    db_manager = current_app.config['db_manager']
    
    try:
        # Get basic statistics that are safe to share publicly
        total_papers = len(db_manager.get_recent_papers(days=365))
        recent_papers = len(db_manager.get_recent_papers(days=7))
        
        return jsonify({
            'total_papers': total_papers,
            'recent_papers': recent_papers,
            'last_update': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/user/bookmarks', methods=['GET'])
@require_auth
def get_user_bookmarks():
    """Get user's bookmarked papers."""
    user = get_current_user()
    
    # Placeholder implementation
    return jsonify({
        'bookmarks': [],
        'user_id': user.user_id,
        'message': 'User bookmarks feature not implemented yet'
    })


@api_bp.route('/admin/pipeline/trigger', methods=['POST'])
@require_admin
def trigger_pipeline():
    """Admin-only endpoint to trigger curation pipeline."""
    user = get_current_user()
    
    # Placeholder implementation
    return jsonify({
        'message': 'Pipeline trigger requested',
        'triggered_by': user.username,
        'status': 'not_implemented'
    })
