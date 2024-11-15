import os
import requests
from openai import OpenAI
from utils import parse_list
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify as md
from concurrent.futures import ThreadPoolExecutor



class RufusScraper:
    def __init__(self, base_url, retries=3, max_depth=2, async_mode=True, max_workers=5, api_key=None):
        """
        Initializes the Rufus WebsiteScraper instance.
        :param base_url: The base URL to start scraping from.
        :param retries: Number of retries for failed requests.
        :param max_depth: Maximum depth of web tree to crawl recursively.
        :param async_mode: Whether to use asynchronous mode for fetching content.
        :param max_workers: Maximum number of workers for concurrent fetching.
        :param api_key: OpenAI API key. If not provided, make sure to set as environment variable 'OPENAI_API_KEY'.
        """
        self.base_url = base_url
        self.retries = retries
        self.max_depth = max_depth
        self.async_mode = async_mode
        self.max_workers = max_workers
        self.visited = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
        self.openai_client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def fetch_website_content(self, url):
        """
        Fetches content from a given URL and returns it as Markdown text.
        :param url: The URL to fetch content from.
        """
        for _ in range(self.retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                # soup = BeautifulSoup(response.text, 'html.parser')

                markdown_content = md(response.text)
                return markdown_content
            except Exception as e:
                print(f"Error fetching content from {url}: {e}")
        return None

    def crawl_all_links(self, url, depth=1):
        """
        Crawl all links(only URLs) from a website recursively up to max_depth.
        :param url: The URL to start crawling from.
        :param depth: The current depth of the crawl.
        """
        if depth > self.max_depth or url in self.visited:
            return []

        self.visited.add(url)
        print(f"Fetching links from: {url} (Depth: {depth})")
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            links = []
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                full_url = href if href.startswith('http') else urljoin(url, href)
                if full_url not in self.visited:
                    links.append(full_url)

            for link in links:
                links += self.crawl_all_links(link, depth + 1)

            return links
        except Exception as e:
            print(f"Error fetching links from {url}: {e}")
            return []

    def get_relevant_urls(self, prompt, links):
        """
        Filters relevant URLs using OpenAI.
        """
        try:
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": f"Based on the given instructions: '{prompt}', select the most relevant URLs which might contain relevant information from the following list of URLs: {links}.\n\nReturn ONLY the URLs as a list. (Ex: ['url_1', 'url_2'])"}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error! Failed to get relevant URLs: {e}")
            return []

    def parallel_fetch_content(self, urls):
        """
        Fetch content from multiple URLs in parallel and return results in the desired JSON format.
        """
        def fetch_content(url):
            return {'url': url, 'markdown_content': self.fetch_website_content(url)}

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(fetch_content, url): url for url in urls}
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error in parallel fetch for {futures[future]}: {e}")
        return results

    # def analyze_with_openai(self, prompt, content):
    #     """
    #     Analyzes content using OpenAI based on the given prompt.
    #     """
    #     try:
    #         completion = self.openai_client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             messages=[
    #                 {"role": "user", "content": f"Extract the most relevant information from the following content based on this prompt: '{prompt}'\n\nContent:\n{content}"}
    #             ]
    #         )
    #         return completion.choices[0].message.content
    #     except Exception as e:
    #         print(f"Error analyzing content with OpenAI: {e}")
    #         return None

    def scrape(self, prompt):
        """
        Orchestrates the scraping process:
        1. Fetches all links.
        2. Filters relevant links using OpenAI.
        3. Scrapes content from relevant links.
        """
        # Step 1: Fetch all links recursively
        all_links = self.crawl_all_links(self.base_url)

        # Step 2: Filter relevant URLs
        relevant_links = self.get_relevant_urls(prompt, all_links)
        relevant_links = parse_list(relevant_links)

        # Step 3: Fetch content from relevant URLs
        if self.async_mode:
            relevant_content = self.parallel_fetch_content(relevant_links)
        else:
            relevant_content = [{'url': url, 'markdown_content': self.fetch_website_content(url)} for url in relevant_links]

        # # Step 4: Analyze content with OpenAI
        # analyzed_results = {}
        # for url, content in relevant_content.items():
        #     analyzed_results[url] = self.analyze_with_openai(prompt, content)

        # return analyzed_results


if __name__ == "__main__":
    base_url = "https://www.github.com/"
    prompt = "Student Benefits of Github"

    scraper = RufusScraper(base_url, retries=3, max_depth=2, async_mode=True, max_workers=5)
    results = scraper.scrape(prompt)

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to results.json")

    # for url, analysis in results.items():
    #     print(f"Analysis for {url}:\n{analysis}\n")
