from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text
import os
import json
from datetime import datetime

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@localhost:5432/arxiv_curator')
engine = create_engine(DATABASE_URL)

def get_papers_with_summaries():
    """Get all papers with their summaries"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.arxiv_id, p.title, p.authors, p.abstract, p.published_date, 
                   p.categories, p.pdf_url, s.summary, s.key_points, s.relevance_score, s.model_used
            FROM papers p
            LEFT JOIN summaries s ON p.id = s.paper_id
            ORDER BY p.published_date DESC
        """))
        
        papers = []
        for row in result:
            # Handle PostgreSQL arrays and JSON fields
            authors = row.authors if row.authors else []
            categories = row.categories if row.categories else []
            key_points = json.loads(row.key_points) if row.key_points else []
            
            paper = {
                'arxiv_id': row.arxiv_id,
                'title': row.title,
                'authors': authors,
                'abstract': row.abstract,
                'published_date': row.published_date,
                'categories': categories,
                'pdf_url': row.pdf_url,
                'summary': {
                    'summary': row.summary,
                    'key_points': key_points,
                    'relevance_score': row.relevance_score,
                    'model_used': row.model_used
                } if row.summary else None
            }
            papers.append(paper)
        return papers

def get_paper_by_arxiv_id(arxiv_id):
    """Get a single paper by ArXiv ID"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.arxiv_id, p.title, p.authors, p.abstract, p.published_date, 
                   p.categories, p.pdf_url, s.summary, s.key_points, s.relevance_score, s.model_used
            FROM papers p
            LEFT JOIN summaries s ON p.id = s.paper_id
            WHERE p.arxiv_id = :arxiv_id
        """), {'arxiv_id': arxiv_id})
        
        row = result.fetchone()
        if not row:
            return None
            
        # Handle PostgreSQL arrays and JSON fields
        authors = row.authors if row.authors else []
        categories = row.categories if row.categories else []
        key_points = json.loads(row.key_points) if row.key_points else []
        
        paper = {
            'arxiv_id': row.arxiv_id,
            'title': row.title,
            'authors': authors,
            'abstract': row.abstract,
            'published_date': row.published_date,
            'categories': categories,
            'pdf_url': row.pdf_url,
            'summary': {
                'summary': row.summary,
                'key_points': key_points,
                'relevance_score': row.relevance_score,
                'model_used': row.model_used
            } if row.summary else None
        }
        return paper

def search_papers(query):
    """Search papers by title"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.arxiv_id, p.title, p.authors, p.abstract, p.published_date, 
                   p.categories, p.pdf_url, s.summary, s.key_points, s.relevance_score, s.model_used
            FROM papers p
            LEFT JOIN summaries s ON p.id = s.paper_id
            WHERE p.title ILIKE :query
            ORDER BY p.published_date DESC
        """), {'query': f'%{query}%'})
        
        papers = []
        for row in result:
            # Handle PostgreSQL arrays and JSON fields
            authors = row.authors if row.authors else []
            categories = row.categories if row.categories else []
            key_points = json.loads(row.key_points) if row.key_points else []
            
            paper = {
                'arxiv_id': row.arxiv_id,
                'title': row.title,
                'authors': authors,
                'abstract': row.abstract,
                'published_date': row.published_date,
                'categories': categories,
                'pdf_url': row.pdf_url,
                'summary': {
                    'summary': row.summary,
                    'key_points': key_points,
                    'relevance_score': row.relevance_score,
                    'model_used': row.model_used
                } if row.summary else None
            }
            papers.append(paper)
        return papers

@app.route('/')
def index():
    """Main page displaying all papers with their summaries"""
    papers = get_papers_with_summaries()
    return render_template('index.html', papers=papers)

@app.route('/paper/<arxiv_id>')
def paper_detail(arxiv_id):
    """Detailed view of a single paper"""
    paper = get_paper_by_arxiv_id(arxiv_id)
    if not paper:
        return "Paper not found", 404
    return render_template('paper_detail.html', paper=paper)

@app.route('/api/papers')
def api_papers():
    """API endpoint to get papers as JSON"""
    papers = get_papers_with_summaries()
    papers_data = []
    for paper in papers:
        papers_data.append({
            'arxiv_id': paper['arxiv_id'],
            'title': paper['title'],
            'authors': paper['authors'],
            'abstract': paper['abstract'][:200] + '...' if len(paper['abstract']) > 200 else paper['abstract'],
            'published_date': paper['published_date'].isoformat(),
            'categories': paper['categories'],
            'pdf_url': paper['pdf_url'],
            'summary': paper['summary']['summary'] if paper['summary'] else None,
            'relevance_score': paper['summary']['relevance_score'] if paper['summary'] else None
        })
    return jsonify(papers_data)

@app.route('/search')
def search():
    """Search papers by title or keywords"""
    query = request.args.get('q', '')
    if query:
        papers = search_papers(query)
    else:
        papers = []
    return render_template('search_results.html', papers=papers, query=query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
