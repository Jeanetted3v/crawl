"""To run:
python -m src.crawl4ai.llm_extract_candidates
"""
import logging
import os
import json
import asyncio
import re
from dotenv import load_dotenv
from src.crawl4ai.extraction_model import ExtractedElectionData
from pydantic_ai import Agent
load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")


def clean_and_save_markdown_file(input_file_path, output_file_path):
    with open(input_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    constituency_sections = []
    
    # Match lines with constituency names (PAP candidate for X SMC or PAP team for Y GRC)
    constituency_matches = re.finditer(r'### PAP (candidate|team) for ([A-Za-z\s\-]+)(GRC|SMC)', content)
    
    for match in constituency_matches:
        # Keep the header and a few lines after it (date and potential candidate info)
        start_pos = match.start()
        end_pos = content.find('###', start_pos + 1)
        if end_pos == -1:  # If no next header, go to the end
            end_pos = len(content)
        
        section = content[start_pos:end_pos].strip()
        constituency_sections.append(section)
    
    # Join all found constituency sections
    cleaned_content = '\n\n---\n\n'.join(constituency_sections)
    
    # Save to new file
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(cleaned_content)
    
    print(f"Cleaned content saved to {output_file_path}")
    return cleaned_content


async def extract_website_content(
    cleaned_content: str
) -> ExtractedElectionData:
    extraction_agent = Agent(
        model="openai:gpt-4.1-mini",
        result_type=ExtractedElectionData,
        system_prompt="""
        You are an assistant specialized in extracting electoral data from website content. 
        
        Follow these steps in order:
        
        STEP 1: Identify and list ALL constituencies mentioned in the content.
        - First, carefully scan the entire document to identify every constituency name
        - Count and list each Group Representation Constituency (GRC)
        - Count and list each Single Member Constituency (SMC)
        - Verify your count matches approximately 24-26 total constituencies
        
        STEP 2: For each identified constituency, extract the following information:
        - The full constituency name (e.g., "Tampines GRC" or "Hougang SMC")
        - The type of constituency (GRC or SMC)
        - All political parties contesting in this constituency
        
        STEP 3: For each constituency, extract all candidate information:
        - Full name of each candidate
        - Their party affiliation
        - Their complete biography as provided in the content (include ALL details)
        - Any positions or roles mentioned (e.g., Minister, Mayor, etc.)
        
        STEP 4: Organize all information hierarchically by constituency.
        
        Be extremely thorough. Do not skip any constituencies or candidates. Extract ALL information available for each constituency and candidate.
        """
    )
    
    user_prompt = """
    Extract detailed electoral information from the following website content.
    
    For EACH constituency mentioned:
    - Extract the constituency name
    - Identify all parties contesting in this constituency
    - Extract all candidates contesting in this constituency
    - For each candidate, extract their name, party affiliation, and any biographical information
    
    Organize the data by constituency, with each constituency containing its contesting parties and candidates.
    
    Content:
    {website_data}
    """
    print("Extracting data from the website content...")
    result = await extraction_agent.run(
        user_prompt.format(website_data=cleaned_content)
    )
    extracted_info = result.output
    with open("./data/crawl4ai/raw_extracted_info.json", "w", encoding="utf-8") as f:
        json.dump(extracted_info.model_dump(), f, indent=2)
    logger.info(f"Extracted {len(extracted_info.constituencies)} constituencies with "
                f"a total of {sum(len(c.candidates) for c in extracted_info.constituencies)} candidates")
    return extracted_info


async def main():
    input_file = "./data/crawl4ai/pap_constituency_results.md"
    output_file = "./data/crawl4ai/cleaned_pap_constituency_results.md"
    cleaned_content = clean_and_save_markdown_file(input_file, output_file)
    logging.info(f"Cleaned content: {cleaned_content[:200]}...")
    extracted_info = await extract_website_content(cleaned_content)
    logging.info(f"Extracted info: {extracted_info}")

if __name__ == "__main__":
    asyncio.run(main())

