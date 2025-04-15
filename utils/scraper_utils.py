import asyncio
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
)

from config import PRODUCT_URL_PATTERNS, REQUEST_DELAY
from models.product import Product
from utils.data_utils import extract_domain, is_duplicate_url, is_product_url

def get_browser_config():
    return BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=True,
    )

async def extract_links_from_page(crawler, url, session_id):
    print(f"Extracting links from {url}...")
    
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
        ),
    )

    if not result.success:
        print(f"Error fetching page {url}: {result.error_message}")
        return []

    soup = BeautifulSoup(result.cleaned_html, "html.parser")
    links = []
    
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href")
        if href and not href.startswith("javascript:") and not href.startswith("#"):
            absolute_url = urljoin(url, href)
            if extract_domain(absolute_url) == extract_domain(url):
                links.append(absolute_url)
    
    print(f"Found {len(links)} links on {url}")
    return links

async def crawl_domain_for_products(
    crawler,
    domain,
    max_pages,
    max_depth,
    session_id,
    seen_urls,
):
    print(f"Starting depth-first crawl of domain: {domain}")
    
    to_visit = [(domain, 0)]
    products = []
    pages_visited = 0
    
    while to_visit and pages_visited < max_pages:
        current_url, depth = to_visit.pop()
        
        if current_url in seen_urls:
            continue
        
        seen_urls.add(current_url)
        pages_visited += 1
        
        print(f"Visiting page {pages_visited}/{max_pages}: {current_url} (depth: {depth})")
        
        if is_product_url(current_url, PRODUCT_URL_PATTERNS):
            product_id = extract_product_id(current_url)
            category = extract_category(current_url)
            
            product = Product(
                url=current_url,
                domain=domain,
                product_id=product_id,
                category=category
            )
            products.append(product)
            print(f"Found product URL: {current_url}")
        
        if depth < max_depth:
            links = await extract_links_from_page(crawler, current_url, session_id)
            
            for link in links:
                if link not in seen_urls:
                    # have a rabbitmq queue for this and have a worker that consumes the queue and crawls the links and saves the products to the db
                    # have a worker that consumes the queue and crawls the links and saves the products to the db
                    to_visit.append((link, depth + 1))
        
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"Completed crawl of {domain}. Visited {pages_visited} pages, found {len(products)} product URLs.")
    return products

def extract_product_id(url):
    patterns = [
        r"/p/([\w-]+)",
        r"/product/([\w-]+)",
        r"/products/([\w-]+)",
        r"pid=([\w]+)",
        r"product_id=([\w]+)",
        r"id=([\w]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def extract_category(url):
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    
    if len(parts) >= 2 and any(pattern in url for pattern in PRODUCT_URL_PATTERNS):
        return parts[-2]
    
    return None

async def crawl_multiple_domains(
    domains,
    max_pages_per_domain,
    max_depth,
):
    browser_config = get_browser_config()
    session_id = "ecommerce_product_crawler"
    
    results = {}
    seen_urls = set()
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for domain in domains:
            domain_products = await crawl_domain_for_products(
                crawler,
                domain,
                max_pages_per_domain,
                max_depth,
                session_id,
                seen_urls,
            )
            
            results[domain] = domain_products
            
            await asyncio.sleep(REQUEST_DELAY * 2)
    
    return results