"""
Public API routes for non-authenticated users.
Provides read-only access to papers and statistics.
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc

public_bp = Blueprint('public', __name__, url_prefix='/api/public')


@public_bp.route('/stats', methods=['GET'])
def get_public_stats():
    """Get public statistics about papers."""
    from flask import current_app
    db_manager = current_app.config['db_manager']
    
    try:
        with db_manager.session_scope() as session:
            # Total papers count
            total_papers = session.query(func.count(db_manager.paper_model.id)).scalar()
            
            # Papers from last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_papers = session.query(func.count(db_manager.paper_model.id)).filter(
                db_manager.paper_model.published_date >= week_ago
            ).scalar()
            
            # Average relevance score
            avg_score = session.query(func.avg(db_manager.paper_model.relevance_score)).scalar()
            
            return jsonify({
                "total_papers": total_papers or 0,
                "recent_papers": recent_papers or 0,
                "average_score": float(avg_score) if avg_score else 0.0,
                "last_update": datetime.utcnow().isoformat()
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@public_bp.route('/papers', methods=['GET'])
def get_public_papers():
    """Get public list of papers with pagination."""
    from flask import current_app
    db_manager = current_app.config['db_manager']
    
    # Parse query parameters
    limit = min(int(request.args.get('limit', 10)), 50)
    offset = max(int(request.args.get('offset', 0)), 0)
    min_score = float(request.args.get('min_score', 0.5))
    
    try:
        with db_manager.session_scope() as session:
            query = session.query(db_manager.paper_model).filter(
                db_manager.paper_model.relevance_score >= min_score
            )
            
            # Order by published date descending
            query = query.order_by(desc(db_manager.paper_model.published_date))
            
            # Apply pagination
            papers = query.offset(offset).limit(limit).all()
            
            # Convert to dict format
            papers_data = []
            for paper in papers:
                papers_data.append({
                    "arxiv_id": paper.arxiv_id,
                    "title": paper.title,
                    "abstract": paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract,
                    "authors": paper.authors,
                    "published_date": paper.published_date.isoformat(),
                    "relevance_score": float(paper.relevance_score) if paper.relevance_score else 0.0,
                    "categories": paper.categories
                })
            
            return jsonify({
                "papers": papers_data,
                "count": len(papers_data),
                "offset": offset,
                "limit": limit
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@public_bp.route('/papers/<arxiv_id>', methods=['GET'])
def get_public_paper(arxiv_id):
    """Get details of a specific paper by ArXiv ID."""
    from flask import current_app
    db_manager = current_app.config['db_manager']
    
    try:
        with db_manager.session_scope() as session:
            paper = session.query(db_manager.paper_model).filter(
                db_manager.paper_model.arxiv_id == arxiv_id
            ).first()
            
            if not paper:
                return jsonify({"error": "Paper not found"}), 404
            
            return jsonify({
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "published_date": paper.published_date.isoformat(),
                "relevance_score": float(paper.relevance_score) if paper.relevance_score else 0.0,
                "categories": paper.categories,
                "pdf_url": f"https://arxiv.org/pdf/{paper.arxiv_id}.pdf",
                "arxiv_url": f"https://arxiv.org/abs/{paper.arxiv_id}"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
