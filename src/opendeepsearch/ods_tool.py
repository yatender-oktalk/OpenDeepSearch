from smolagents import Tool
from opendeepsearch.ods_agent import OpenDeepSearchAgent
import wolframalpha
import json
import os

class OpenDeepSearchTool(Tool):
    name = "web_search"
    description = """
    Performs web search based on your query (think a Google search) then returns the final answer that is processed by an llm."""
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to perform",
        },
    }
    output_type = "string"

    def __init__(self, model_name: str, reranker: str = "infinity"):
        super().__init__()
        self.search_model_name = model_name #LiteLLM model name
        self.reranker = reranker

    def forward(self, query: str):
        answer = self.search_tool.ask_sync(query, max_sources=2, pro_mode=True)
        return answer

    def setup(self):
        self.search_tool = OpenDeepSearchAgent(
            self.search_model_name,
            reranker=self.reranker
        )

class WolframAlphaTool(Tool):
    name = "wolfram_alpha"
    description = """
    Performs computational, mathematical, and factual queries using Wolfram Alpha's computational knowledge engine.
    """
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to send to Wolfram Alpha",
        },
    }
    output_type = "string"
    
    def __init__(self, app_id: str, cache_file: str = "wolfram_cache.json"):
        super().__init__()
        self.app_id = app_id
        self.cache_file = cache_file
        self.cache = {}
        
    def forward(self, query: str):
        # Check if this query is already in the cache
        if query in self.cache:
            return self.cache[query]
            
        # Initialize the Wolfram Alpha client
        self.wolfram_client = wolframalpha.Client(self.app_id)
        
        try:
            # Send the query to Wolfram Alpha
            res = self.wolfram_client.query(query)
            
            # Process the results
            results = []
            for pod in res.pods:
                if pod.title:
                    for subpod in pod.subpods:
                        if subpod.plaintext:
                            results.append({
                                'title': pod.title,
                                'result': subpod.plaintext
                            })
                            
            # Convert results to a JSON-serializable format
            formatted_result = {
                'queryresult': {
                    'success': bool(results),
                    'inputstring': query,
                    'pods': [
                        {
                            'title': result['title'], 
                            'subpods': [{'title': '', 'plaintext': result['result']}]
                        } for result in results
                    ]
                }
            }
            
            # Initialize final_result with a default value
            final_result = "No result found."
            
            # Extract the pods from the query result
            pods = formatted_result.get("queryresult", {}).get("pods", [])
            
            # Loop through pods to find the "Result" title
            for pod in pods:
                if pod.get("title") == "Result":
                    # Extract and return the plaintext from the subpods
                    subpods = pod.get("subpods", [])
                    if subpods:
                        final_result = subpods[0].get("plaintext", "").strip()
                        break
            
            # If no "Result" pod was found, use the first available result
            if final_result == "No result found." and results:
                final_result = results[0]['result']
                
            # Cache the result
            self.cache[query] = final_result
            self.save_search_cache()
            
            print(f"QUERY: {query}\n\nRESULT: {final_result}")
            return final_result
            
        except Exception as e:
            error_message = f"Error querying Wolfram Alpha: {str(e)}"
            print(error_message)
            return error_message
    
    def setup(self):
        # Load the cache if it exists
        self.load_search_cache()
    
    def load_search_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}
        else:
            self.cache = {}
    
    def save_search_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)