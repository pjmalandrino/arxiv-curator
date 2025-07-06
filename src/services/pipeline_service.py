"""Pipeline service for orchestrating the curation workflow."""

import logging
import time
from typing import List, Dict, Any

from ..core.config import ProcessingConfig
from ..core.exceptions import ArxivCuratorError
from .curation_service import CurationService

logger = logging.getLogger(__name__)


class PipelineService:
    """Service for running the paper curation pipeline."""
    
    def __init__(
        self,
        curation_service: CurationService,
        processing_config: ProcessingConfig
    ):
        """Initialize pipeline service.
        
        Args:
            curation_service: Curation service for processing papers
            processing_config: Processing configuration
        """
        self.curation_service = curation_service
        self.config = processing_config

    def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete curation pipeline.
        
        Returns:
            Dict[str, Any]: Pipeline execution results
        """
        logger.info("Starting ArXiv curation pipeline...")
        start_time = time.time()
        
        results = {
            "total_fetched": 0,
            "new_papers": 0,
            "skipped_papers": 0,
            "failed_papers": 0,
            "errors": []
        }
        
        try:
            # Fetch recent papers
            papers = self.curation_service.arxiv_client.fetch_recent_papers(
                days_back=self.config.days_lookback
            )
            results["total_fetched"] = len(papers)
            logger.info(f"Fetched {len(papers)} papers from ArXiv")
            
            # Process papers in batches
            for i in range(0, len(papers), self.config.batch_size):
                batch = papers[i:i + self.config.batch_size]
                logger.info(f"Processing batch {i // self.config.batch_size + 1}")
                
                for paper_data in batch:
                    try:
                        paper = self.curation_service.process_paper(paper_data)
                        if paper:
                            results["new_papers"] += 1
                        else:
                            results["skipped_papers"] += 1
                            
                    except Exception as e:
                        results["failed_papers"] += 1
                        results["errors"].append({
                            "arxiv_id": paper_data.get("arxiv_id", "unknown"),
                            "error": str(e)
                        })
                        logger.error(f"Failed to process paper: {e}")
                    
                    # Rate limiting between papers
                    time.sleep(2)

            # Calculate execution time
            execution_time = time.time() - start_time
            results["execution_time"] = f"{execution_time:.2f} seconds"
            
            # Log summary
            logger.info(
                f"Pipeline completed in {execution_time:.2f}s: "
                f"{results['new_papers']} new papers, "
                f"{results['skipped_papers']} skipped, "
                f"{results['failed_papers']} failed"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise ArxivCuratorError(f"Pipeline execution failed: {e}") from e
    
    def run_batch_with_retry(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of papers with retry logic.
        
        Args:
            papers: List of paper data dictionaries
            
        Returns:
            Dict[str, Any]: Batch processing results
        """
        results = {
            "processed": 0,
            "failed": 0,
            "retried": 0
        }
        
        for paper_data in papers:
            success = False
            
            for attempt in range(self.config.retry_attempts):
                try:
                    paper = self.curation_service.process_paper(paper_data)
                    if paper:
                        results["processed"] += 1
                        success = True
                        break
                        
                except Exception as e:
                    if attempt < self.config.retry_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for "
                            f"{paper_data.get('arxiv_id')}: {e}"
                        )
                        results["retried"] += 1
                        time.sleep(self.config.retry_delay)
                    else:
                        logger.error(
                            f"All attempts failed for "
                            f"{paper_data.get('arxiv_id')}: {e}"
                        )
            
            if not success:
                results["failed"] += 1
        
        return results
