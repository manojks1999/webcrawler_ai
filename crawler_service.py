import asyncio
import time
import sys
import os
from datetime import datetime

from utils.db_utils import init_db, get_pending_urls, update_url_status, save_crawled_products
from utils.scraper_utils import AsyncWebCrawler, get_browser_config, crawl_domain_for_products
from models.product import Product

init_db()

async def process_url(url_data):
    url_id = url_data['id']
    url = url_data['url']
    domain = url_data['domain']
    max_pages = url_data['max_pages']
    max_depth = url_data['max_depth']
    
    print(f"Processing URL: {url} (ID: {url_id})")
    
    update_url_status(url_id, 'processing')
    
    try:
        browser_config = get_browser_config()
        session_id = f"crawler_service_{url_id}_{int(time.time())}"
        seen_urls = set()
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            products = await crawl_domain_for_products(
                crawler=crawler,
                domain=url,
                max_pages=max_pages,
                max_depth=max_depth,
                session_id=session_id,
                seen_urls=seen_urls,
            )
            
            product_dicts = [product.dict() for product in products]
            
            save_crawled_products(product_dicts, url_id)
            
            update_url_status(url_id, 'completed')
            
            print(f"Completed processing URL: {url} (ID: {url_id}). Found {len(products)} products.")
            print("products", products)
    except Exception as e:
        print(f"Error processing URL: {url} (ID: {url_id}): {str(e)}")
        update_url_status(url_id, 'failed')

CHECK_INTERVAL = 10

async def run_crawler_service():
    print(f"[{datetime.now()}] Starting crawler service loop...")

    while True:
        print(f"[{datetime.now()}] Checking for pending URLs...")
        pending_urls = get_pending_urls()

        if not pending_urls:
            print(f"[{datetime.now()}] No pending URLs found. Sleeping for {CHECK_INTERVAL} seconds.")
        else:
            print(f"[{datetime.now()}] Found {len(pending_urls)} pending URLs to process.")

            for url_data in pending_urls:
                await process_url(url_data)

            print(f"[{datetime.now()}] Finished processing current batch of URLs.")

        await asyncio.sleep(CHECK_INTERVAL)

def main():
    asyncio.run(run_crawler_service())

if __name__ == "__main__":
    main()