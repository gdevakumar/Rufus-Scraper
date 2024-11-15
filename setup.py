from setuptools import setup, find_packages

setup(
    name="rufus-scraper",
    version="1.0.0",
    author="Deva Kumar Gajulamandyam",
    author_email="gdevakumar267@gmail.com",
    description="A smart web scraper powered by OpenAI for relevance-based content extraction.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gdevakumar/Rufus-Scraper", 
    packages=find_packages(), 
    install_requires=[
        "requests",
        "beautifulsoup4",
        "markdownify",
        "openai"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
