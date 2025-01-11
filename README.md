# Web_Crawler
To run this code simply run python crawler.py, it will create output file with results in product_urls.json 

1. First install all import using pip
2. max_depth	: Limits how deep the crawler goes into the website's link structure, preventing unnecessary or infinite crawling.
3. max_pages	: Caps the total number of pages visited, ensuring the crawl doesn't take too long or consume too many resources.
4. max_concurrent_requests	: Controls how many HTTP requests are made in parallel, balancing speed and server/resource load.


Use cases of all imports
1. Concurrency and speed: asyncio, aiohttp, ThreadPoolExecutor.
asyncio and aiohttp are the foundation of asynchronous crawling, making the code scalable and fast.
ThreadPoolExecutor prevents blocking operations (like HTML parsing) from slowing down the event loop.

2. HTML processing: bs4 (BeautifulSoup).
bs4 is a widely-used and simple library for processing and extracting data from HTML.

3. URL handling: urllib.parse.
urllib.parse ensures robust handling of URLs (e.g., resolving relative paths, filtering domains).

4. Pattern matching: re (regex).

5. Data storage: json. It ensures results are stored in a portable, machine-readable format.

    PRODUCT_PATTERNS = [r"/product/", r"/item/", r"/p/", r"/catalogue/"] : It searches for following patterns in the given domain to find any page.
    domains = ["books.toscrape.com"] : for testing I am crawling this domain. It can be comma separated.
