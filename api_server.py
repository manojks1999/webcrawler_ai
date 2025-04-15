import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from urllib.parse import urlparse
import os
from utils.db_utils import DB_PATH
from utils.db_utils import init_db, add_url_to_crawl
from utils.data_utils import extract_domain
from typing import Optional

init_db()

app = FastAPI(title="Web Crawler API", description="API for adding URLs to crawl queue")

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 10
    max_depth: int = 3

class CrawlResponse(BaseModel):
    id: int
    url: str
    status: str
    message: str

@app.post("/api/crawl", response_model=CrawlResponse)
async def add_url(crawl_request: CrawlRequest):  # Add type annotation here
    print("Received request to add URL to crawl queue:", crawl_request)
    try:
        parsed_url = urlparse(crawl_request.url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        print("Invalid URL format")
        raise HTTPException(status_code=400, detail="Invalid URL format")
    try:
        print("Extracting domain", crawl_request)
        domain = extract_domain(crawl_request.url)
        
        url_id = add_url_to_crawl(
            url=crawl_request.url,
            domain=domain,
            max_pages=crawl_request.max_pages,
            max_depth=crawl_request.max_depth
        )
        
        if url_id == -1:
            return CrawlResponse(
                id=-1,
                url=crawl_request.url,
                status="duplicate",
                message="URL already exists in the crawl queue"
            )
        
        return CrawlResponse(
            id=url_id,
            url=crawl_request.url,
            status="pending",
            message="URL added to crawl queue successfully"
        )
    except Exception as e:
        print(f"Error adding URL to crawl queue: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def root():
    return {"message": "Web Crawler API is running. Use /api/crawl to add URLs to crawl."}

from utils.db_utils import (
    get_pending_urls,
    update_url_status,
    save_crawled_products,
    add_url_to_crawl,
    init_db
)

import sqlite3

class StatusUpdateRequest(BaseModel):
    url_id: int
    status: str

class Product(BaseModel):
    url: str
    domain: str
    product_id: Optional[str] = None
    category: Optional[str] = None

class ProductSaveRequest(BaseModel):
    crawl_id: int
    products: list[Product]

@app.get("/api/products")
async def get_products():
    from utils.db_utils import get_all_products
    products = get_all_products()
    return {"products": products}

@app.get("/api/products/{crawl_id}")
async def get_products_by_crawl_id(crawl_id):
    from utils.db_utils import get_products_by_crawl_id
    products = get_products_by_crawl_id(crawl_id)
    return {"products": products}

@app.get("/api/pending-urls")
async def get_pending():
    return get_pending_urls()

@app.put("/api/update-status")
async def update_status(req):
    valid_status = ['pending', 'processing', 'completed', 'failed']
    if req.status not in valid_status:
        raise HTTPException(status_code=400, detail="Invalid status value")
    
    update_url_status(req.url_id, req.status)
    return {"message": f"Status updated to {req.status} for ID {req.url_id}"}

@app.post("/api/save-products")
async def save_products(req):
    save_crawled_products([p.dict() for p in req.products], req.crawl_id)
    return {"message": "Products saved successfully"}

@app.delete("/api/delete-url/{url_id}")
async def delete_url(url_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urls_to_crawl WHERE id = ?", (url_id,))
    conn.commit()
    conn.close()
    return {"message": f"Deleted URL with id {url_id}"}

@app.delete("/api/delete-product/{product_id}")
async def delete_product(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM crawled_products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"message": f"Deleted product with id {product_id}"}

@app.delete("/api/clear-urls")
async def clear_all_urls():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urls_to_crawl")
    conn.commit()
    conn.close()
    return {"message": "All URLs cleared from crawl queue."}

@app.delete("/api/clear-products")
async def clear_all_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM crawled_products")
    conn.commit()
    conn.close()
    return {"message": "All crawled products cleared."}

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)


