from typing import Optional, Dict, Any
from .serp_search.serp_search import SerperAPI
from .context_building.process_sources_pro import SourceProcessor
from .context_building.build_context import build_context

class OpenDeepSearch:
    def __init__(
        self,
        serper_api_key: Optional[str] = None,
        source_processor_config: Optional[Dict[str, Any]] = None,
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
        """
        # Initialize SerperAPI with optional API key
        self.serp_search = SerperAPI(api_key=serper_api_key) if serper_api_key else SerperAPI()
        
        # Initialize SourceProcessor with provided config or defaults
        processor_config = source_processor_config or {'pro_mode': False}
        self.source_processor = SourceProcessor(**processor_config)

    async def search_and_build_context(
        self,
        query: str,
        max_sources: int = 2
    ) -> str:
        """
        Main function to perform search and build context from results.
        
        Args:
            query (str): User's search query
            max_sources (int): Maximum number of sources to process (overrides top_results
                             from source_processor_config if smaller)
            
        Returns:
            str: Built context from processed sources
        """
        # Get sources from SERP
        sources = self.serp_search.get_sources(query)
        
        # Process sources
        processed_sources = await self.source_processor.process_sources(
            sources,
            max_sources,
            query
        )
        
        # Build and return context
        return build_context(processed_sources)
