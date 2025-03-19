import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get HuggingFace token
HF_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def create_vector_store(documents: List[Document]):
    """
    Create a vector store from the documents.
    
    Args:
        documents (List[Document]): List of documents to index
        
    Returns:
        FAISS: The vector store containing the indexed documents
    """
    if not HF_token:
        logger.error("No HuggingFace API token available. Cannot create embeddings.")
        raise ValueError("No embeddings service available - please set HUGGINGFACEHUB_API_TOKEN in your .env file")
        
    try:
        logger.info("Creating HuggingFace embeddings")
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=HF_token,
            model_name="BAAI/bge-base-en-v1.5"
        )
        
    except Exception as e:
        logger.error(f"Error creating HuggingFace embeddings: {str(e)}")
        raise ValueError(f"Error creating embeddings: {str(e)}")
    
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store 