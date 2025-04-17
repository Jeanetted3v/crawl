"""To run:
python -m src.llm_extract
"""
import logging
import os, json
import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")


async def extract_website_content() -> str:
    extraction_agent = Agent(
        model="openai:gpt-4.1-mini",
        result_type=str,
        system_prompt="""
        You are an assistant specialized in content extraction. Your job is to extract 
        all meaningful information from the given website content, which contains both 
        English and Chinese text.
        
        Return the extracted information in markdown format, preserving all original 
        Chinese characters. Do not translate anything at this stage."""
    )
    with open("./data/firecrawl/result.json", "r", encoding="utf-8") as f:
        website_data = json.load(f)

    combined_contents = []
    for item in website_data["data"]:
        content = ""
        if "markdown" in item and item["markdown"]:
            content += item["markdown"] + "\n\n"
        if "html" in item and item["html"]:
            content += f"HTML_CONTENT: {item['html']}\n\n"
        if content:
            combined_contents.append(content)
    
    website_content = "\n\n".join(combined_contents)
    logger.info(f"Sample of website content (first 500 chars): {website_content[:500]}")

    user_prompt = """
    {website_content}
    Extract useful information of the company from this website content and return it in markdown format.
    Make sure to preserve all Chinese text - it's critical information.
    """

    result = await extraction_agent.run(user_prompt.format(website_content=website_content))
    extracted_info = result.output
    with open("./data/firecrawl/raw_extracted_info.txt", "w", encoding="utf-8") as f:
        f.write(extracted_info)
    logging.info(f"Extracted info: {extracted_info}")
    return extracted_info


async def translate(extracted_info: str) -> None:
    translation_agent = Agent(
        model="openai:gpt-4.1-mini",
        result_type=str,
        system_prompt="""
        You are a translation agent. You will be given extracted information
        from a company's website, which might contain multi-language information.
        Your job is to translate all text to English and output it in markdown format.
        If all text is already in English, just return the text as it is.
        """
    )
    user_prompt = """
    {extracted_info}
    Translate all text to English.
    """
    result = await translation_agent.run(user_prompt.format(extracted_info=extracted_info))
    translated_info = result.output
    
    logging.info(f"Translated info: {translated_info}")
    with open("./data/firecrawl/translated_info.txt", "w", encoding="utf-8") as f:
        f.write(translated_info)
    logging.info(f"Translated information saved to data/translated_info.txt")

async def main():
    extracted_info = await extract_website_content()
    logging.info(f"Extracted info: {extracted_info}")
    await translate(extracted_info)
    logging.info("Translation completed.")

if __name__ == "__main__":
    asyncio.run(main())

