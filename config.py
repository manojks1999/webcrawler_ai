# config.py

# List of e-commerce domains to crawl
DOMAINS = [
    # "https://www.virgio.com",
    # "https://www.tatacliq.com",
    # "https://nykaafashion.com",
    # "https://www.westside.com"
]

# Common product URL patterns to identify product pages
PRODUCT_URL_PATTERNS = [
    "/collections/luna-blu-women-footwear/"
    "/collections/all/",
    "/product/",
    "/item/",
    "/p/",
    "/products/",
    "/shop/",
    "/buy/",
    "-pd-",
    "pdp"
]

# Maximum number of pages to crawl per domain
MAX_PAGES_PER_DOMAIN = 10

# Maximum depth for crawling (how many links deep to follow)
MAX_DEPTH = 10

# Delay between requests in seconds (to be polite to servers)
REQUEST_DELAY = 1