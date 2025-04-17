"""To run:
python -m src.firecrawl_app
"""

import os
import json
from dotenv import load_dotenv
from firecrawl.firecrawl import FirecrawlApp

load_dotenv()
firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY")

app = FirecrawlApp(api_key=firecrawl_api_key)


def crawl(url):
    print(f"Crawling {url}...")
    # Start the crawl
    crawl_result = app.crawl_url(
        url,
        params={
            'limit': 100, 
            'scrapeOptions': {'formats': ['markdown', 'html']}
        },
        poll_interval=30
    )
    print(crawl_result)
    return crawl_result

def save_results(results, output_dir="./data"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"result.json")
    print(f"Saving result to {filename}")
    with open(filename, 'w', encoding='utf-8') as f:
        if isinstance(results, str):
            try:
                json_data = json.loads(results)
                f.write(json.dumps(json_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                f.write(results)
        else:
            f.write(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    website_url = os.getenv("URL")
    results = crawl(website_url)
    save_results(results)
    print(f"Results saved to {os.path.join('./data', 'result.json')}")