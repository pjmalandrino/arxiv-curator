from flask import Flask, render_template, jsonify, request, redirect, url_for
from sqlalchemy import create_engine, text
from datetime import datetime, date
import os
import json

app = Flask(__name__, 
            static_folder='../static',
            template_folder='../templates')

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@localhost:5432/arxiv_curator')
engine = create_engine(DATABASE_URL)

def date_handler(obj):
    """JSON serializer for date objects"""
    if isinstance(obj, (datetime, date)):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def get_papers_with_summaries():
    """Récupère tous les papiers avec leurs résumés"""
    query = """
    SELECT 
        p.id,
        p.arxiv_id,
        p.title,
        p.authors,
        p.abstract,
        p.published_date,
        p.categories,
        p.pdf_url,
        s.summary,
        s.key_points,
        s.relevance_score,
        s.model_used,
        s.created_at as summary_created_at
    FROM papers p
    LEFT JOIN summaries s ON p.id = s.paper_id
    ORDER BY p.published_date DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        papers = []
        for row in result:
            # key_points is already a list from PostgreSQL ARRAY
            key_points = row.key_points if row.key_points else []

            paper_dict = {
                'id': str(row.id),
                'arxiv_id': row.arxiv_id,
                'title': row.title,
                'authors': row.authors,  # This is also already a list
                'abstract': row.abstract[:300] + '...' if len(row.abstract) > 300 else row.abstract,
                'published_date': row.published_date,  # Keep as date object for template
                'published_date_str': row.published_date.strftime('%Y-%m-%d'),  # Also provide string version
                'categories': row.categories,  # This is also already a list
                'pdf_url': row.pdf_url,
                'summary': row.summary,
                'key_points': key_points,
                'relevance_score': row.relevance_score,
                'model_used': row.model_used,
                'has_summary': row.summary is not None
            }
            papers.append(paper_dict)

        return papers

def get_statistics():
    """Récupère les statistiques de la base de données"""
    stats_query = """
    SELECT 
        COUNT(DISTINCT p.id) as total_papers,
        COUNT(DISTINCT s.id) as total_summaries,
        AVG(s.relevance_score) as avg_relevance,
        MAX(p.published_date) as latest_paper_date
    FROM papers p
    LEFT JOIN summaries s ON p.id = s.paper_id
    """

    with engine.connect() as conn:
        result = conn.execute(text(stats_query))
        row = result.fetchone()

        return {
            'total_papers': row.total_papers,
            'total_summaries': row.total_summaries,
            'avg_relevance': round(row.avg_relevance, 2) if row.avg_relevance else 0,
            'latest_paper_date': row.latest_paper_date,  # Keep as date object
            'latest_paper_date_str': row.latest_paper_date.strftime('%Y-%m-%d') if row.latest_paper_date else 'N/A'
        }

@app.route('/')
def index():
    """Page principale"""
    papers = get_papers_with_summaries()
    stats = get_statistics()

    return render_template('index.html', papers=papers, stats=stats)

@app.route('/api/papers')
def api_papers():
    """API endpoint pour récupérer les papiers"""
    papers = get_papers_with_summaries()
    # Use custom JSON encoder for dates
    return app.response_class(
        response=json.dumps(papers, default=date_handler),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/stats')
def api_stats():
    """API endpoint pour les statistiques"""
    stats = get_statistics()
    # Use custom JSON encoder for dates
    return app.response_class(
        response=json.dumps(stats, default=date_handler),
        status=200,
        mimetype='application/json'
    )

@app.route('/paper/<arxiv_id>')
def paper_detail(arxiv_id):
    """Page de détail d'un papier"""
    query = """
    SELECT 
        p.*,
        s.summary,
        s.key_points,
        s.relevance_score,
        s.model_used,
        s.created_at as summary_created_at
    FROM papers p
    LEFT JOIN summaries s ON p.id = s.paper_id
    WHERE p.arxiv_id = :arxiv_id
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {'arxiv_id': arxiv_id})
        row = result.fetchone()

        if not row:
            return "Paper not found", 404

        paper = {
            'id': str(row.id),
            'arxiv_id': row.arxiv_id,
            'title': row.title,
            'authors': row.authors,  # Already a list
            'abstract': row.abstract,
            'published_date': row.published_date,  # Keep as date object for template
            'published_date_str': row.published_date.strftime('%Y-%m-%d'),  # Also provide string version
            'categories': row.categories,  # Already a list
            'pdf_url': row.pdf_url,
            'summary': row.summary,
            'key_points': row.key_points if row.key_points else [],  # Already a list
            'relevance_score': row.relevance_score,
            'model_used': row.model_used,
            'has_summary': row.summary is not None
        }

        return render_template('paper_detail.html', paper=paper)

@app.route('/search')
def search():
    """Search papers by title"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('index'))
    
    search_query = """
    SELECT 
        p.id,
        p.arxiv_id,
        p.title,
        p.authors,
        p.abstract,
        p.published_date,
        p.categories,
        p.pdf_url,
        s.summary,
        s.key_points,
        s.relevance_score,
        s.model_used
    FROM papers p
    LEFT JOIN summaries s ON p.id = s.paper_id
    WHERE LOWER(p.title) LIKE LOWER(:query)
    ORDER BY p.published_date DESC
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(search_query), {'query': f'%{query}%'})
        papers = []
        for row in result:
            paper_dict = {
                'id': str(row.id),
                'arxiv_id': row.arxiv_id,
                'title': row.title,
                'authors': row.authors,
                'abstract': row.abstract[:300] + '...' if len(row.abstract) > 300 else row.abstract,
                'published_date': row.published_date,
                'categories': row.categories,
                'pdf_url': row.pdf_url,
                'summary': row.summary,
                'key_points': row.key_points if row.key_points else [],
                'relevance_score': row.relevance_score,
                'model_used': row.model_used,
                'has_summary': row.summary is not None
            }
            papers.append(paper_dict)
    
    return render_template('search_results.html', papers=papers, query=query)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)