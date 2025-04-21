"""To run:
python -m src.crawl4ai.crawl4ai_basic
"""
import os
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode


async def main():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        browser_config = BrowserConfig(
            verbose=True,
            headless=True
        )
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url="https://www.pap.org.sg/featured/pap-team-for-marine-parade-braddell-heights-grc/")
            if result.success:
                print("Content:", result.markdown[:500])
                for image in result.media["images"]:
                    print(f"Found image: {image['src']}")
                output_dir = "./data/crawl4ai"
                os.makedirs(output_dir, exist_ok=True)
                output_file = "marine_parade_braddell_heights_grc.md"
                output_file_path = os.path.join(output_dir, output_file)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(result.markdown)
                print(f"Result saved to {output_file_path}")

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())