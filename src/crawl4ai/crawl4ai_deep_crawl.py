"""To run
python -m src.crawl4ai.crawl4ai_deep_crawl
"""
import os
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import (
    BFSDeepCrawlStrategy,
    BestFirstCrawlingStrategy
)
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter


async def main():
    # scorer = KeywordRelevanceScorer(
    #     keywords=["crawl", "example", "async", "configuration"],
    #     weight=0.7
    # )
    # constituency_filter = URLPatternFilter(patterns=["*grc*", "*smc*"])
    combined_filter = URLPatternFilter(patterns=[
        "*grc*",                         # Match GRC pages
        "*smc*",                         # Match SMC pages
        "*/category/featured/page/*"     # Match pagination pages
    ])

    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2,
            filter_chain=FilterChain([combined_filter]),
            include_external=False,
            # url_scorer=scorer,
            max_pages=100,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )

    results = []
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(
            "https://www.pap.org.sg/category/featured/",
            config=config
        )
        for result in results:
            depth = result.metadata.get("depth", 0)
            print(f"Depth: {depth} | {result.url}")
    
    output_dir = "./data/crawl4ai"
    os.makedirs(output_dir, exist_ok=True)
    output_file = "pap_constituency_results.md"
    output_file_path = os.path.join(output_dir, output_file)
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("# PAP Constituency Pages Crawl Results\n\n")
        f.write(f"Total pages crawled: {len(results)}\n\n")
        
        # Group by depth
        depth_counts = {}
        for result in results:
            depth = result.metadata.get("depth", 0)
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        f.write("## Pages crawled by depth:\n\n")
        for depth, count in sorted(depth_counts.items()):
            f.write(f"- Depth {depth}: {count} pages\n")
        f.write("\n")
        
        # Write detailed results for each page
        f.write("## Detailed Results\n\n")
        for result in results:
            title = result.metadata.get("title", "Untitled")
            depth = result.metadata.get("depth", 0)
            
            f.write(f"### {title}\n\n")
            f.write(f"- URL: {result.url}\n")
            f.write(f"- Depth: {depth}\n\n")
            
            # Add content summary
            if hasattr(result, 'markdown') and result.markdown:
                f.write("**Content:**\n\n")
                f.write(result.markdown + "\n\n")
            
            f.write("---\n\n")


if __name__ == "__main__":
    asyncio.run(main())