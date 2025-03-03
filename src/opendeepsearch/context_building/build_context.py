from typing import List, Dict, Optional
from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter


def extract_snippets(organic_results: List[Dict]) -> List[str]:
    """Extract snippets from organic search results."""
    return [
        f"{item['snippet']} {item.get('date', '')}"
        for item in organic_results 
        if 'snippet' in item
    ]

def process_html_content(organic_results: List[Dict]) -> List[str]:
    """Process and chunk HTML content from search results."""
    html_text = " ".join(item['html'] for item in organic_results if 'html' in item) # The HTML content is processed beforehand and cleaned
    
    if not html_text or len(html_text) <= 200:
        return []
    
    # We're using a recursive character splitter to chunk the HTML content, since the HTML is cleaned we're taking around 300 tokens which is around 1-2 paragraphs
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=175,
        chunk_overlap=50,
        length_function=len
    )
    chunks = splitter.split_text(html_text)
    
    return chunks

def extract_top_stories(top_stories: Optional[List[Dict]]) -> List[str]:
    """Extract titles from top stories."""
    if not top_stories:
        return []
    
    return [
        item['title'] 
        for item in top_stories 
        if 'title' in item
    ]

def extract_graph_and_answer_box(
    graph: Optional[Dict], 
    answer_box: Optional[Dict]
) -> List[str]:
    """Extract information from graph and answer box."""
    results = []
    
    if graph and graph.get('description'):
        results.append(graph['description'])
    
    if answer_box:
        for key in ['answer', 'snippet']:
            if answer_box.get(key):
                results.append(answer_box[key])
    
    return results

def build_context(
    sources_result: Dict,
    query: str,
    pro_mode: bool,
    date_context: str,
    ranking_mode: str = "none",  # Options: "none", "embeddings", "llm"
    rerank_top_res: int = 15
) -> List[str]:
    """
    Build context from search results.
    
    Args:
        sources_result: Dictionary containing search results
        query: Search query string
        pro_mode: Boolean indicating whether to use pro mode
        date_context: Date context string
        ranking_mode: Ranking strategy to use ("none", "embeddings", "llm")
        rerank_top_res: Number of top results to return after reranking
        
    Returns:
        List of context strings
    """
    try:
        # Extract all components
        organic_results = sources_result.get('organic', [])
        combined_list = []
        
        # Build context from different components
        combined_list.extend(extract_snippets(organic_results))
        combined_list.extend(process_html_content(organic_results))
        combined_list.extend(extract_top_stories(sources_result.get('topStories')))
        combined_list.extend(extract_graph_and_answer_box(
            sources_result.get('graph'),
            sources_result.get('answerBox')
        ))

        if pro_mode and ranking_mode != "none":
            full_query = query + date_context
            if ranking_mode == "embeddings":
                return get_reranking_nvidia(
                    combined_list,
                    full_query,
                    top_res=rerank_top_res
                )
        
        return combined_list

    except Exception as e:
        logger.exception(f"An error occurred while building context: {e}")
        return combined_list