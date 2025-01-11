import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
from concurrent.futures import ThreadPoolExecutor


class AsyncProductCrawler:
    # Patterns to identify potential product URLs
    PRODUCT_PATTERNS = [r"/product/", r"/item/", r"/p/", r"/catalogue/"]

    def __init__(self, max_depth=2, max_pages=10, max_concurrent_requests=3):
        """
        :param max_depth: Maximum depth to crawl for URLs
        :param max_pages: Maximum number of pages to crawl per domain
        :param max_concurrent_requests: Maximum concurrent requests to run
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.max_concurrent_requests = max_concurrent_requests

    async def fetch_url(self, session, url):
        """
        Fetch a URL asynchronously.

        :param session: The aiohttp session object
        :param url: The URL to fetch
        :return: The HTML content of the page or None if an error occurs
        """
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
        return None

    def parse_links(self, html, base_url):
        """
        Parse and extract all valid links from an HTML page.

        :param html: The HTML content of the page
        :param base_url: The base URL to resolve relative links
        :return: A set of absolute URLs found on the page
        """
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for link in soup.find_all("a", href=True):
            href = urljoin(base_url, link["href"])
            # Avoid fragments like #section
            parsed_href = urlparse(href)._replace(fragment="").geturl()
            links.add(parsed_href)
        return links

    def is_product_url(self, url):
        """
        Check if the URL matches any product pattern.

        :param url: URL to check
        :return: True if the URL matches a product pattern, else False
        """
        return any(re.search(pattern, url) for pattern in self.PRODUCT_PATTERNS)

    async def crawl_domain(self, domain):
        """
        Crawl a single domain to find product URLs.

        :param domain: The domain to crawl (e.g., "books.toscrape.com")
        :return: A list of discovered product URLs
        """
        print(f"Starting crawl for domain: {domain}")

        # Initialize BFS queue
        queue = asyncio.Queue()
        await queue.put((f"https://{domain}", 0))  # (URL, Depth)

        visited = set()
        product_urls = set()

        async with ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            while not queue.empty() and len(visited) < self.max_pages:
                current_url, depth = await queue.get()

                # Skip if max depth is reached or URL is already visited
                if depth > self.max_depth or current_url in visited:
                    continue

                # Mark the URL as visited
                visited.add(current_url)

                # Fetch the page content
                html = await self.fetch_url(session, current_url)
                if html is None:
                    continue

                # Parse the page and extract links
                links = self.parse_links(html, current_url)

                # Process each link
                for link in links:
                    if link in visited:
                        continue
                    if self.is_product_url(link):
                        product_urls.add(link)
                    elif domain in link:  # Only crawl links within the same domain
                        await queue.put((link, depth + 1))

        print(f"Finished crawl for domain: {domain}. Found {len(product_urls)} product URLs.")
        return list(product_urls)

    async def crawl_domains(self, domains):
        """
        Crawl multiple domains concurrently.

        :param domains: A list of domains to crawl
        :return: A dictionary mapping each domain to its list of product URLs
        """
        results = {}
        tasks = []

        # Limit the number of concurrent domain crawls
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async def crawl_with_semaphore(domain):
            async with semaphore:
                results[domain] = await self.crawl_domain(domain)

        for domain in domains:
            tasks.append(crawl_with_semaphore(domain))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)
        return results

    def save_results(self, results, filename="product_urls.json"):
        """
        Save the crawl results to a JSON file.

        :param results: Dictionary of domain -> product URLs
        :param filename: File to save the results
        """
        with open(filename, "w") as file:
            json.dump(results, file, indent=4)
        print(f"Results saved to {filename}")


# Main function to run the crawler
def main():
    # List of domains to crawl
    domains = ["books.toscrape.com"]

    # Initialize the async crawler
    crawler = AsyncProductCrawler(max_depth=2, max_pages=50, max_concurrent_requests=5)

    # Run the crawler using asyncio
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(crawler.crawl_domains(domains))

    # Save results to a file
    crawler.save_results(results)


if __name__ == "__main__":
    main()

