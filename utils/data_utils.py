import csv
import json
import os
from typing import Dict, List, Set
from urllib.parse import urlparse

from models.product import Product

def is_duplicate_url(url, seen_urls):
    return url in seen_urls

def is_product_url(url, product_patterns):
    return any(pattern in url.lower() for pattern in product_patterns)

def extract_domain(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def save_products_to_csv(products, filename):
    if not products:
        print("No products to save.")
        return

    fieldnames = Product.model_fields.keys()
    print("kjdnfjkdsf", filename)
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([product.model_dump() for product in products])
    print(f"Saved {len(products)} product URLs to '{filename}'.")

def save_products_by_domain(products_by_domain, crawl_id):
    print("jkjkdsfnsd", products_by_domain)
    from utils.db_utils import save_crawled_products
    
    for domain, products in products_by_domain.items():
        save_crawled_products(products, crawl_id)
    
    print(f"Saved {sum(len(products) for products in products_by_domain.values())} products to database.")

    print("kjdsnfdsfsd", products_by_domain)
    summary_filename = os.path.join(output_dir, "summary.txt")
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write("E-commerce Product URL Crawler - Summary\n")
        f.write("===========================================\n\n")
        total_products = 0
        for domain, products in products_by_domain.items():
            count = len(products)
            total_products += count
            f.write(f"{domain}: {count} product URLs\n")
        f.write(f"\nTotal: {total_products} product URLs across {len(products_by_domain)} domains\n")
    
    print(f"Created summary at '{summary_filename}'.")