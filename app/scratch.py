from rag import RagClient
import json

rag = RagClient()

text = "I am looking for john wayne movies"
#text = "I am looking for western movies but I am only interested in the ones with Clint Eastwood"

print(rag.self_query_search(text))
