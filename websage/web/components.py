import streamlit as st
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

def setup_page():
    """
    Set up the page configuration and header.
    """
    # Page configuration
    st.set_page_config(
        page_title="WebSage: Content-Based Q&A Explorer",
        page_icon="🧠",
        layout="wide"
    )

    # App title and description
    st.title("WebSage: Content-Based Q&A Explorer")
    st.markdown("""
    This tool allows you to extract content from web pages and ask questions about that content.
    The answers will be based **only** on the information from the URLs you provide.
    """)

def show_api_configuration(using_azure, azure_deployment, azure_api_version, azure_api_key, azure_endpoint):
    """
    Display Azure OpenAI configuration information.
    """
    with st.expander("API Configuration"):
        if using_azure:
            st.write("**Using Azure OpenAI API**")
            st.write(f"**Chat Model Deployment:** {azure_deployment}")
            st.write(f"**API Version:** {azure_api_version}")
            
            # Add a button to list available deployments
            if st.button("List Available Deployments"):
                try:
                    import openai
                    client = openai.AzureOpenAI(
                        api_key=azure_api_key,
                        api_version=azure_api_version,
                        azure_endpoint=azure_endpoint
                    )
                    deployments = client.deployments.list()
                    deployment_ids = [d.id for d in deployments]
                    st.write("**Available Deployments:**")
                    for deployment_id in deployment_ids:
                        st.write(f"- {deployment_id}")
                        
                    # Check if our specified deployments exist
                    chat_exists = azure_deployment in deployment_ids
                    
                    if not chat_exists:
                        st.warning(f"⚠️ Chat model deployment '{azure_deployment}' not found in available deployments!")
                except Exception as e:
                    st.error(f"Error listing deployments: {str(e)}")
        else:
            st.write("**Using OpenAI API**")
            st.write("Using model: gpt-3.5-turbo")
            
        st.write("**Embeddings**: Using HuggingFace Inference API (BAAI/bge-base-en-v1.5)")

def url_input_section(has_credentials, process_function, callback):
    """
    Display the URL input section.
    
    Args:
        has_credentials: Whether API credentials are available
        process_function: Function to process URLs
        callback: Callback function after processing
    """
    st.header("1. Enter URLs")
    urls_input = st.text_area(
        "Enter one or more URLs (one per line):",
        height=150,
        help="Enter the URLs of web pages you want to extract content from."
    )
    
    # Extraction method options
    st.subheader("Content Extraction Options")
    extraction_method = st.radio(
        "Select extraction method:",
        options=["LangChain (Recommended)", "BeautifulSoup", "Try all methods"],
        index=0,
        help="LangChain works better for complex pages. BeautifulSoup is simpler. 'Try all methods' will attempt all available approaches."
    )
    
    show_debug = st.checkbox("Show debugging information", value=False)
    
    extract_button = st.button("Extract Content", type="primary", disabled=not has_credentials)
    
    if extract_button and urls_input and has_credentials:
        # Clear previous errors
        if 'error_logs' in st.session_state:
            st.session_state.error_logs = []
        
        urls = urls_input.strip().split('\n')
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        debug_area = st.empty()
        
        status_text.text("Processing URLs...")
        
        # Determine which method to use
        use_langchain = extraction_method in ["LangChain (Recommended)", "Try all methods"]
        try_all = extraction_method == "Try all methods"
        
        # Process URLs and extract content
        result = process_function(urls, use_langchain)
        
        if callback(result, progress_bar, status_text):
            st.success(f"✅ Successfully processed URLs. You can now ask questions about the content.")
        else:
            st.error("❌ Could not extract valid content from any of the provided URLs.")
            
            # Try suggesting fixes
            st.info("""
            Possible solutions:
            1. Check if the URLs are correct and accessible
            2. Try a different extraction method
            3. Some websites block scraping - try a different website
            4. Make sure the website has accessible text content
            """)
            
        progress_bar.empty()
        status_text.empty()

    # Display processed URLs
    if 'processed_urls' in st.session_state and st.session_state.processed_urls:
        st.subheader("Processed URLs:")
        for url in st.session_state.processed_urls:
            st.markdown(f"- [{url}]({url})")
    
    # Show debug information if requested
    if show_debug and 'error_logs' in st.session_state and st.session_state.error_logs:
        st.subheader("Debugging Information")
        for i, log in enumerate(st.session_state.error_logs):
            with st.expander(f"Error Log {i+1}"):
                st.code(log)

def qa_section(qa_function):
    """
    Display the question and answer section.
    
    Args:
        qa_function: Function to get answers to questions
    """
    st.header("2. Ask Questions")
    question = st.text_input("Enter your question about the content:", placeholder="What is the main topic discussed?")
    
    ask_button = st.button("Ask", type="primary", key="ask_button", disabled=not st.session_state.get('qa_chain'))
    
    # Display answer if question is asked and QA chain exists
    if ask_button and question and st.session_state.get('qa_chain'):
        with st.spinner("Getting answer..."):
            answer, source_docs = qa_function(st.session_state.qa_chain, question)
            
            st.subheader("Answer:")
            st.markdown(f"{answer}")
            
            # Display sources
            if source_docs:
                st.subheader("Sources:")
                
                # Group source documents by URL
                sources_by_url = {}
                for doc in source_docs:
                    url = doc.metadata.get("source", "Unknown")
                    if url not in sources_by_url:
                        sources_by_url[url] = []
                    sources_by_url[url].append(doc)
                
                # Show sources
                for url, docs in sources_by_url.items():
                    with st.expander(f"Source: {url}"):
                        for i, doc in enumerate(docs):
                            st.markdown(f"**Excerpt {i+1}:**")
                            st.markdown(f"{doc.page_content[:300]}...")
    
    # Display message if no URLs have been processed
    elif ask_button and not st.session_state.get('qa_chain'):
        st.warning("⚠️ Please extract content from URLs first before asking questions.")

def show_footer(using_azure, openai_api_key):
    """
    Display the footer.
    """
    st.markdown("---")
    api_info = "Using Azure OpenAI API" if using_azure else "Using OpenAI API" if openai_api_key else "No API configured"
    st.markdown(f"Built with Streamlit, LangChain, and {api_info}")
    
    # Add custom CSS
    st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
        }
        .css-18e3th9 {
            padding-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True) 