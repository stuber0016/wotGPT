import getpass
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def rag_init():
    # ENV VARIABLES
    load_dotenv()

    # model load
    if not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

    llm = ChatGroq(groq_api_key=os.environ.get("GROQ_API_KEY"),
                   model_name="llama-3.3-70b-versatile",
                   temperature=0.7
                   )

    # embeddings init
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-mpnet-base-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.environ.get("HFACE_API_KEY"),
    )

    # vector memory init
    vector_store = InMemoryVectorStore(embeddings)

    # document loader
    from os import listdir
    from os.path import isfile, join
    only_files = [f for f in listdir(os.path.abspath("RAG/context_docs/")) if
                  isfile(join(os.path.abspath("RAG/context_docs/"), f))]

    # print(only_files)
    file_paths = [os.path.abspath("RAG/context_docs/" + f) for f in only_files]
    # print(file_paths)

    # file_paths = ["context_docs/context.md", "context_docs/marty_tipy.md", "context_docs/vybaveni.md"]

    all_documents = []
    for file in file_paths:
        with open(file, 'r') as f:
            markdown_string = f.read()
        all_documents.append(markdown_string)

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"), ]

    # text split to chunks
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    processed_docs = []

    for doc in all_documents:
        processed_docs.extend(markdown_splitter.split_text(doc))

    """for idx, chunk in enumerate(processed_docs):
        print(f"Chunk {idx + 1}:\n{chunk}\n")"""

    # store docs to vector
    document_ids = vector_store.add_documents(documents=processed_docs)

    print(document_ids[:3])
    return llm


def ask_model(model, query):
    return model.invoke([HumanMessage(content=query)])
