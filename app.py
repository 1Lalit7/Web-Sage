import streamlit as st
import os
import logging
from dotenv import load_dotenv
from websage.utils.document_processing import process_urls, create_documents_from_contents, split_documents
from websage.models.embeddings import create_vector_store
from websage.models.question_answering import setup_qa_system, get_answer
from websage.web.components import (
    setup_page, 
    show_api_configuration, 
    url_input_section, 
    qa_section, 
    show_footer
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check API credentials
openai_api_key = os.getenv("OPENAI_API_KEY")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION") 
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Determine which API we're using
using_azure = azure_api_key and azure_endpoint and azure_deployment
has_credentials = openai_api_key or using_azure

# Initialize session state variables
if 'urls_content' not in st.session_state:
    st.session_state.urls_content = {}
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None
if 'processed_urls' not in st.session_state:
    st.session_state.processed_urls = []
if 'error_logs' not in st.session_state:
    st.session_state.error_logs = []

def process_callback(urls_content, progress_bar, status_text):
    """
    Callback function for processing URLs.
    
    Args:
        urls_content: The extracted content from URLs
        progress_bar: Progress bar object
        status_text: Status text object
        
    Returns:
        bool: Whether processing was successful
    """
    # Store the URLs content
    st.session_state.urls_content = urls_content
    
    # Create documents from the content
    documents = create_documents_from_contents(urls_content)
    
    if documents:
        status_text.text("Creating vector store...")
        progress_bar.progress(50)
        
        # Create split documents
        split_docs = split_documents(documents)
        
        # Create vector store and QA chain
        try:
            vector_store = create_vector_store(split_docs)
            st.session_state.qa_chain = setup_qa_system(vector_store)
            
            # Update processed URLs
            st.session_state.processed_urls = list(urls_content.keys())
            
            progress_bar.progress(100)
            status_text.text("Content extracted and indexed successfully!")
            
            # Automatically hide progress indicators after 1 second
            import time
            time.sleep(1)
            
            return True
        except Exception as e:
            logger.error(f"Error creating QA system: {str(e)}")
            if 'error_logs' in st.session_state:
                st.session_state.error_logs.append(str(e))
            return False
    else:
        return False

def main():
    """Main application function"""
    
    # Set up the page
    setup_page()
    
    # Check for API credentials and show warnings if needed
    if not has_credentials:
        if not openai_api_key and not azure_api_key:
            st.warning("⚠️ No API key found. Please add either an OpenAI API key or Azure OpenAI API key to your .env file")
        elif using_azure and not azure_deployment:
            st.warning("⚠️ Azure OpenAI API key found but deployment name is missing. Please add it to your .env file as AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name")
        elif using_azure and not azure_endpoint:
            st.warning("⚠️ Azure OpenAI API key found but endpoint is missing. Please add it to your .env file as AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/")
    elif using_azure:
        # Display Azure OpenAI configuration information
        # show_api_configuration(using_azure, azure_deployment, azure_api_version, azure_api_key, azure_endpoint)
        pass
    # Create two columns for the layout
    col1, col2 = st.columns([1, 1])
    
    # URL Input Section
    with col1:
        url_input_section(has_credentials, process_urls, process_callback)
    
    # Question and Answer Section
    with col2:
        qa_section(get_answer)
    
    # Footer
    show_footer(using_azure, openai_api_key)

if __name__ == "__main__":
    main() 