import os
import ast
import json
import requests
from typing import List
from openai import OpenAI
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify as md
from concurrent.futures import ThreadPoolExecutor



def parse_list(llm_output: str) -> List[str] | None:
    try:
        return ast.literal_eval(llm_output)
    except (ValueError, SyntaxError):
        return None


class RufusScraper:
    def __init__(self, retries=3, max_depth=2, async_mode=True, max_workers=5, api_key=None):
        """
        Initializes the Rufus WebsiteScraper instance.
        :param retries: Number of retries for failed requests.
        :param max_depth: Maximum depth of web tree to crawl recursively.
        :param async_mode: Whether to use asynchronous mode for fetching content.
        :param max_workers: Maximum number of workers for concurrent fetching.
        :param api_key: OpenAI API key. If not provided, make sure to set as environment variable 'OPENAI_API_KEY'.
        """
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
                markdown_content = md(response.text)
                return markdown_content
            except Exception as e:
                print(f"Error fetching content from {url}: {e}")
        return None

    def fetch_relevant_links(self, url, depth=1):
        """
        Fetches and filters relevant links from a website during the crawling phase.
        :param url: The base URL to crawl.
        :param depth: Current depth of crawling (used for recursive depth control).
        :return: A list of relevant links.
        """
        if depth > self.max_depth or url in self.visited:
            return []

        self.visited.add(url)
        print(f"Crawling: {url} (Depth: {depth})")
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

            filtered_links = self.get_relevant_urls(self.prompt, links)
            filtered_links = parse_list(filtered_links)

            for link in filtered_links:
                filtered_links += self.fetch_relevant_links(link, depth + 1)

            return filtered_links
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
            return {'url': url, 'markdown': self.fetch_website_content(url)}

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

    def scrape(self, base_url, prompt, output_file='output.json'):
        """
        Orchestrates the scraping process:
        1. Fetches all links.
        2. Filters relevant links using OpenAI.
        3. Scrapes content from relevant links.

        :param base_url: The base URL to start scraping from.
        :param prompt: The prompt to guide the scraping process.
        :param output_file: The file to save the scraped results. [Optional](Default: output.json)
        """
        self.base_url = base_url
        self.prompt = prompt

        relevant_links = self.fetch_relevant_links(self.base_url)
        if self.async_mode:
            relevant_content = self.parallel_fetch_content(relevant_links)
        else:
            relevant_content = [
                {'url': url, 'markdown': self.fetch_website_content(url)} for url in relevant_links
            ]

        with open(output_file, "w") as f:
            json.dump(relevant_content, f, indent=2)
            print(f"Scraped results saved to {output_file}")

        return relevant_content

        # # Step 4: Analyze content with OpenAI
        # analyzed_results = {}
        # for url, content in relevant_content.items():
        #     analyzed_results[url] = self.analyze_with_openai(prompt, content)

        # return analyzed_results


if __name__ == "__main__":

    base_url = "https://www.sjsu.edu/"
    prompt = "Admission procedure for international students"

    rufus = RufusScraper(retries=3, max_depth=1, async_mode=True, max_workers=5)
    output = rufus.scrape(base_url, prompt)
