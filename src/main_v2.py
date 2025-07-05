"""Updated ArXiv curation pipeline with advanced scoring system."""

import logging
import time
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from src.config import Config
from src.arxiv_client import ArxivClient
from src.hf_client import HuggingFaceClient
from src.database import DatabaseManager
from src.scoring import (
    ScoringConfig,
    create_scorer,
    get_default_config,
    Paper
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArxivCurationPipeline:
    def __init__(self, config: Config, scoring_config: Optional[ScoringConfig] = None):
        self.config = config
        self.scoring_config = scoring_config or get_default_config()
        
        # Initialize clients
        self.arxiv_client = ArxivClient(config.arxiv_categories, config.arxiv_keywords)
        self.hf_client = HuggingFaceClient(
            model=config.hf_model,
            api_key=config.hf_token
        )
        self.db_manager = DatabaseManager(config.database_url)
        
        # Initialize scorer
        self.scorer = create_scorer(self.scoring_config)
    
    async def score_paper(self, paper_data: Dict) -> Dict:
        """Score a paper using the configured scoring system."""
        # Convert to Paper object
        paper = Paper(
            arxiv_id=paper_data['arxiv_id'],
            title=paper_data['title'],
            abstract=paper_data.get('abstract', paper_data.get('summary', '')),
            authors=paper_data.get('authors', []),
            categories=paper_data.get('categories', []),
            published_date=paper_data.get('published', datetime.now()),
            pdf_url=paper_data.get('pdf_url', ''),
            metadata=paper_data
        )
        
        # Create context from configuration
        context = {
            'research_interests': self.scoring_config.keywords,
            'keywords': self.scoring_config.keywords
        }
        
        # Score the paper
        try:
            result = await self.scorer.score(paper, context)
            return {
                'score': result.score,
                'explanation': result.explanation,
                'components': result.components,
                'metadata': result.metadata
            }
        except Exception as e:
            logger.error(f"Error scoring paper {paper.arxiv_id}: {e}")
            return {
                'score': 0.5,
                'explanation': f"Scoring failed: {str(e)}",
                'components': {},
                'metadata': {'error': str(e)}
            }
    
    async def process_papers_async(self, papers: List[Dict]) -> List[Dict]:
        """Process papers asynchronously with scoring."""
        results = []
        
        for paper_data in papers:
            # Check if paper already exists
            if self.db_manager.paper_exists(paper_data['arxiv_id']):
                logger.info(f"Paper {paper_data['arxiv_id']} already exists, skipping...")
                continue
            
            # Score the paper
            score_result = await self.score_paper(paper_data)
            
            logger.info(f"Paper: {paper_data['title'][:60]}...")
            logger.info(f"  Score: {score_result['score']:.3f}")
            # Format components for logging
            comp_str = ', '.join(
                f"{k}: {v:.2f}" if isinstance(v, (int, float)) 
                else f"{k}: {v.get('score', 0):.2f}" 
                for k, v in score_result['components'].items()
            )
            logger.info(f"  Components: {comp_str}")
            
            # Only process papers above threshold
            if score_result['score'] < self.config.min_relevance_score:
                logger.info(f"  → Skipped (below threshold of {self.config.min_relevance_score})")
                continue
            
            # Save paper to database
            paper = self.db_manager.save_paper(paper_data)
            if not paper:
                continue
            
            # Generate summary
            logger.info(f"Generating summary for: {paper.title} (score: {score_result['score']:.2f})")
            # Update paper_data to ensure it has 'summary' key for HF client
            if 'summary' not in paper_data and 'abstract' in paper_data:
                paper_data['summary'] = paper_data['abstract']
            summary_data = self.hf_client.summarize_paper(paper_data)
            
            if summary_data:
                # Add scoring data to summary (only fields that exist in the model)
                summary_data['relevance_score'] = score_result['score']
                # Remove extra fields that don't exist in the Summary model
                summary_data.pop('score_explanation', None)
                summary_data.pop('score_components', None)
                
                self.db_manager.save_summary(paper.id, summary_data)
                
                results.append({
                    'paper': paper_data,
                    'score': score_result,
                    'summary': summary_data
                })
            
            # Rate limiting
            await asyncio.sleep(2)
        
        return results
    
    def run(self, days_back: int = 7):
        """Run the complete pipeline with scoring."""
        logger.info("Starting ArXiv curation pipeline with advanced scoring...")
        logger.info(f"Using HuggingFace model: {self.config.hf_model}")
        logger.info(f"Minimum relevance score: {self.config.min_relevance_score}")
        
        # 1. Fetch papers from ArXiv
        papers = self.arxiv_client.fetch_recent_papers(
            max_results=self.config.arxiv_max_results,
            days_back=days_back
        )
        logger.info(f"Fetched {len(papers)} papers from ArXiv")
        
        # 2. Process papers with scoring (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(self.process_papers_async(papers))
            
            # 3. Generate report
            self._generate_report(results)
            
        finally:
            loop.close()
        
        logger.info(f"Pipeline completed. Processed {len(results)} high-quality papers.")
    
    def _generate_report(self, results: List[Dict]):
        """Generate a report of processed papers."""
        if not results:
            logger.info("No papers met the relevance threshold.")
            return
        
        logger.info("\n" + "="*80)
        logger.info("CURATION REPORT")
        logger.info("="*80)
        
        # Sort by score
        results.sort(key=lambda x: x['score']['score'], reverse=True)
        
        for i, result in enumerate(results[:10], 1):  # Top 10
            paper = result['paper']
            score = result['score']
            
            logger.info(f"\n{i}. {paper['title']}")
            logger.info(f"   ArXiv ID: {paper['arxiv_id']}")
            logger.info(f"   Score: {score['score']:.3f} - {score['explanation']}")
            logger.info(f"   Components: " + ", ".join(
                f"{k}: {v:.2f}" if isinstance(v, (int, float)) else f"{k}: {v['score']:.2f}"
                for k, v in score['components'].items()
            ))
        
        # Summary statistics
        avg_score = sum(r['score']['score'] for r in results) / len(results)
        logger.info(f"\nTotal papers processed: {len(results)}")
        logger.info(f"Average relevance score: {avg_score:.3f}")
        
        # Component analysis
        component_totals = {}
        for result in results:
            for comp, value in result['score']['components'].items():
                if isinstance(value, dict) and 'score' in value:
                    score_val = value['score']
                else:
                    score_val = value
                
                if comp not in component_totals:
                    component_totals[comp] = []
                component_totals[comp].append(score_val)
        
        logger.info("\nAverage component scores:")
        for comp, scores in component_totals.items():
            avg = sum(scores) / len(scores)
            logger.info(f"  {comp}: {avg:.3f}")


def main():
    """Main entry point with configurable scoring."""
    # Load base configuration
    config = Config()
    
    # Create custom scoring configuration
    # You can modify this based on your research interests
    scoring_config = ScoringConfig(
        # LLM settings (using Ollama)
        use_llm=True,
        llm_weight=0.3,
        ollama_host=config.ollama_host if hasattr(config, 'ollama_host') else None,
        ollama_model=config.ollama_model if hasattr(config, 'ollama_model') else None,
        
        # Keywords for your research area
        keywords=[
            "machine learning", "deep learning", "neural networks",
            "transformer", "llm", "generative ai", "reinforcement learning"
        ],
        boost_terms={
            "novel": 1.5,
            "state-of-the-art": 1.3,
            "efficient": 1.2,
            "scalable": 1.2
        },
        keyword_weight=0.25,
        
        # Citation settings
        min_citations=5,
        citation_weight=0.15,
        
        # Temporal settings - trending topics
        trend_keywords={
            "llm": 1.5,
            "rag": 1.4,
            "agent": 1.3,
            "multimodal": 1.3,
            "efficient": 1.2
        },
        temporal_weight=0.2,
        
        # Author settings
        known_authors={
            # Add your favorite researchers here
        },
        author_weight=0.1
    )
    
    # Create and run pipeline
    pipeline = ArxivCurationPipeline(config, scoring_config)
    pipeline.run(days_back=7)


if __name__ == "__main__":
    main()
