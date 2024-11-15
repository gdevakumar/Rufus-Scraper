# Rufus Scraper

Rufus Scraper is a Python-based web scraper designed to intelligently crawl websites, filter relevant links using OpenAI's GPT models, and extract content relevant to provided instructions in JSON format. It simplifies the process of extracting structured data from web pages based on user-defined prompts. This can be used further in a RAG pipeline.

---

## Features

- Recursive crawling with depth control.
- Relevance-based filtering using OpenAI API. (Support to more APIs/opensource LLMs from Huggingface will be added in the future)
- Concurrent fetching of webpage content for efficiency.
- Content extraction in Markdown format for easy integration.
- Saves results as JSON for further processing.

---

## Requirements

- Python 3.10+
- OpenAI API key (set as an environment variable or passed as a parameter).

## Install

### Install via Source

Clone the repository:
```bash
git clone https://github.com/gdevakumar/Rufus-Scraper
cd Rufus-Scraper
pip install -e .
```

### Install via PyPI
```bash
pip install rufus-scraper
```

---
### Parameters

#### RufusScraper Initialization

| Parameter     | Description                                                                                  | Default    |
|---------------|----------------------------------------------------------------------------------------------|------------|
| `retries`     | Number of retries for failed HTTP requests.                                                  | `3`        |
| `max_depth`   | Maximum depth of recursion for crawling linked pages.                                        | `2`        |
| `async_mode`  | Enables concurrent fetching of webpages for efficiency.                                      | `True`     |
| `max_workers` | Number of threads to use for concurrent fetching (applies if `async_mode=True`).             | `5`        |
| `api_key`     | OpenAI API key. If not set, the scraper will use the `OPENAI_API_KEY` environment variable.  | `None`     |

---
### Methods

#### `scrape(base_url, prompt, output_file='output.json')`

Orchestrates the scraping process:
1. Crawls the base URL to fetch relevant links.
2. Filters links based on the provided prompt using OpenAI.
3. Extracts content from relevant pages.
4. Saves the results as a JSON file.

| Parameter     | Description                                                                                  |
|---------------|----------------------------------------------------------------------------------------------|
| `base_url`    | The starting URL for the scraper.                                                           |
| `prompt`      | A text prompt to guide the relevance filtering of links.                                    |
| `output_file` | The name of the JSON file where the scraped results will be saved. (Default: `output.json`)  |

---

## Usage

```python
from rufus_scraper import RufusScraper

# Base URL and prompt
base_url = "https://www.sjsu.edu/"
prompt = "Admission procedure for international students"

# Initialize RufusScraper
rufus = RufusScraper(retries=3, max_depth=1, async_mode=True, max_workers=5)

# Start scraping
output = rufus.scrape(base_url, prompt, output_file="sjsu_admissions.json")

# Output results
print("Scraped data:", output)
```

---
