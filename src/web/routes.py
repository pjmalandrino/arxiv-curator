"""Web application routes."""

from flask import Blueprint, render_template, jsonify, request, current_app
from datetime import datetime, timedelta

papers_bp = Blueprint('papers', __name__)
api_bp = Blueprint('api', __name__)


@papers_bp.route('/')
def index():
    """Home page showing recent papers."""
    return render_template('index.html')


@papers_bp.route('/papers')
def papers_list():
    """List all papers."""
    return render_template('papers.html')


@papers_bp.route('/paper/<arxiv_id>')
def paper_detail(arxiv_id):
    """Show paper details."""
    return render_template('paper_detail.html', arxiv_id=arxiv_id)


@api_bp.route('/papers', methods=['GET'])
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
            'last_update': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
