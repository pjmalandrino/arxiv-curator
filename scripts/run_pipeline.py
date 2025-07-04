#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import init_db, check_connection
from src.pipeline.runner import Pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if not check_connection():
        logger.error("Database connection failed")
        sys.exit(1)

    try:
        pipeline = Pipeline()
        stats = pipeline.run()
        logger.info(f"Pipeline complete: {stats}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
