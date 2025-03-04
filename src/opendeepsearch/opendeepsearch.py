from typing import Optional, Dict, Any
from opendeepsearch.serp_search.serp_search import SerperAPI
from opendeepsearch.context_building.process_sources_pro import SourceProcessor
from opendeepsearch.context_building.build_context import build_context
from litellm import completion

class OpenDeepSearch:
    def __init__(
        self,
        serper_api_key: Optional[str] = None,
        source_processor_config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize OpenDeepSearch with customizable configurations.
        
        Args:
            serper_api_key (str, optional): API key for SerperAPI
            source_processor_config (dict, optional): Configuration for SourceProcessor
                Example: {
                    'pro_mode': False,  # Enable advanced processing features
                    'strategies': ["no_extraction"],  # Content extraction strategies
                    'filter_content': True,  # Enable content filtering
                    'top_results': 5  # Number of top results to process
                }
            system_prompt (str, optional): System prompt to use for the LLM
            model (str): Model to use for completions (default: "gpt-3.5-turbo")
        """
        # Initialize SerperAPI with optional API key
        self.serp_search = SerperAPI(api_key=serper_api_key) if serper_api_key else SerperAPI()
        
        # Initialize SourceProcessor with provided config or defaults
        processor_config = source_processor_config or {'pro_mode': False}
        self.source_processor = SourceProcessor(**processor_config)
        
        # Initialize LLM settings
        self.model = model
        self.system_prompt = system_prompt or (
            "You are a helpful AI assistant. Use the provided context to answer "
            "questions accurately. If you're unsure or the context doesn't contain "
            "the relevant information, please say so."
        )

    async def search_and_build_context(
        self,
        query: str,
        max_sources: int = 2,
        pro_mode: bool = False
    ) -> str:
        """
        Main function to perform search and build context from results.
        
        Args:
            query (str): User's search query
            max_sources (int): Maximum number of sources to scrape if pro_mode is True (overrides top_results
                             from source_processor_config if smaller)
            pro_mode (bool): enable pro mode/deeper search for this query
        Returns:
            str: Built context from processed sources
        """
        # Get sources from SERP
        sources = self.serp_search.get_sources(query)
        
        # Process sources
        processed_sources = await self.source_processor.process_sources(
            sources,
            max_sources,    
            query,
            pro_mode
        )
        
        # Build and return context
        return build_context(processed_sources)

    async def ask(self, query: str, max_sources: int = 2) -> str:
        """
        Search for information and answer the query using an LLM.
        
        Args:
            query (str): User's question
            max_sources (int): Maximum number of sources to process
            
        Returns:
            str: AI-generated response based on the search results
        """
        # Get context from search results
        context = await self.search_and_build_context(query, max_sources)
        
        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        # Get completion from LLM
        response = completion(
            model=self.model,
            messages=messages
        )
        
        return response.choices[0].message.content
