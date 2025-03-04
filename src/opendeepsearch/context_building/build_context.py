from typing import List, Dict, Optional
from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter


def extract_information(organic_results: List[Dict]) -> List[str]:
    """Extract snippets from organic search results in a formatted string."""
    formatted_results = []
    for item in organic_results:
        if 'snippet' in item:
            result_parts = [
                f"title: {item.get('title', 'N/A')}",
                f"date authored: {item.get('date', 'N/A')}",
                f"link: {item.get('link', 'N/A')}",
                f"snippet: {item['snippet']}"
            ]
            
            if 'html' in item:
                result_parts.append(f"additional information: {item['html']}")
            
            formatted_results.append('\n'.join(result_parts))
    
    return formatted_results

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
    answer_box: Optional[Dict]
) -> List[str]:
    """Extract information from graph and answer box."""
    results = []
    
    if answer_box:
        for key in ['answer', 'snippet']:
            if answer_box.get(key):
                results.append(answer_box[key])
    
    return results

def build_context(
    sources_result: Dict,
) -> List[str]:
    """
    Build context from search results.
    
    Args:
        sources_result: Dictionary containing search results
        
    Returns:
        List of context strings
    """
    try:
        # Build context from different components
        organic_results = extract_information(sources_result.get('organic', []))
        top_stories = extract_top_stories(sources_result.get('topStories'))
        graph_and_answer_box = extract_graph_and_answer_box(
            sources_result.get('answerBox')
        )
        
        final_results = {
            'graph_and_answer_box': graph_and_answer_box,
            'organic_results': organic_results,
            'top_stories': top_stories
        }

        return final_results

    except Exception as e:
        logger.exception(f"An error occurred while building context: {e}")
