from setuptools import setup, find_packages

setup(
    name="websage",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.28.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-community>=0.0.10",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "faiss-cpu>=1.7.4",
        "html2text>=2024.2.26"
    ],
    python_requires=">=3.8",
) 