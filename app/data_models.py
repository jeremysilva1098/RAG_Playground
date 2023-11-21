from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    score: float
    payload: dict
    vector: Optional[List[float]]

class RewriteSearchResults(BaseModel):
    rewrite: str
    results: List[SearchResult]

class RetrievalContext(BaseModel):
    context: str
    steps: dict
    results: List[SearchResult]

class ChatResponse(BaseModel):
    response: str
    steps: dict
    results: List[SearchResult]