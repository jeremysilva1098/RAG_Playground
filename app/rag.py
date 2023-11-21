import requests
import json
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import openai
import os
from typing import List
from sklearn.metrics.pairwise import cosine_distances
from data_models import SearchResult, RewriteSearchResults, RetrievalContext

load_dotenv()

class RagClient:
    def __init__(self, db_url: str = "http://localhost",
                db_port: int = 6333,
                collection_name: str = "wiki_movies") -> None:
        # instate the db client
        self.dbClient = QdrantClient(url=db_url, port=db_port)
        self.collection = collection_name
        self.dbUrl = db_url
        self.dbPort = db_port
        # instantiate the openai client, will use for embeddings
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.embed_model = "text-embedding-ada-002"
        self.chat_model = "gpt-3.5-turbo-1106"
        self.max_context = 16000
        # read in the query rewrite prompt
        with open("./prompts/query_rewrite.txt", "r") as f:
            self.query_rewrite_prompt = f.read()
        # read in the query rewrite full context search prompt
        with open("./prompts/query_rewrite_full_context.txt", "r") as f:
            self.query_rewrite_full_context_prompt = f.read()
        # read in the llm reranking prompt
        with open("./prompts/llm_rerank.txt", "r") as f:
            self.llm_rerank_prompt = f.read()
        # read in the self query filter
        with open("./prompts/self_query.txt", "r") as f:
            self.self_query_prompt = f.read()
        # read in the multi query search
        with open("./prompts/multi_query.txt", "r") as f:
            self.multi_query_prompt = f.read()
    

    def embed_text(self, text: str) -> list:
        response = openai.Embedding.create(
            input = text,
            model = self.embed_model
        )
        return response["data"][0]["embedding"]
    

    def chat_completion(self, text: str, sys_msg: str = None, json_mode: bool = False) -> str:
        # build the messages input
        messages = []
        # add a system message if it exists
        if sys_msg:
            messages.append({"role": "system", "content": sys_msg})
        messages.append({"role": "user", "content": text})
        params = {'model': self.chat_model,
                  'messages': messages}
        if json_mode:
            params['response_format'] = {"type": "json_object"}
        # send to the model
        res = openai.ChatCompletion.create(**params)
        # extract the answer
        return res.choices[0].message['content']


    def search(self, text: str, top_n: int = 5, 
                     cosine_threshold: int = 0.75,
                     return_vector: bool = False) -> List[SearchResult]:
        try:
            print("Searching for: ", text)
            # create the embedding
            embedding = self.embed_text(text)
            # search the db
            searchRes = self.dbClient.search(
                collection_name=self.collection,
                query_vector=embedding,
                limit=top_n,
                with_vectors=return_vector
            )

            resParsed = []
            for idx, point in enumerate(searchRes):
                if return_vector:
                    subRes = SearchResult(score=point.score, payload=point.payload, vector=point.vector)
                else:
                    subRes = SearchResult(score=point.score, payload=point.payload, vector=None)
                resParsed.append(subRes)

            return resParsed
        except Exception as e:
            print(f"Error occurred during search: {e}")
            return []
    

    def build_context_str(self, searchRes: List[SearchResult]) -> str:
        context_str = ""
        for res in searchRes:
            edited_payload = res.payload
            # remove url from payload
            del edited_payload["url"]
            context_str += str(edited_payload)
            context_str += "\n---\n"
        return context_str
    

    def basic_search(self, query: str, top_n: int = 5,
                     cosine_threshold: int = 0.75) -> RetrievalContext:
        # search the db
        searchRes = self.search(query, top_n, cosine_threshold)
        # create the context
        context = self.build_context_str(searchRes)

        steps = {"basic_search": query}
        
        return RetrievalContext(context=context, steps=steps, results=searchRes)
    

    def parse_rewrite_res(self, rewrite_res: RewriteSearchResults) -> RetrievalContext:
        # take a rewrite search result and parse it into a retrieval context
        # get the write steps
        steps = {"rewriten_query": rewrite_res.rewrite}
        # get the search results
        context = self.build_context_str(rewrite_res.results)
        '''context = ""
        for search_res in rewrite_res.results:
            context += str(search_res.payload)
            context += "\n---\n"'''
        return RetrievalContext(context=context, steps=steps, results=rewrite_res.results)


    def query_rewrite_search(self, text: str, top_n: int = 5,
                             cosine_threshold: int = 0.75) -> RetrievalContext:
        print("Original query: ", text)
        # get the rewrite
        rewrite_prompt = self.query_rewrite_prompt.format(text)
        # get the rewrite
        rewrite = self.chat_completion(rewrite_prompt).replace('"', '')
        print("Rewriten Query: ", rewrite)
        # search the db
        searchRes = self.search(rewrite, top_n, cosine_threshold)
        rewrite_res = RewriteSearchResults(rewrite=rewrite, results=searchRes)
        return self.parse_rewrite_res(rewrite_res)
    

    def query_rewrite_full_context_search(self, messages: dict, query: str, top_n: int = 5,
                                          cosine_threshold: int = 0.75) -> RetrievalContext:
        # get the rewrite
        rewrite_prompt = self.query_rewrite_full_context_prompt.format(str(messages), query)
        # get the rewrite
        rewrite = self.chat_completion(rewrite_prompt).replace('"', '')
        print("Rewriten Query: ", rewrite)
        # search the db
        searchRes = self.search(rewrite, top_n, cosine_threshold)
        rewrite_res = RewriteSearchResults(rewrite=rewrite, results=searchRes)
        return self.parse_rewrite_res(rewrite_res)
    
    
    def multi_query_search(self, messages: dict, query: str, top_n: int = 5,
                           cosine_threshold: float = 0.75) -> RetrievalContext:
        # get the multiple queries
        multi_query_prompt = self.multi_query_prompt.format(chat_history=str(messages), query=query)
        queries = json.loads(self.chat_completion(multi_query_prompt))
        print("Muli Query Generation: ", queries)
        # search the db
        subQueryLimit = top_n // len(queries)
        searchRes = []
        for query in queries:
            subSearcRes = self.search(query, subQueryLimit, cosine_threshold)
            searchRes.extend(subSearcRes)
        # build the context
        context = self.build_context_str(searchRes)
        steps = {"multi_query": queries}
        return RetrievalContext(context=context, steps=steps, results=searchRes)

    
    def llm_rerank_search(self, query: str, top_n: int = 5,
                          cosine_threshold: float = 0.75) -> RetrievalContext:
        # perform basic search
        searchRes = self.search(query)
        # rerank
        rerank_prompt = self.llm_rerank_prompt.format(query=query, results=searchRes)
        # get the reranked titles
        relevant_results = json.loads(self.chat_completion(rerank_prompt))
        print("Relevant results: ", relevant_results)
        # filter the search results for the titles
        rerankedSearchRes = []
        origTitles = []
        for res in searchRes:
            origTitles.append(res.payload["title"])
            if res.payload["title"] in relevant_results:
                rerankedSearchRes.append(res)
        # get the original context
        steps = {"llm_rerank": {"original": origTitles, "reranked": relevant_results}}
        context = self.build_context_str(rerankedSearchRes)
        return RetrievalContext(context=context, steps=steps, results=rerankedSearchRes)
    

    def validate_filter(self, filter: dict) -> bool:
        '''valid filter looks like this
        {
            "must": [
                {
                    "key": "genere",
                    "match": {
                        "text": "western"
                    }
                },
                {
                    "key": "release_year",
                    "range": {
                        "gt": 1900,
                        "lt": 1970
                    }
                },
                {
                    "key": "cast",
                    "match": {
                        "any": [
                            "John Wayne",
                            "Clint Eastwood"
                        ]
                    }
                }
            ]
        }
        '''
        # check if the filter is valid
        valid_keys = ["must", "must_not", "should"]
        for key in filter.keys():
            if key not in valid_keys:
                return False
        # check if the values are valid
        for v in filter.values():
            if type(v) != list:
                return False
            for sub_v in v:
                if type(sub_v) != dict:
                    return False
        return True


    def self_query_search(self, query: str, top_n: int = 5,
                          cosine_threshold: float = 0.75) -> None:
        # create the filter
        sq_prompt = self.self_query_prompt.format(query=query)
        filter = json.loads(self.chat_completion(sq_prompt, json_mode=True))
        print(f"Searching for {query} with the following filters:", json.dumps(filter, indent=4))
        
        # validate the filter
        if not self.validate_filter(filter):
            raise Exception("Invalid filter")
    
        # query the db via rest API in order to use the filter object
        input_params = {
            "vector": self.embed_text(query),
            "limit": top_n,
            "filters": filter,
            "with_payload": True
        }
        url = self.dbUrl + ":" + str(self.dbPort) + "/collections/" + self.collection + "/points/search"
        res = requests.post(url, json=input_params)
        print(res.status_code)
        # get the search results
        searchRes = res.json()['result']
        resParsed = []
        for idx, point in enumerate(searchRes):
            subRes = SearchResult(score=point['score'], payload=point['payload'])
            resParsed.append(subRes)
        # build a context string
        context = self.build_context_str(resParsed)
        steps = {"self_query_filter": filter}
        return RetrievalContext(context=context, steps=steps, results=resParsed)
    

    def compute_mmr(self, searchRes: List[SearchResult], top_n: float = 0.5) -> List[SearchResult]:
        # set lambda param to 0.5 for a balance between relevance and diversity
        lambdaParam = 0.5
        def diversity_func(vecA, vecB):
            return cosine_distances([vecA], [vecB])[0][0]
        
        # keep track of the vectors that have been selected and those remaining to be processed
        selected_results = []
        remaining_results = searchRes.copy()

        for _ in range(top_n):
            mmr_scores = []
            # calculate the MMR score for each vector
            for res in remaining_results:
                rel_score = res.score
                if not selected_results:
                    diversity_score = 0
                else:
                    diversity_score = max([diversity_func(res.vector, selected_results[i].vector) for i in range(len(selected_results))])
                mmr_score = lambdaParam * rel_score - (1 - lambdaParam) * diversity_score
                mmr_scores.append(mmr_score)
            # select the vector with the highest mmr score
            if not mmr_scores:
                break
            max_idx = mmr_scores.index(max(mmr_scores))
            # update the list of selected and remaining vectors
            selected_results.append(remaining_results.pop(max_idx))

        return selected_results


    def mmr_search(self, query: str, top_n: int = 5, cosine_threshold: float = 0.75) -> RetrievalContext:
        # perform basic search with vectors returned
        # double top n on original search then use MMR to reduce to requested top n
        searchRes = self.search(text=query, return_vector=True,
                                top_n=top_n*2, cosine_threshold=cosine_threshold)
        # get the orginal titles
        orig_titles = [res.payload['title'] for res in searchRes]
        # get the mmr results
        mmr_results = self.compute_mmr(searchRes, top_n=top_n)
        # get the mmr titles
        mmr_titles = [res.payload['title'] for res in mmr_results]

        # format the steps with the titles pre and post mmr
        steps = {"mmr_ranking": {"original": orig_titles, "mmr": mmr_titles}}

        # build the context
        context = self.build_context_str(mmr_results)
        return RetrievalContext(context=context, steps=steps, results=mmr_results)


        



        




