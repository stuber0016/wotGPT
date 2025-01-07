"""
rag_read.py - RAG Context Retrieval Module

This module provides functionality to retrieve relevant context from a pre-built
Retrieval-Augmented Generation (RAG) database for given queries.

Note: Requires a pre-existing Chroma database and HFACE_API_KEY environment variable.

Dependencies:
- os: For environment variable access
- dotenv: For loading environment variables
- langchain_huggingface: For HuggingFace embeddings
- langchain_chroma: For interacting with the Chroma database
"""
import os
from dotenv import load_dotenv
from kubernetes.client import ApiKeyError
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma
from huggingface_hub.errors import BadRequestError

load_dotenv()

FOUND_CONTEXT = 1
NO_CONTEXT = 0
OTHER_ERROR = 2

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "chroma")


def read_rag_context(query):
    """
       Retrieves relevant context for a given query using a Chroma vector database.

       This function loads environment variables, configures HuggingFace embeddings,
       and searches a pre-existing Chroma database for context relevant to the input query.

       Args:
           query (str): The input query to find relevant context for.

       Returns:
           str: A formatted string containing:
                - A header instructing to use the context
                - The retrieved context (or a message if no relevant context was found)
                - A footer repeating the instruction and the original query

       Raises:
           Exception: If the HFACE_API_KEY environment variable is not set.

       Note:
           - Requires a pre-existing Chroma database in the "chroma" directory.
           - Uses HuggingFace's sentence-transformers model for embeddings.
           - Considers context relevant if the similarity score is >= 0.5.
           - Retrieves up to 3 most relevant context pieces.
       """
    # configure embedding function - it must be the same function used for creating the rag DB
    if not os.environ.get("HFACE_API_KEY"):
        return OTHER_ERROR, "RAG context database error. Please try again later."

    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-mpnet-base-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.environ.get("HFACE_API_KEY"),
    )

    # load db from file
    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    # search for the context and check its relevance
    try:
        context = db.similarity_search_with_score(query, k=3)
    except BadRequestError as e:
        print(e)
        print("RAG READ: Probably embeddings API key error")
        return OTHER_ERROR, "RAG context database error. Please try again later."

    result = NO_CONTEXT

    if len(context) == 0:
        print("No relevant RAG context found")
        context_parsed = "No relevant RAG context found so the response can be inaccurate."

    elif context[0][1] < 0.5:
        print("No relevant RAG context found score: ", context[0][1])
        context_parsed = "No relevant RAG context found so the response can be inaccurate."

    else:
        print("Found RAG context score: ", context[0][1])
        context_parsed = "\n\n---\n\n".join([page.page_content for page, _score in context])
        result = FOUND_CONTEXT

    header = "Answer the question using information from the context:\n"
    footer = f"\n---\nAnswer the question using information from the context above: {query}"
    return result, header + context_parsed + footer
