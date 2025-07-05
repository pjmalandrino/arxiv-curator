from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy import create_engine, text
import os
import json
from datetime import datetime, timedelta
import subprocess
import threading
import logging
import traceback

from ..config import Config
from ..arxiv_client import ArxivClient
from ..hf_client import HuggingFaceClient
from ..database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://curator:secretpassword@localhost:5432/arxiv_curator')
engine = create_engine(DATABASE_URL)

# Global variables to track pipeline status
pipeline_running = False
pipeline_status = {"status": "idle", "message": "", "progress": 0}

def get_admin_config():
    """Get current configuration from database or defaults"""
    query = """
    SELECT key, value FROM admin_config
    """
    
    config = {
        'days_back': 7,
        'max_results': 10,
        'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
        'keywords': ['LLM', 'language model', 'transformer', 'GPT', 'BERT'],
        'batch_size': 5,
        'min_relevance_score': 0.4
    }
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            for row in result:
                key = row.key
                value = row.value
                if key in ['days_back', 'max_results', 'batch_size']:
                    config[key] = int(value)
                elif key == 'min_relevance_score':
                    config[key] = float(value)
                elif key in ['categories', 'keywords']:
                    config[key] = json.loads(value)
                else:
                    config[key] = value
    except Exception as e:
        logger.warning(f"Could not load admin config: {e}")
    
    return config

def save_admin_config(config_data):
    """Save configuration to database"""
    # First, create table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS admin_config (
        key VARCHAR(100) PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()
        
        # Save each config item
        for key, value in config_data.items():
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            else:
                value = str(value)
            
            upsert_query = """
            INSERT INTO admin_config (key, value, updated_at) 
            VALUES (:key, :value, CURRENT_TIMESTAMP)
            ON CONFLICT (key) 
            DO UPDATE SET value = :value, updated_at = CURRENT_TIMESTAMP
            """
            
            conn.execute(text(upsert_query), {'key': key, 'value': value})
        
        conn.commit()

def run_pipeline_thread(config_data):
    """Run the pipeline in a separate thread"""
    global pipeline_running, pipeline_status
    
    logger.info("Pipeline thread started")
    
    try:
        pipeline_status = {"status": "running", "message": "Initializing pipeline...", "progress": 10}
        logger.info("Pipeline status set to running")
        
        # Create custom config with admin settings
        config = Config()
        config.arxiv_categories = config_data.get('categories', ['cs.CL', 'cs.AI', 'cs.LG'])
        config.arxiv_keywords = config_data.get('keywords', ['LLM', 'language model'])
        config.arxiv_max_results = config_data.get('max_results', 10)
        config.batch_size = config_data.get('batch_size', 5)
        config.min_relevance_score = config_data.get('min_relevance_score', 0.4)
        
        logger.info(f"Config created with categories: {config.arxiv_categories}")
        
        # Initialize components
        pipeline_status["message"] = "Connecting to ArXiv..."
        pipeline_status["progress"] = 20
        
        try:
            arxiv_client = ArxivClient(config.arxiv_categories, config.arxiv_keywords)
            logger.info("ArxivClient initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ArxivClient: {e}")
            raise
        
        try:
            hf_client = HuggingFaceClient(model=config.hf_model, api_key=config.hf_token)
            logger.info("HuggingFaceClient initialized")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFaceClient: {e}")
            raise
        
        try:
            db_manager = DatabaseManager(config.database_url)
            logger.info("DatabaseManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseManager: {e}")
            raise
        
        # Fetch papers
        pipeline_status["message"] = f"Fetching papers from last {config_data.get('days_back', 7)} days..."
        pipeline_status["progress"] = 30
        
        try:
            papers = arxiv_client.fetch_recent_papers(
                max_results=config.arxiv_max_results,
                days_back=config_data.get('days_back', 7)
            )
            logger.info(f"Fetched {len(papers)} papers from ArXiv")
        except Exception as e:
            logger.error(f"Failed to fetch papers: {e}")
            raise
        
        pipeline_status["message"] = f"Found {len(papers)} papers. Processing..."
        pipeline_status["progress"] = 40
        
        # Process papers
        new_papers_count = 0
        total_papers = len(papers)
        
        if total_papers == 0:
            pipeline_status = {
                "status": "completed",
                "message": "No new papers found for the specified criteria.",
                "progress": 100
            }
            return
        
        for i, paper_data in enumerate(papers):
            try:
                # Update progress
                progress = 40 + int((i / total_papers) * 50)
                pipeline_status["progress"] = progress
                pipeline_status["message"] = f"Processing paper {i+1}/{total_papers}: {paper_data['title'][:50]}..."
                
                # Check if paper exists
                if db_manager.paper_exists(paper_data['arxiv_id']):
                    logger.info(f"Paper {paper_data['arxiv_id']} already exists, skipping")
                    continue
                
                # Save paper
                paper = db_manager.save_paper(paper_data)
                if not paper:
                    logger.warning(f"Failed to save paper {paper_data['arxiv_id']}")
                    continue
                
                # Generate summary
                logger.info(f"Generating summary for {paper_data['arxiv_id']}")
                summary_data = hf_client.summarize_paper(paper_data)
                if summary_data:
                    db_manager.save_summary(paper.id, summary_data)
                    new_papers_count += 1
                    logger.info(f"Summary saved for {paper_data['arxiv_id']}")
                
            except Exception as e:
                logger.error(f"Error processing paper {paper_data.get('arxiv_id', 'unknown')}: {e}")
                continue
        
        pipeline_status = {
            "status": "completed",
            "message": f"Pipeline completed successfully! Processed {new_papers_count} new papers out of {total_papers} found.",
            "progress": 100
        }
        logger.info(f"Pipeline completed: {new_papers_count} new papers processed")
        
    except Exception as e:
        error_msg = f"Pipeline error: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        pipeline_status = {
            "status": "error",
            "message": error_msg,
            "progress": 0
        }
    finally:
        pipeline_running = False
        logger.info("Pipeline thread finished")

