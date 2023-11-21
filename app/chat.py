import openai
from dotenv import load_dotenv
import os
import json
import requests
from rag import RagClient
from datetime import date , timedelta
from typing import Optional, Tuple, Dict
from data_models import *

load_dotenv()


class ChatSession():
    def __init__(self, system_message) -> None:
        self.key = os.getenv("OPENAI_API_KEY")
        # set the key
        openai.api_key = self.key
        self.news_key = os.getenv("NEWS_API_KEY")
        self.model_name = "gpt-3.5-turbo-16k"
        self.max_context = 16000
        # create the rag client
        self.ragClient = RagClient()
        # initialize the message history with the system message
        self.messages = [{'role': 'system', 'content': system_message}]

    
    def trim_messages(self) -> None:
        # check if we are near the max context
        while len(str(self.messages)) > self.max_context * 0.8:
            # remove the second oldest message
            self.messages.pop(1)
    

    def enhance_query(self, query: str, ragContext: RetrievalContext) -> str:
        return query + "\n---\n" + ragContext.context
    

    def answer_query(self, query: str, rag_strategy: str = "basic",
                     top_n: int = 5, cosine_threshold: float = 0.75) -> str:
        # check if this is not the first query
        if len(self.messages) > 1:
            # trim the messages as needed
            self.trim_messages()
        
        # run rag on the query
        if rag_strategy == "rewrite":
            # run the rewrite search
            ragContext = self.ragClient.query_rewrite_search(text=query, top_n=top_n,
                                                             cosine_threshold=cosine_threshold)
        elif rag_strategy == "rewrite_full_context":
            ragContext = self.ragClient.query_rewrite_full_context_search(messages=self.messages,
                                                                           query=query, top_n=top_n,
                                                                           cosine_threshold=cosine_threshold)
        elif rag_strategy == "llm_rerank":
            ragContext = self.ragClient.llm_rerank_search(query=query, top_n=top_n,
                                                          cosine_threshold=cosine_threshold)
        elif rag_strategy == "self_query":
            ragContext = self.ragClient.self_query_search(query=query, top_n=top_n,
                                                          cosine_threshold=cosine_threshold)
        elif rag_strategy == "multi_query":
            ragContext = self.ragClient.multi_query_search(messages=self.messages, query=query,
                                                           top_n=top_n, cosine_threshold=cosine_threshold)
        elif rag_strategy == "mmr":
            ragContext = self.ragClient.mmr_search(query=query, top_n=top_n,
                                                   cosine_threshold=cosine_threshold)
        else:
            # run the basic search
            ragContext = self.ragClient.basic_search(query, top_n=top_n,
                                                     cosine_threshold=cosine_threshold)

        #print("Context from rag: ", ragContext)
        # enhance the query
        enhanced_query = self.enhance_query(query, ragContext)
        # add the query to the message history
        self.messages.append({'role': 'user', 'content': enhanced_query})
        # add the 
        completionArgs = {
            "model": self.model_name,
            "messages": self.messages
        }
        chat_completion = openai.ChatCompletion.create(**completionArgs)
        #print(json.dumps(chat_completion, indent=4))
        # get the response
        ansDict = chat_completion.choices[0].message
        # add the response to the message history
        self.messages.append(ansDict)
        # create the response object
        return ChatResponse(response=ansDict['content'], steps=ragContext.steps, results=ragContext.results)
    

    def __repr__(self) -> str:
        return "Chat Session Instantiated!"

