#!/usr/bin/env python3

import os
import sys
import time
import logging
from datetime import datetime

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'crawler_cron_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('crawler_cron')

def run_crawler_service():
    try:
        logger.info(f"Starting crawler service at {datetime.now()}")
        from crawler_service import main as crawler_main
        crawler_main()
        logger.info(f"Crawler service completed at {datetime.now()}")
    except Exception as e:
        logger.error(f"Error running crawler service: {str(e)}")

if __name__ == "__main__":
    start_time = time.time()
    logger.info("Starting cron job for web crawler")
    
    try:
        run_crawler_service()
    except Exception as e:
        logger.error(f"Unhandled exception in cron job: {str(e)}")
    
    execution_time = time.time() - start_time
    logger.info(f"Cron job completed in {execution_time:.2f} seconds")