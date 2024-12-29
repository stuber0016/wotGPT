"""
rag_create.py - RAG Context Creation Module

This module is responsible for creating a Retrieval-Augmented Generation (RAG) context
using a Chroma vector database. It processes Markdown documents, splits them into chunks,
and creates embeddings using HuggingFace's sentence transformer model.

Key components:
- Document loading from a specified directory
- Text splitting into manageable chunks
- Embedding generation using HuggingFace's API
- Chroma database creation and persistence

Usage:
Run this script to create or update the RAG context. It will process all .md files
in the DATA_PATH directory and create a new Chroma database in the DB_PATH directory.

Dependencies:
- os: For file and directory operations
- shutil: For directory removal
- dotenv: For loading environment variables
- langchain_huggingface: For HuggingFace embeddings
- langchain.text_splitter: For document splitting
- langchain_community.document_loaders: For loading documents from directory
- langchain_chroma: For Chroma vector database operations
"""
import os
import shutil

from dotenv import load_dotenv
from kubernetes.client import ApiKeyError
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma

load_dotenv()

# paths to input data and output database
DATA_PATH = "context_docs"
DB_PATH = "chroma"


def main():
    """
    Entry point of the script.
    Calls create_rag_context() to initiate the RAG context creation process.
    """
    create_rag_context()


def create_rag_context():
    """
        Executes all parts of the RAG context creation process.

        This function:
        1. Loads documents from the specified directory.
        2. Splits the loaded documents into chunks.
        3. Creates a Chroma database from the document chunks.
        """
    documents = load_documents()
    chunks = split_documents(documents)
    create_chroma_db(chunks)


def load_documents():
    """
        Loads Markdown documents from the DATA_PATH directory.

        Returns:
            list: A list of loaded document objects.
        """
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    return loader.load()


def split_documents(documents):
    """
        Splits the input documents into smaller chunks for processing.

        Args:
            documents (list): A list of document objects to be split.

        Returns:
            list: A list of document chunks.

        Note:
            Uses RecursiveCharacterTextSplitter with a chunk size of 300 and overlap of 100.
        """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )

    chunks = splitter.split_documents(documents)
    print(f"{len(documents)} documents split into {len(chunks)} chunks.")

    return chunks


def create_chroma_db(chunks):
    """
        Creates a Chroma vector database from the provided document chunks.

        Args:
            chunks (list): A list of document chunks to be added to the database.

        This function:
        1. Removes any existing database in DB_PATH.
        2. Configures HuggingFace embeddings for vector representation.
        3. Creates and persists a new Chroma database with the document chunks.

        Raises:
            Exception: If HFACE_API_KEY environment variable is not set.

        Note:
            Requires HFACE_API_KEY environment variable for HuggingFace API access.
        """
    # check for existent database
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    # configure embedding function
    if not os.environ.get("HFACE_API_KEY"):
        raise ApiKeyError("HFACE_API_KEY error - creat_RAG")
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-mpnet-base-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.environ.get("HFACE_API_KEY"),
    )

    # create Chroma database

    Chroma.from_documents(documents=chunks,
                          embedding=embeddings,
                          persist_directory=DB_PATH)

    print(f"Succesfully created Chroma database of {len(chunks)} chunks")


if __name__ == "__main__":
    main()
