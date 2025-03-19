from typing import List, Dict
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from websage.extractors.beautifulsoup_extractor import extract_content_from_url
from websage.extractors.langchain_extractor import extract_content_with_langchain, extract_content_with_html2text

# Configure logging
logger = logging.getLogger(__name__)

def process_urls(urls: List[str], use_langchain: bool = False) -> Dict[str, str]:
    """
    Process a list of URLs and extract content from each.
    
    Args:
        urls (List[str]): List of URLs to process
        use_langchain (bool): Whether to use LangChain's loaders
        
    Returns:
        Dict[str, str]: Dictionary mapping URLs to their extracted content
    """
    contents = {}
    
    # Clean URLs
    clean_urls = []
    for url in urls:
        url = url.strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            clean_urls.append(url)
    
    logger.info(f"Processing {len(clean_urls)} URLs with {'LangChain' if use_langchain else 'BeautifulSoup'} method")
    
    # Fallback mechanism: if the primary method fails, try the alternative
    if use_langchain and clean_urls:
        try:
            # Try AsyncHtmlLoader with Html2TextTransformer first
            docs = extract_content_with_html2text(clean_urls)
            
            # Check if we got valid results
            has_valid_content = False
            for doc in docs:
                url = doc.metadata.get("source")
                if url and not doc.page_content.startswith("Error"):
                    contents[url] = doc.page_content
                    has_valid_content = True
                else:
                    logger.warning(f"Invalid content for {url}: {doc.page_content[:100]}...")
            
            # If AsyncHtmlLoader failed for all URLs, try WebBaseLoader for each URL
            if not has_valid_content:
                logger.info("AsyncHtmlLoader failed for all URLs, trying WebBaseLoader individually")
                for url in clean_urls:
                    try:
                        docs = extract_content_with_langchain(url)
                        if docs and not docs[0].page_content.startswith("Error"):
                            contents[url] = docs[0].page_content
                            has_valid_content = True
                        else:
                            logger.warning(f"WebBaseLoader failed for {url}")
                    except Exception as e:
                        logger.error(f"WebBaseLoader error for {url}: {str(e)}")
            
            # If both LangChain methods failed, fall back to BeautifulSoup
            if not has_valid_content:
                logger.info("All LangChain methods failed, falling back to BeautifulSoup")
                for url in clean_urls:
                    content = extract_content_from_url(url)
                    if not content.startswith("Error"):
                        contents[url] = content
                        has_valid_content = True
                    else:
                        logger.warning(f"BeautifulSoup failed for {url}")
            
        except Exception as e:
            logger.error(f"Error processing URLs with LangChain: {str(e)}")
            logger.info("Falling back to BeautifulSoup method")
            # Fall back to traditional method
            for url in clean_urls:
                contents[url] = extract_content_from_url(url)
    else:
        # Use traditional method
        for url in clean_urls:
            contents[url] = extract_content_from_url(url)
    
    # Final check of results
    valid_contents = {}
    for url, content in contents.items():
        if not content.startswith("Error"):
            valid_contents[url] = content
        else:
            logger.warning(f"No valid content for {url}: {content[:100]}...")
    
    if not valid_contents:
        logger.error("Failed to extract valid content from any URL")
    else:
        logger.info(f"Successfully extracted content from {len(valid_contents)} URLs")
    
    return contents

def create_documents_from_contents(contents: Dict[str, str]) -> List[Document]:
    """
    Create LangChain Document objects from extracted contents.
    
    Args:
        contents (Dict[str, str]): Dictionary mapping URLs to their content
        
    Returns:
        List[Document]: List of Document objects for processing
    """
    documents = []
    for url, content in contents.items():
        if not content.startswith("Error"):
            doc = Document(
                page_content=content,
                metadata={"source": url}
            )
            documents.append(doc)
    
    logger.info(f"Created {len(documents)} documents from extracted content")
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks for processing.
    
    Args:
        documents (List[Document]): List of documents to split
        
    Returns:
        List[Document]: List of split documents
    """
    if not documents:
        logger.warning("No documents to split")
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    split_docs = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
    return split_docs 