@admin_bp.route('/')
def admin_index():
    """Admin dashboard"""
    config = get_admin_config()
    
    # Get statistics
    stats_query = """
    SELECT 
        COUNT(DISTINCT p.id) as total_papers,
        COUNT(DISTINCT s.id) as total_summaries,
        MAX(p.published_date) as latest_paper_date,
        MIN(p.published_date) as oldest_paper_date
    FROM papers p
    LEFT JOIN summaries s ON p.id = s.paper_id
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(stats_query))
        row = result.fetchone()
        
        stats = {
            'total_papers': row.total_papers,
            'total_summaries': row.total_summaries,
            'latest_paper_date': row.latest_paper_date.strftime('%Y-%m-%d') if row.latest_paper_date else 'N/A',
            'oldest_paper_date': row.oldest_paper_date.strftime('%Y-%m-%d') if row.oldest_paper_date else 'N/A'
        }
    
    return render_template('admin/dashboard.html', config=config, stats=stats, pipeline_status=pipeline_status)

@admin_bp.route('/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        config_data = {
            'days_back': int(request.form.get('days_back', 7)),
            'max_results': int(request.form.get('max_results', 10)),
            'categories': request.form.getlist('categories[]'),
            'keywords': [k.strip() for k in request.form.get('keywords', '').split(',') if k.strip()],
            'batch_size': int(request.form.get('batch_size', 5)),
            'min_relevance_score': float(request.form.get('min_relevance_score', 0.4))
        }
        
        save_admin_config(config_data)
        
        return jsonify({"success": True, "message": "Configuration updated successfully!"})
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route('/trigger-pipeline', methods=['POST'])
def trigger_pipeline():
    """Trigger the pipeline"""
    global pipeline_running, pipeline_status
    
    logger.info("Pipeline trigger requested")
    
    if pipeline_running:
        logger.warning("Pipeline already running")
        return jsonify({"success": False, "message": "Pipeline is already running!"}), 400
    
    try:
        pipeline_running = True
        pipeline_status = {"status": "starting", "message": "Starting pipeline...", "progress": 5}
        config = get_admin_config()
        
        logger.info(f"Starting pipeline with config: {config}")
        
        # Start pipeline in a separate thread
        pipeline_thread = threading.Thread(target=run_pipeline_thread, args=(config,))
        pipeline_thread.daemon = True  # Make thread daemon so it doesn't prevent shutdown
        pipeline_thread.start()
        
        return jsonify({"success": True, "message": "Pipeline started successfully!"})
    except Exception as e:
        logger.error(f"Failed to start pipeline: {str(e)}", exc_info=True)
        pipeline_running = False
        pipeline_status = {"status": "error", "message": f"Failed to start: {str(e)}", "progress": 0}
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/pipeline-status')
def pipeline_status_endpoint():
    """Get pipeline status"""
    return jsonify(pipeline_status)

@admin_bp.route('/clear-database', methods=['POST'])
def clear_database():
    """Clear all papers and summaries"""
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM summaries"))
            conn.execute(text("DELETE FROM papers"))
            conn.commit()
        
        return jsonify({"success": True, "message": "Database cleared successfully!"})
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/categories')
def get_categories():
    """Get all available arXiv categories"""
    # Common CS categories
    categories = [
        {'code': 'cs.AI', 'name': 'Artificial Intelligence'},
        {'code': 'cs.CL', 'name': 'Computation and Language'},
        {'code': 'cs.CV', 'name': 'Computer Vision and Pattern Recognition'},
        {'code': 'cs.LG', 'name': 'Machine Learning'},
        {'code': 'cs.NE', 'name': 'Neural and Evolutionary Computing'},
        {'code': 'cs.RO', 'name': 'Robotics'},
        {'code': 'cs.CR', 'name': 'Cryptography and Security'},
        {'code': 'cs.DB', 'name': 'Databases'},
        {'code': 'cs.DC', 'name': 'Distributed, Parallel, and Cluster Computing'},
        {'code': 'cs.DS', 'name': 'Data Structures and Algorithms'},
        {'code': 'cs.GT', 'name': 'Computer Science and Game Theory'},
        {'code': 'cs.HC', 'name': 'Human-Computer Interaction'},
        {'code': 'cs.IR', 'name': 'Information Retrieval'},
        {'code': 'cs.IT', 'name': 'Information Theory'},
        {'code': 'cs.LO', 'name': 'Logic in Computer Science'},
        {'code': 'cs.MA', 'name': 'Multiagent Systems'},
        {'code': 'cs.MM', 'name': 'Multimedia'},
        {'code': 'cs.NA', 'name': 'Numerical Analysis'},
        {'code': 'cs.NI', 'name': 'Networking and Internet Architecture'},
        {'code': 'cs.OS', 'name': 'Operating Systems'},
        {'code': 'cs.PL', 'name': 'Programming Languages'},
        {'code': 'cs.SE', 'name': 'Software Engineering'},
        {'code': 'cs.SI', 'name': 'Social and Information Networks'},
        {'code': 'cs.SY', 'name': 'Systems and Control'},
    ]
    
    return jsonify(categories)
