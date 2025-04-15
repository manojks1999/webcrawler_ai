import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawler.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS crawled_products')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crawled_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        domain TEXT NOT NULL,
        product_id TEXT,
        category TEXT,
        crawl_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crawl_id) REFERENCES urls_to_crawl (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_url_to_crawl(url, domain, max_pages = 10, max_depth = 3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO urls_to_crawl (url, domain, max_pages, max_depth) VALUES (?, ?, ?, ?)",
            (url, domain, max_pages, max_depth)
        )
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except sqlite3.IntegrityError:
        return -1
    finally:
        conn.close()

def get_pending_urls():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM urls_to_crawl WHERE status = 'pending' ORDER BY created_at ASC")
    rows = cursor.fetchall()
    print("kdfkdsnfkjdsdsd0d0d", rows)
    result = [dict(row) for row in rows]
    conn.close()
    
    return result

def update_url_status(url_id, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if status == 'processing':
        cursor.execute(
            "UPDATE urls_to_crawl SET status = ?, started_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, url_id)
        )
    elif status in ['completed', 'failed']:
        cursor.execute(
            "UPDATE urls_to_crawl SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, url_id)
        )
    else:
        cursor.execute(
            "UPDATE urls_to_crawl SET status = ? WHERE id = ?",
            (status, url_id)
        )
    
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM crawled_products ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    result = [dict(row) for row in rows]
    conn.close()
    
    return result

def get_products_by_crawl_id(crawl_id):
    print(f"\nDebug - Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM urls_to_crawl WHERE id = ?", (crawl_id,))
        url_data = cursor.fetchone()
        if url_data:
            url_data_dict = dict(url_data)
            print(f"Debug - Found URL data for crawl_id {crawl_id}:")
            print(f"  Status: {url_data_dict.get('status')}")
            print(f"  URL: {url_data_dict.get('url')}")
        else:
            print(f"Debug - No URL found for crawl_id {crawl_id}")
        
        cursor.execute("SELECT * FROM crawled_products WHERE crawl_id = ? ORDER BY created_at DESC", (crawl_id,))
        rows = cursor.fetchall()
        
        if rows:
            print(f"Debug - Found {len(rows)} products for crawl_id {crawl_id}")
            for row in rows:
                row_dict = dict(row)
                print(f"  Product URL: {row_dict.get('url')}")
                print(f"  Product ID: {row_dict.get('product_id')}")
        else:
            print(f"Debug - No products found for crawl_id {crawl_id}")
        
        result = [dict(row) for row in rows]
        return result
    except Exception as e:
        print(f"Debug - Error occurred: {str(e)}")
        raise
    finally:
        conn.close()
    
    return result

def save_crawled_products(products, crawl_id):
    if not products:
        return crawl_id
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("Saving products:", products, "crawl_id:", crawl_id)
    
    for product in products:
        cursor.execute(
            "INSERT INTO crawled_products (url, domain, product_id, category, crawl_id) VALUES (?, ?, ?, ?, ?)",
            (product['url'], product['domain'], product.get('product_id'), product.get('category'), crawl_id)
        )
        print(f"Inserted product: {product['url']}")
    
    conn.commit()
    conn.close()
    
    return crawl_id