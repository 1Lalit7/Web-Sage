from typing import List
from langchain.docstore.document import Document
from langchain_community.document_loaders import WebBaseLoader, AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)

def extract_content_with_langchain(url: str) -> List[Document]:
    """
    Alternative method to extract content using LangChain's WebBaseLoader.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        List[Document]: List of Document objects with the extracted content
    """
    try:
        logger.info(f"Extracting content from {url} using WebBaseLoader")
        # Option 1: Using WebBaseLoader
        loader = WebBaseLoader(
            url,
            header_template={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        )
        docs = loader.load()
        
        if not docs or len(docs[0].page_content.strip()) < 10:
            logger.warning(f"WebBaseLoader extracted no content or too little content from {url}")
            return [Document(
                page_content=f"Error extracting content from {url}: Content was empty or too short",
                metadata={"source": url, "error": "Empty content"}
            )]
        
        logger.info(f"Successfully extracted {len(docs[0].page_content)} characters from {url} with WebBaseLoader")
        return docs
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error extracting content with WebBaseLoader from {url}: {str(e)}\n{error_details}")
        return [Document(
            page_content=f"Error extracting content from {url}: {str(e)}",
            metadata={"source": url, "error": str(e)}
        )]

def extract_content_with_html2text(urls: List[str]) -> List[Document]:
    """
    Extract content from multiple URLs using AsyncHtmlLoader and Html2TextTransformer.
    This method is good for preserving some structure while removing HTML.
    
    Args:
        urls (List[str]): List of URLs to extract content from
        
    Returns:
        List[Document]: List of Document objects with the extracted content
    """
    try:
        logger.info(f"Extracting content from {len(urls)} URLs using AsyncHtmlLoader and Html2TextTransformer")
        # Load HTML - AsyncHtmlLoader doesn't accept headers in constructor
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()
        
        if not docs:
            logger.warning(f"AsyncHtmlLoader failed to extract content from URLs")
            return [Document(
                page_content=f"Error extracting content from URLs: No content extracted",
                metadata={"source": ", ".join(urls), "error": "No content extracted"}
            )]
        
        # Transform HTML to text
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        
        # Validate content
        valid_docs = []
        for doc in docs_transformed:
            if len(doc.page_content.strip()) >= 10:
                valid_docs.append(doc)
            else:
                logger.warning(f"Document from {doc.metadata.get('source', 'unknown')} has insufficient content")
        
        if not valid_docs:
            logger.warning("No valid documents found after transformation")
            return [Document(
                page_content=f"Error extracting content from URLs: All documents had insufficient content",
                metadata={"source": ", ".join(urls), "error": "Insufficient content"}
            )]
        
        logger.info(f"Successfully extracted content from {len(valid_docs)} URLs with AsyncHtmlLoader")
        return valid_docs
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error extracting content with AsyncHtmlLoader: {str(e)}\n{error_details}")
        return [Document(
            page_content=f"Error extracting content from URLs: {str(e)}",
            metadata={"source": ", ".join(urls), "error": str(e)}
        )] 