import os
import shutil

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma

load_dotenv()

DATA_PATH = "context_docs"
DB_PATH = "chroma"


def main():
    create_rag_context()


def create_rag_context():
    documents = load_documents()
    chunks = split_documents(documents)
    create_chroma_db(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    return loader.load()


def split_documents(documents):
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
    # check for existent database
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    # configure embedding function
    if not os.environ.get("HFACE_API_KEY"):
        raise Exception("HFACE_API_KEY error - creat_RAG")
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-mpnet-base-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.environ.get("HFACE_API_KEY"),
    )

    # create Chroma database

    db = Chroma.from_documents(documents=chunks,
                               embedding=embeddings,
                               persist_directory=DB_PATH)

    print(f"Succesfully created Chroma database of {len(chunks)} chunks")


if __name__ == "__main__":
    main()
