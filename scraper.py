import os
import ast
import requests
from utils import parse_list
from openai import OpenAI
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def fetch_website_content(url, retry=3):
    for _ in range(retry):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            content = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = tag.get_text(strip=True)
                if text:
                    content.append(text)

            return " ".join(content)
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
    return None



def analyze_with_openai(prompt, content):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    try:
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # {"role": "system", "content": "You are an AI Agent that is capable of extracting all the URLs from the given markdown text and return them in a list."},
            # {"role": "user", "content": f"Based on the markdown content below, extract and return all the URLs in a list. \nMarkdown: {content}"}
            {"role": "user", "content": f"Extract the most relevant information from the following content based on this prompt: '{prompt}'\n\nContent:\n{content}"} 
            ]
        )

        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error analyzing content with OpenAI: {e}")
        return None


def fetch_all_links(url):
    """
    Fetches all links (anchor tags) from the given URL.
    """
    try:
        headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = href if href.startswith('http') else requests.compat.urljoin(url, href)
            links.append(full_url)

        return links
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
        return []


def get_relevant_urls(prompt, links):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    try:
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Based on the given instructions: '{prompt}', select the most relevant URLs which might contain relevant information from the following list of URLs: {links}.\n\nReturn ONLY the URLs as a list. (Ex: ['url_1', 'url_2'])"}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error getting relevant URLs: {e}")
        return []




web_content = fetch_website_content("https://www.sjsu.edu/")
# print(analyze_with_openai("What is the admission process to get into masters degree program at SJSU?", web_content))

# all_links = fetch_all_links("https://www.github.com/")
# relevant_links = get_relevant_urls("Student Benefits of Github", all_links)
# relevant_links = parse_list(relevant_links)

print(web_content)