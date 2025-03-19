import requests
from bs4 import BeautifulSoup
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)

def extract_content_from_url(url: str) -> str:
    """
    Extract text content from a given URL.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: The extracted text content
    """
    try:
        logger.info(f"Extracting content from {url} using BeautifulSoup method")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
            
        # Get text and remove extra whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text or len(text.strip()) < 10:
            logger.warning(f"Extracted content from {url} is empty or too short")
            return f"Error extracting content from {url}: Content was empty or too short"
        
        logger.info(f"Successfully extracted {len(text)} characters from {url}")
        return text
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error extracting content from {url}: {str(e)}\n{error_details}")
        return f"Error extracting content from {url}: {str(e)}" 