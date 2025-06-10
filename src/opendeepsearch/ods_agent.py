from typing import Optional, Dict, Any, Literal
from opendeepsearch.serp_search.serp_search import create_search_api, SearchAPI
from opendeepsearch.context_building.process_sources_pro import SourceProcessor
from opendeepsearch.context_building.build_context import build_context
from opendeepsearch.temporal_kg_tool import TemporalKGTool
from litellm import completion, utils
import os
from dotenv import load_dotenv
from opendeepsearch.prompts import SEARCH_SYSTEM_PROMPT, TEMPORAL_REASONING_PROMPT
import asyncio
import nest_asyncio


load_dotenv()

class OpenDeepSearchAgent:
    def __init__(
        self,
        model: Optional[str] = None, #We use LiteLLM to call the model
        system_prompt: Optional[str] = SEARCH_SYSTEM_PROMPT,
        search_provider: Literal["serper", "searxng"] = "serper",
        serper_api_key: Optional[str] = None,
        searxng_instance_url: Optional[str] = None,
        searxng_api_key: Optional[str] = None,
        source_processor_config: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2, # Slight variation while maintaining reliability
        top_p: float = 0.3, # Focus on high-confidence tokens
        reranker: Optional[str] = "None", # Optional reranker identifier
        enable_temporal_kg: bool = False,
        neo4j_uri: Optional[str] = None,
        neo4j_username: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ):
        """
        Initialize an OpenDeepSearch agent that combines web search, content processing, and LLM capabilities.

        This agent performs web searches using either SerperAPI or SearXNG, processes the search results to extract
        relevant information, and uses a language model to generate responses based on the gathered context.

        Args:
            model (str): The identifier for the language model to use (compatible with LiteLLM).
            system_prompt (str, optional): Custom system prompt for the language model. If not provided,
                uses a default prompt that instructs the model to answer based on context.
            search_provider (str, optional): The search provider to use ('serper' or 'searxng'). Default is 'serper'.
            serper_api_key (str, optional): API key for SerperAPI. Required if search_provider is 'serper' and
                SERPER_API_KEY environment variable is not set.
            searxng_instance_url (str, optional): URL of the SearXNG instance. Required if search_provider is 'searxng'
                and SEARXNG_INSTANCE_URL environment variable is not set.
            searxng_api_key (str, optional): API key for SearXNG instance. Optional even if search_provider is 'searxng'.
            source_processor_config (Dict[str, Any], optional): Configuration dictionary for the
                SourceProcessor. Supports the following options:
                - strategies (List[str]): Content extraction strategies to use
                - filter_content (bool): Whether to enable content filtering
                - top_results (int): Number of top results to process
            temperature (float, default=0.2): Controls randomness in model outputs. Lower values make
                the output more focused and deterministic.
            top_p (float, default=0.3): Controls nucleus sampling for model outputs. Lower values make
                the output more focused on high-probability tokens.
            reranker (str, optional): Identifier for the reranker to use. If not provided,
                uses the default reranker from SourceProcessor.
            enable_temporal_kg (bool, default=False): Whether to enable the temporal knowledge graph tool.
            neo4j_uri (str, optional): URI of the Neo4j database. Required if enable_temporal_kg is True.
            neo4j_username (str, optional): Username for the Neo4j database. Required if enable_temporal_kg is True.
            neo4j_password (str, optional): Password for the Neo4j database. Required if enable_temporal_kg is True.
        """
        # Initialize search API based on provider
        self.serp_search = create_search_api(
            search_provider=search_provider,
            serper_api_key=serper_api_key,
            searxng_instance_url=searxng_instance_url,
            searxng_api_key=searxng_api_key
        )

        # Update source_processor_config with reranker if provided
        if source_processor_config is None:
            source_processor_config = {}
        if reranker:
            source_processor_config['reranker'] = reranker

        # Initialize SourceProcessor with provided config or defaults
        self.source_processor = SourceProcessor(**source_processor_config)

        # Initialize LLM settings
        self.model = model if model is not None else os.getenv("LITELLM_SEARCH_MODEL_ID", os.getenv("LITELLM_MODEL_ID", "openrouter/google/gemini-2.0-flash-001"))
        self.temperature = temperature
        self.top_p = top_p
        self.system_prompt = system_prompt

        # Configure LiteLLM with OpenAI base URL if provided
        openai_base_url = os.environ.get("OPENAI_BASE_URL")
        if openai_base_url:
            utils.set_provider_config("openai", {"base_url": openai_base_url})

        # Initialize temporal KG tool if enabled
        self.temporal_tool = None
        if enable_temporal_kg and neo4j_uri and neo4j_username and neo4j_password:
            self.temporal_tool = TemporalKGTool(
                neo4j_uri=neo4j_uri,
                username=neo4j_username,
                password=neo4j_password,
                model_name=self.model
            )
            
            # Update system prompt to include temporal reasoning
            self.system_prompt += "\n\n" + TEMPORAL_REASONING_PROMPT

    async def search_and_build_context(
        self,
        query: str,
        max_sources: int = 2,
        pro_mode: bool = False
    ) -> str:
        """
        Performs a web search and builds a context from the search results.

        This method executes a search query, processes the returned sources, and builds a
        consolidated context, inspired by FreshPrompt in the FreshLLMs paper, that can be used for answering questions.

        Args:
            query (str): The search query to execute.
            max_sources (int, default=2): Maximum number of sources to process. If pro_mode
                is enabled, this overrides the top_results setting in source_processor_config
                when it's smaller.
            pro_mode (bool, default=False): When enabled, performs a deeper search and more
                thorough content processing.

        Returns:
            str: A formatted context string built from the processed search results.
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

    def _should_use_temporal_search(self, query: str) -> bool:
        """Determine if query should use temporal knowledge graph"""
        if not self.temporal_tool:
            return False
            
        # Simple heuristics for temporal queries
        temporal_indicators = [
            'customer', 'timeline', 'what happened', 'between', 'after', 'before',
            'events', 'sequence', 'history', 'journey', 'cust001', 'cust002', 'cust003'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in temporal_indicators)

    async def ask(
        self,
        query: str,
        max_sources: int = 2,
        pro_mode: bool = False,
    ) -> str:
        """
        Searches for information and generates an AI response to the query.
        Now includes temporal knowledge graph capabilities.
        """
        # Check if this should use temporal search
        if self._should_use_temporal_search(query):
            try:
                # Use temporal knowledge graph
                temporal_result = self.temporal_tool.forward(query)
                
                # Prepare messages for the LLM with temporal context
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Temporal Knowledge Graph Result:\n{temporal_result}\n\nQuestion: {query}"}
                ]
                
                # Get completion from LLM
                response = completion(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    top_p=self.top_p
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                # Fallback to web search if temporal search fails
                print(f"Temporal search failed, falling back to web search: {e}")
        
        # Use regular web search (existing logic)
        context = await self.search_and_build_context(query, max_sources, pro_mode)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        response = completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p
        )

        return response.choices[0].message.content

    def ask_sync(
        self,
        query: str,
        max_sources: int = 2,
        pro_mode: bool = False,
    ) -> str:
        """
        Synchronous version of ask() method.
        """
        try:
            # Try getting the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in a running event loop (e.g., Jupyter), use nest_asyncio
                nest_asyncio.apply()
        except RuntimeError:
            # If there's no event loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.ask(query, max_sources, pro_mode))
