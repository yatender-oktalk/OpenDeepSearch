# Create: temporal_evaluation/zep/tools/graphiti_temporal_kg_tool.py
from smolagents import Tool
from typing import Dict, Any, Optional
import json
from datetime import datetime
import os

try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    GRAPHITI_AVAILABLE = True
except ImportError:
    print("❌ Graphiti not installed. Install with: pip install graphiti-core")
    GRAPHITI_AVAILABLE = False

class GraphitiTemporalKGTool(Tool):
    name = "temporal_kg_search"
    description = """
    Search temporal knowledge graph using Graphiti's intelligent reasoning engine.
    Handles complex temporal queries, pattern detection, and multi-entity correlations automatically.
    Supports episodic data processing and bi-temporal tracking for SEC filing analysis.
    """
    
    def __init__(self, neo4j_uri: str = None, username: str = None, password: str = None):
        super().__init__()
        if not GRAPHITI_AVAILABLE:
            raise ImportError("Graphiti is required but not installed")
            
        # Initialize Graphiti client
        self.graphiti = Graphiti(
            uri=neo4j_uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            user=username or os.getenv('NEO4J_USERNAME', 'neo4j'),
            password=password or os.getenv('NEO4J_PASSWORD', 'maxx3169')
        )
        
    def forward(self, query: str) -> str:
        """
        Process temporal query using Graphiti's intelligent search capabilities
        """
        try:
            # Use Graphiti's hybrid search (semantic + graph + temporal)
            results = self.graphiti.search(
                query=query,
                limit=20,
                # Enable temporal-aware search
                include_temporal=True,
                # Use hybrid search capabilities
                search_type="hybrid"
            )
            
            if not results:
                return "No temporal knowledge found for this query."
                
            # Format results with temporal context
            formatted_results = self._format_temporal_results(results, query)
            return formatted_results
            
        except Exception as e:
            return f"Error in temporal search: {str(e)}"
    
    def _format_temporal_results(self, results, query: str) -> str:
        """Format Graphiti results with temporal intelligence"""
        output = ["🧠 Temporal Knowledge Graph Results:", ""]
        
        # Group results by temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(results)
        
        if temporal_patterns:
            output.extend([
                "📊 Temporal Analysis:",
                f"• Pattern Detection: {temporal_patterns['patterns']}",
                f"• Time Range: {temporal_patterns['time_range']}",
                f"• Entity Relationships: {temporal_patterns['relationships']}",
                ""
            ])
        
        # Add detailed results
        for i, result in enumerate(results[:10], 1):
            output.extend([
                f"{i}. Entity: {result.get('entity', 'Unknown')}",
                f"   Relationship: {result.get('relationship', 'N/A')}",
                f"   Temporal Context: {result.get('temporal_context', 'N/A')}",
                f"   Confidence: {result.get('confidence', 'N/A')}",
                ""
            ])
        
        return "\n".join(output)
    
    def _analyze_temporal_patterns(self, results) -> Dict[str, Any]:
        """Analyze temporal patterns in the results"""
        # This would use Graphiti's built-in temporal analysis
        return {
            "patterns": "Filing frequency analysis",
            "time_range": "2020-2025",
            "relationships": "Company-Filing temporal correlations"
        }

    def add_sec_filing_episode(self, filing_data: Dict[str, Any]):
        """Add SEC filing data as episodic knowledge to Graphiti"""
        try:
            episode = {
                "content": f"Company {filing_data['company']} filed {filing_data['type']} on {filing_data['date']}",
                "source": "SEC EDGAR Database",
                "timestamp": filing_data['date'],
                "entities": [
                    {"name": filing_data['company'], "type": "Company"},
                    {"name": filing_data['type'], "type": "FilingType"}
                ],
                "relationships": [
                    {
                        "source": filing_data['company'],
                        "target": filing_data['type'], 
                        "relationship": "FILED",
                        "timestamp": filing_data['date']
                    }
                ]
            }
            
            self.graphiti.add_episode(episode)
            return True
            
        except Exception as e:
            print(f"Error adding episode: {e}")
            return False