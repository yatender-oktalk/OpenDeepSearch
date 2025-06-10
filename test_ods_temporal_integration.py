import sys
import os
sys.path.append('src')

from opendeepsearch import OpenDeepSearchTool

# Test ODS with temporal capabilities
def test_ods_temporal():
    # Create ODS with temporal KG enabled
    search_agent = OpenDeepSearchTool(
        model_name="openrouter/google/gemini-2.0-flash-001",
        reranker="jina",
        enable_temporal_kg=True,
        neo4j_config={
            "uri": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "maxx3169"
        }
    )
    
    # Setup the tool
    search_agent.setup()
    
    # Test temporal queries
    temporal_queries = [
        "What happened to Customer CUST001?",
        "Show me the timeline for Customer CUST003",
        "What is machine learning?",  # This should use web search
    ]
    
    print("🔍 Testing ODS with Temporal Knowledge Graph Integration:")
    print("=" * 60)
    
    for query in temporal_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        try:
            result = search_agent.forward(query)
            print(f"📊 Result: {result}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print()

if __name__ == "__main__":
    test_ods_temporal() 