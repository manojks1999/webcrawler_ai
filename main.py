import asyncio
import os

from dotenv import load_dotenv

from config import DOMAINS, MAX_DEPTH, MAX_PAGES_PER_DOMAIN
from utils.data_utils import save_products_by_domain
from utils.scraper_utils import crawl_multiple_domains

load_dotenv()

async def main():
    print("E-commerce Product URL Crawler")
    print("=============================")
    print(f"Domains to crawl: {len(DOMAINS)}")
    for domain in DOMAINS:
        print(f"  - {domain}")
    print(f"Max pages per domain: {MAX_PAGES_PER_DOMAIN}")
    print(f"Max crawl depth: {MAX_DEPTH}")
    print("\nStarting crawl...\n")

    products_by_domain = await crawl_multiple_domains(
        domains=DOMAINS,
        max_pages_per_domain=MAX_PAGES_PER_DOMAIN,
        max_depth=MAX_DEPTH,
    )

    save_products_by_domain(products_by_domain)

    print("\nCrawl completed!")
    print("================")
    total_products = sum(len(products) for products in products_by_domain.values())
    print(f"Total product URLs found: {total_products}")
    for domain, products in products_by_domain.items():
        print(f"  - {domain}: {len(products)} product URLs")
    print("\nResults have been saved to the 'output' directory.")

if __name__ == "__main__":
    asyncio.run(main())