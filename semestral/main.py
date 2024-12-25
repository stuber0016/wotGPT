import os

import RAG.rag_backend
from RAG.rag_backend import ask_model
from RAG.rag_backend import rag_init

model = rag_init()

response = ask_model(model, "Where is Paris?")

print(response)
