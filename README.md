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

### Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

