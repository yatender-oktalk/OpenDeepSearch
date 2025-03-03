import torch
import requests
import json
from typing import List, Dict, Union, Optional

class SemanticSearch:
    """
    A semantic reranking model that uses the Infinity Embedding API for text embeddings.
    
    This class provides methods to rerank documents based on their semantic similarity
    to queries using embeddings from the Infinity API. The API endpoint expects to receive
    text inputs and returns high-dimensional embeddings that capture semantic meaning.
    
    The default model used is 'Alibaba-NLP/gte-Qwen2-7B-instruct', but other models
    available through the Infinity API can be specified.
    
    Attributes:
        embedding_endpoint (str): URL of the Infinity Embedding API endpoint
        model_name (str): Name of the embedding model to use
        
    Example:
        ```python
        reranker = SemanticSearch(
            embedding_endpoint="http://localhost:7997/embeddings",
            model_name="Alibaba-NLP/gte-Qwen2-7B-instruct"
        )
        
        documents = [
            "Munich is in Germany.",
            "The sky is blue."
        ]
        
        results = reranker.rerank(
            query="What color is the sky?",
            documents=documents,
            top_k=1
        )
        ```
    """
    
    def __init__(
        self, 
        embedding_endpoint: str = "http://localhost:7997/embeddings",
        model_name: str = "Alibaba-NLP/gte-Qwen2-7B-instruct",
        instruction_prefix: str = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "
    ):
        """
        Initialize the semantic search engine with Infinity Embedding API settings.
        
        Args:
            embedding_endpoint: URL of the Infinity Embedding API endpoint
            model_name: Name of the embedding model available in Infinity API
            instruction_prefix: Prefix to add to queries for better search relevance
        """
        self.embedding_endpoint = embedding_endpoint
        self.model_name = model_name
        self.instruction_prefix = instruction_prefix

    def _get_embeddings(self, texts: List[str]) -> torch.Tensor:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            torch.Tensor containing the embeddings
        """
        response = requests.post(
            self.embedding_endpoint,
            json={
                "model": self.model_name,
                "input": texts
            }
        )
        
        content_str = response.content.decode('utf-8')
        content_json = json.loads(content_str)
        
        return torch.tensor([item['embedding'] for item in content_json['data']])

    def calculate_scores(
        self,
        queries: List[str],
        documents: List[str],
        normalize: str = "softmax"  # Options: "softmax", "scale", "none"
    ) -> torch.Tensor:
        """
        Calculate similarity scores between queries and documents.
        
        Args:
            queries: List of query strings
            documents: List of document strings
            normalize: Normalization method:
                      - "softmax": Apply softmax normalization (default)
                      - "scale": Scale to 0-100 range
                      - "none": No normalization
            
        Returns:
            torch.Tensor of shape (num_queries, num_documents) containing similarity scores
        """
        # Use the instruction prefix from the instance
        formatted_queries = [self.instruction_prefix + q for q in queries]
        
        # Get embeddings for queries and documents
        query_embeddings = self._get_embeddings(formatted_queries)
        doc_embeddings = self._get_embeddings(documents)
        
        # Calculate similarity scores
        scores = query_embeddings @ doc_embeddings.T
        
        # Apply normalization
        if normalize == "softmax":
            scores = torch.softmax(scores, dim=-1)  # Apply along document dimension
        elif normalize == "scale":
            scores = scores * 100
        elif normalize == "none":
            pass
        else:
            raise ValueError(f"Unknown normalization method: {normalize}")
            
        return scores

    def rerank(
        self,
        query: Union[str, List[str]],
        documents: List[str],
        top_k: int = 5,
        normalize: str = "softmax"
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Rerank documents based on their semantic similarity to the query.
        
        Args:
            query: Query string or list of query strings
            documents: List of documents to rerank
            top_k: Number of top results to return per query
            normalize: Normalization method for scores ("softmax", "scale", or "none")
            
        Returns:
            List of dicts containing reranked documents and their scores.
            For single query: [{"document": str, "score": float}, ...]
            For multiple queries: [[{"document": str, "score": float}, ...], ...]
        """
        # Convert single query to list for consistent handling
        queries = [query] if isinstance(query, str) else query
        
        # Calculate similarity scores
        scores = self.calculate_scores(queries, documents, normalize=normalize)
        
        # Get top-k results for each query
        results = []
        for query_scores in scores:
            # Get top-k indices
            top_indices = torch.topk(query_scores, min(top_k, len(documents)), dim=0)
            
            # Build results for this query
            query_results = [
                {
                    "document": documents[idx.item()],
                    "score": score.item()
                }
                for score, idx in zip(top_indices.values, top_indices.indices)
            ]
            results.append(query_results)
        
        # Return single list for single query, list of lists for multiple queries
        return results[0] if isinstance(query, str) else results
