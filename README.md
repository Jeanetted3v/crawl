# Crawl
* This repositary is for testing out various web crawling and scraping tools for LLM projects. 
* Testing out:
    1. [FireCrawl](https://docs.firecrawl.dev/introduction)
    2. [Crawl4AI](https://github.com/unclecode/crawl4ai)
* Each of the crawl tool has its own folder in src folder. The data crawled and extracted are stored with the same name in data folder. 
```
crawl/
│
├── data/                  # Data directory
│   ├── firecrawl/         # Data for firecrawl
│   ├── craw4ai/           # Data for craw4ai
│   └── webcrawler3/       # Placeholder for third web crawler
│
├── src/                   # Source code
│   └── firecrawl/         # Firecrawl implementation
│       ├── firecrawl_app.py
│       ├── llm_extract.py
│       └── qna.py
│
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
└── requirements.in        # Package dependencies
```
    