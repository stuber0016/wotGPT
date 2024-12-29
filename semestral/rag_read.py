import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma


def read_rag_context(query):
    load_dotenv()
    db_path = "chroma"
    # configure embedding function - it must be the same function used for creating the rag DB
    if not os.environ.get("HFACE_API_KEY"):
        raise Exception("HFACE_API_KEY error - read_rag_context")
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-mpnet-base-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.environ.get("HFACE_API_KEY"),
    )

    # load db from file
    db = Chroma(persist_directory=db_path, embedding_function=embeddings)

    # search for the context and check its relevance
    context = db.similarity_search_with_score(query, k=3)
    if len(context) == 0 or context[0][1] < 0.5:
        print("No relevant RAG context found score: ", context[0][1])
        context_parsed = "No relevant RAG context found so the response can be inaccurate."

    else:
        print("Found RAG context score: ", context[0][1])
        context_parsed = "\n\n---\n\n".join([page.page_content for page, _score in context])
    header = "Answer the question using information from the context:\n"
    footer = f"\n---\nAnswer the question using information from the context above: {query}"
    return header + context_parsed + footer
