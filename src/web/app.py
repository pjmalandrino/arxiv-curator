# src/web/app.py - Full featured web application
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Optional
from datetime import datetime

from src.core.database import get_db
from src.core.models import Paper, Summary

app = FastAPI(title="ArXiv Curator", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Beautiful HTML interface for viewing papers"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArXiv Curator</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0a0e27;
                color: #e0e6ed;
                line-height: 1.6;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            
            h1 { 
                font-size: 48px; 
                margin: 40px 0;
                text-align: center;
                background: linear-gradient(45deg, #00d4ff, #0099ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 30px;
                text-align: center;
                backdrop-filter: blur(10px);
            }
            
            .stat-number {
                font-size: 48px;
                font-weight: bold;
                color: #00d4ff;
                margin: 10px 0;
            }
            
            .paper {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 30px;
                margin-bottom: 20px;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            
            .paper:hover {
                transform: translateY(-2px);
                border-color: rgba(0,212,255,0.3);
                box-shadow: 0 10px 30px rgba(0,212,255,0.2);
            }
            
            .paper::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #00d4ff, #0099ff);
            }
            
            .score {
                position: absolute;
                top: 20px;
                right: 20px;
                background: linear-gradient(45deg, #00d4ff, #0099ff);
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
            }
            
            .title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
                color: #ffffff;
                padding-right: 100px;
            }
            
            .meta {
                color: #94a3b8;
                margin-bottom: 20px;
                font-size: 14px;
            }
            
            .abstract {
                background: rgba(0,0,0,0.3);
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                color: #cbd5e1;
            }
            
            .summary {
                background: rgba(0,212,255,0.1);
                border: 1px solid rgba(0,212,255,0.2);
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
            }
            
            .key-points {
                margin-top: 15px;
            }
            
            .key-points li {
                margin-left: 20px;
                margin-bottom: 8px;
                color: #e0e6ed;
            }
            
            .links {
                display: flex;
                gap: 15px;
                margin-top: 20px;
            }
            
            .links a {
                background: rgba(255,255,255,0.1);
                color: #00d4ff;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid rgba(0,212,255,0.3);
                transition: all 0.3s ease;
            }
            
            .links a:hover {
                background: rgba(0,212,255,0.2);
                transform: translateY(-2px);
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                font-size: 20px;
                color: #64748b;
            }
            
            .error {
                background: rgba(239,68,68,0.1);
                border: 1px solid rgba(239,68,68,0.3);
                color: #fca5a5;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔬 ArXiv Curator</h1>
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            <h2 style="margin-bottom: 20px; color: #94a3b8;">Recent Papers</h2>
            <div id="papers">
                <div class="loading">Loading papers...</div>
            </div>
        </div>
        
        <script>
            // Load statistics
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div>Total Papers</div>
                            <div class="stat-number">${data.total_papers}</div>
                        </div>
                        <div class="stat-card">
                            <div>With Summaries</div>
                            <div class="stat-number">${data.papers_with_summaries}</div>
                        </div>
                        <div class="stat-card">
                            <div>Average Score</div>
                            <div class="stat-number">${data.average_score.toFixed(1)}</div>
                        </div>
                    `;
                })
                .catch(err => {
                    document.getElementById('stats').innerHTML = '<div class="error">Error loading stats</div>';
                });
            
            // Load papers
            fetch('/api/papers?limit=20')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('papers');
                    container.innerHTML = '';
                    
                    data.papers.forEach(paper => {
                        const div = document.createElement('div');
                        div.className = 'paper';
                        div.innerHTML = `
                            ${paper.summary ? `<div class="score">${paper.summary.relevance_score}/10</div>` : ''}
                            <div class="title">${paper.title}</div>
                            <div class="meta">
                                <strong>Authors:</strong> ${paper.authors.join(', ')}<br>
                                <strong>Published:</strong> ${new Date(paper.published_date).toLocaleDateString()}<br>
                                <strong>Categories:</strong> ${paper.categories.join(', ')}<br>
                                <strong>ArXiv ID:</strong> ${paper.arxiv_id}
                            </div>
                            <div class="abstract">
                                <strong>Abstract:</strong><br>
                                ${paper.abstract}
                            </div>
                            ${paper.summary ? `
                                <div class="summary">
                                    <strong>AI Summary:</strong><br>
                                    ${paper.summary.text}
                                    ${paper.summary.key_points && paper.summary.key_points.length > 0 ? `
                                        <div class="key-points">
                                            <strong>Key Points:</strong>
                                            <ul>
                                                ${paper.summary.key_points.map(p => `<li>${p}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}
                                </div>
                            ` : ''}
                            <div class="links">
                                <a href="${paper.pdf_url}" target="_blank">📄 View PDF</a>
                                <a href="https://arxiv.org/abs/${paper.arxiv_id}" target="_blank">🔗 ArXiv Page</a>
                            </div>
                        `;
                        container.appendChild(div);
                    });
                })
                .catch(err => {
                    document.getElementById('papers').innerHTML = `<div class="error">Error loading papers: ${err}</div>`;
                });
        </script>
    </body>
    </html>
    """

@app.get("/api/stats")
def get_stats():
    """Get database statistics"""
    with get_db() as db:
        total_papers = db.query(Paper).count()
        papers_with_summaries = db.query(Paper).join(Summary).count()

        # Calculate average score
        summaries = db.query(Summary.relevance_score).all()
        avg_score = sum(s[0] for s in summaries) / len(summaries) if summaries else 0

        return {
            "total_papers": total_papers,
            "papers_with_summaries": papers_with_summaries,
            "average_score": avg_score
        }

@app.get("/api/papers")
def get_papers(limit: int = 10, offset: int = 0):
    """Get papers with summaries"""
    with get_db() as db:
        papers = db.query(Paper).order_by(Paper.published_date.desc()).offset(offset).limit(limit).all()

        result = []
        for paper in papers:
            summary = db.query(Summary).filter(Summary.paper_id == paper.id).first()

            paper_dict = {
                "id": str(paper.id),
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "authors": paper.authors[:5],  # Limit authors shown
                "abstract": paper.abstract,
                "published_date": paper.published_date.isoformat(),
                "categories": paper.categories,
                "pdf_url": paper.pdf_url,
                "summary": None
            }

            if summary:
                paper_dict["summary"] = {
                    "text": summary.summary,
                    "key_points": summary.key_points or [],
                    "relevance_score": summary.relevance_score,
                    "model_used": summary.model_used
                }

            result.append(paper_dict)

        return {"papers": result, "count": len(result), "total": db.query(Paper).count()}

@app.get("/api/papers/{arxiv_id}")
def get_paper(arxiv_id: str):
    """Get a specific paper by ArXiv ID"""
    with get_db() as db:
        paper = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        summary = db.query(Summary).filter(Summary.paper_id == paper.id).first()

        return {
            "paper": {
                "id": str(paper.id),
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "published_date": paper.published_date.isoformat(),
                "categories": paper.categories,
                "pdf_url": paper.pdf_url,
                "summary": {
                    "text": summary.summary,
                    "key_points": summary.key_points or [],
                    "relevance_score": summary.relevance_score,
                    "model_used": summary.model_used
                } if summary else None
            }
        }