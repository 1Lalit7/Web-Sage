# WebSage: Content-Based Q&A Explorer

A Streamlit web application that allows users to:

1. Enter one or more URLs
2. Extract content from those web pages
3. Ask questions based only on the extracted content
4. Receive concise, accurate answers using only the ingested information

## Features

- **Multiple Content Extraction Methods**: Choose between LangChain's document loaders or BeautifulSoup for content extraction
- **Vector-based Retrieval**: Uses Hugging Face embeddings and FAISS for efficient similarity search
- **Multiple LLM Options**: Compatible with both OpenAI and Azure OpenAI APIs for question answering
- **Source Citations**: Answers include references to the source URLs and content excerpts

## Setup

### 1. Set up a virtual environment (recommended)

#### For Windows:

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# When finished, deactivate with
deactivate
```

#### For macOS/Linux:

```
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# When finished, deactivate with
deactivate
```

### 2. Install dependencies:

To install the package and all dependencies in development mode, run the following command from the `websage` directory:

```bash
# Install the package in development mode
pip install -e .
```

### 3. Create a `.env` file in the root directory and add your API credentials:

For OpenAI:

```
OPENAI_API_KEY=your_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

OR for Azure OpenAI:

```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt_deployment_name
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

**Important Note for Azure OpenAI Users**:

- `AZURE_OPENAI_DEPLOYMENT_NAME` should be your GPT model deployment (e.g., gpt-4o, gpt-3.5-turbo)
- You need both a chat model and an embeddings model deployed in your Azure OpenAI service

**Note**: This application uses Hugging Face embeddings (BAAI/bge-base-en-v1.5) instead of OpenAI embeddings, so you need to provide a Hugging Face API token to use the embedding functionality.

### 4. Run the application:

You can run the application using one of the following methods:

```bash
# Method 1: Using run.py
python run.py

# Method 2: Using streamlit directly
streamlit run app.py

# Method 3: If you installed the package
python -m websage
```

## How to Use

1. Enter one or more URLs (one per line) in the input area
2. Select your preferred content extraction method:
   - **LangChain (Recommended)**: Works better with complex pages
   - **BeautifulSoup**: A simpler alternative that may work better for some sites
   - **Try all methods**: Attempts both approaches sequentially
3. Click "Extract Content" to fetch and process the web pages
4. Ask questions about the content in the question input box
5. View the answer based solely on the extracted content, with source references

## Troubleshooting

If you encounter errors when extracting content:

1. Check if the URLs are correct and accessible
2. Try a different extraction method
3. Some websites block scraping - try with a different website
4. Enable the "Show debugging information" option for detailed error logs

## Project Structure

```
websage/                      # Main package directory
│
├── app.py                    # Streamlit application entry point
│
├── websage/                  # Python package
│   ├── __init__.py
│   │
│   ├── extractors/           # Content extraction modules
│   │   ├── __init__.py
│   │   ├── beautifulsoup_extractor.py
│   │   └── langchain_extractor.py
│   │
│   ├── models/               # Vector store and QA models
│   │   ├── __init__.py
│   │   ├── embeddings.py     # Embeddings implementation
│   │   └── question_answering.py
│   │
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── document_processing.py
│   │
│   └── web/                  # Web/Streamlit interface
│       ├── __init__.py
│       └── components.py     # UI components
│
├── .env                      # Environment variables (not in version control)
├── .env.example              # Example environment file
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Architecture

- **Frontend**: Streamlit
- **Content Extraction**: LangChain document loaders and BeautifulSoup
- **Embeddings**: Hugging Face Inference API (BAAI/bge-base-en-v1.5)
- **Vector Store**: FAISS
- **Question Answering**: LangChain with OpenAI or Azure OpenAI LLMs

## Dependencies

- streamlit: Web application framework
- requests & beautifulsoup4: Web scraping
- langchain, langchain-openai, langchain-community: Document processing and QA chains
- faiss-cpu: Vector similarity search
- python-dotenv: Environment variable management
- html2text: HTML to text conversion
