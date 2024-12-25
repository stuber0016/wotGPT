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

from os import listdir
from os.path import isfile, join


class Model:
    def __init__(self):
        load_dotenv()

        # TODO RAG database

        # MODEl
        if not os.environ.get("GROQ_API_KEY"):
            raise Exception("GROQ_API_KEY error")
        self.llm = ChatGroq(groq_api_key=os.environ.get("GROQ_API_KEY"),
                            model_name="llama-3.3-70b-versatile",
                            temperature=0.7
                            )

        # EMBEDDINGS
        if not os.environ.get("HFACE_API_KEY"):
            raise Exception("HFACE_API_KEY error")
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-mpnet-base-v2",
            task="feature-extraction",
            huggingfacehub_api_token=os.environ.get("HFACE_API_KEY"),
        )
        self.vector_store = InMemoryVectorStore(self.embeddings)

        # DOCS for RAG
        only_files = [f for f in listdir(os.path.abspath("RAG/context_docs/")) if
                      isfile(join(os.path.abspath("RAG/context_docs/"), f))]

        file_paths = [os.path.abspath("RAG/context_docs/" + f) for f in only_files]

        self.all_documents = []
        for file in file_paths:
            with open(file, 'r') as f:
                markdown_string = f.read()
            self.all_documents.append(markdown_string)

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"), ]

        # text split to chunks
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

        self.processed_docs = []

        for doc in self.all_documents:
            self.processed_docs.extend(markdown_splitter.split_text(doc))

        """for idx, chunk in enumerate(processed_docs):
            print(f"Chunk {idx + 1}:\n{chunk}\n")"""

        # store docs to vector
        self.document_ids = self.vector_store.add_documents(documents=self.processed_docs)

        # user context
        self.user_context = {}

    def query(self, query, user):
        if user not in self.user_context:
            self.user_context[user] = []
            self.user_context[user].append(
                SystemMessage("You are helpful assistant that will help player to be better at game World of Tanks"))
            self.user_context[user].append(HumanMessage(query))

        else:
            self.user_context[user].append(HumanMessage(query))

        response = self.llm.invoke(self.user_context[user])
        self.user_context[user].append(AIMessage(response.content))
        return response.content
