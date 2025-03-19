import os
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API credentials
openai_api_key = os.getenv("OPENAI_API_KEY")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION") 
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Check if using Azure OpenAI
using_azure = azure_api_key and azure_endpoint and azure_deployment

def setup_qa_system(vector_store):
    """
    Set up the Question Answering system.
    
    Args:
        vector_store: The vector store containing indexed documents
        
    Returns:
        RetrievalQA: The QA chain
    """
    if using_azure:
        logger.info(f"Setting up Azure OpenAI LLM with deployment: {azure_deployment}")
        llm = AzureChatOpenAI(
            model=azure_deployment,
            openai_api_version=azure_api_version,
            azure_endpoint=azure_endpoint,
            openai_api_key=azure_api_key,
            temperature=0
        )
    else:
        logger.info("Setting up OpenAI LLM")
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", 
            temperature=0,
            openai_api_key=openai_api_key
        )
    
    template = """
    You are a helpful assistant that answers questions based ONLY on the provided context.
    If the answer cannot be found in the context, say "I don't have enough information to answer this question based on the provided content."
    Do not use any prior knowledge or information not contained in the context.
    
    Context: {context}
    
    Question: {question}
    
    Answer:
    """
    
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=True,
    )
    
    return qa_chain

def get_answer(qa_chain, question: str):
    """
    Get an answer to a question using the QA chain.
    
    Args:
        qa_chain: The QA chain
        question (str): The question to answer
        
    Returns:
        tuple: (answer, source_documents)
    """
    result = qa_chain({"query": question})
    return result["result"], result["source_documents"] 