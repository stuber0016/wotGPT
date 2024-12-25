import os

import RAG.rag_backend as RAG

model = RAG.Model()

responses = []
responses2 = []
responses.append(model.query("Hi I am Sam", "Sam"))
responses.append(model.query("Do you know my name?", "Sam"))
responses.append(model.query("Can you tell me what is a good equipment for obj. 277?", "Sam"))
responses2.append(model.query("Do you know my name?", "Alex"))
responses2.append(model.query("Call me Alex.", "Alex"))
responses2.append(model.query("Why do I suck at world of tanks?.", "Alex"))


def printer(to_print):
    for i in range(len(to_print)):
        print(i, ". ", to_print[i])
    print("\n----\n")


printer(responses)
printer(responses2)
