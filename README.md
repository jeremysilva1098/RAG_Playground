# RAG_Playground
Playground to test out different RAG techniques

[Demo Video](https://youtu.be/OH6Q7pBJe50?si=zPRBtdu9iZU-43Y2)

## Techniques Included
### Self Query
The LLM is provided information about the metadata associated with the underlying vectorstore (beyond just the vectors themselves), and it generates a query filter to apply to the search inconjunction with the vector similarity search.
This can be useful when a successful answer requires filtering on date ranges or keywords that aren't neccessarily represented explicitly in the content of the vector embedding. 
### Query Rewrite
Instead of directly embedding the user's query and using that as the search vector, we prompt the model to generate a more effective search query and we use that to embed and search the vector db.
This can either be done with or without full context. Without full context we just pass the query to the LLM and have it improve upon it. With full context rewrite, we pass the whole message history to the model
in addition to the most recent query so it can inject additional context into the search query. Full context rewrite is particullarly useful when handling follow up questions that don't actually contain all 
pertinent information in the single most recent query.
### Maximal Marginal Relevance
MMR is a diversity based reranking technique in which the results of a raw vector search are reranked to optimze for diversity. This can be particularly useful if your underlying datastore contains duplicative information
across documents. The reranking is done algorthmically on the resulting vectors which means there is not an additional LLM call, meaning lower cost and lower latency. 
If your underlying datastore does not contain a lot of duplicative information across documents then MMR likely won't be of that much use.
### LLM Based Reranking
A raw vector search is done but before passing the results to the LLM, an additional LLM call is made to filter the results based on relevancy to the query. LLMs are not great at ignoring information so by filtering 
the results in a seperate call we can avoid distracting information. The intuition here is similar to Chain of Thought prompting in which "task" becomes its own LLM call and they build on top of each other, rather than 
trying to provide multiple steps of reasoning in a single LLM call.
### Multi Query Search
Involves using multiple search queries to run vector search and combining the results before passing the context to the model. You could use an LLM to generate multiple search queries or combine things like self-query and full context query rewrite together.
