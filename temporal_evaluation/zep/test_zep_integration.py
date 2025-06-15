# Create: temporal_evaluation/zep/test_zep_integration.py
from tools.zep_temporal_kg_tool import ZepTemporalKGTool
import os

def test_zep_integration():
    print("🧪 Testing Zep Temporal Knowledge Graph Integration")
    print("=" * 60)
    
    # Initialize tool with your API key
    tool = ZepTemporalKGTool()
    
    # Load SEC data into Zep's knowledge graph
    print("📥 Loading SEC data into Zep...")
    count = tool.load_all_sec_data('../datasets/sec_filings_enhanced.json')
    print(f"✅ Loaded {count} filings into Zep's knowledge graph")
    
    # Test temporal queries that leverage Zep's capabilities
    test_queries = [
        "Show me Apple's recent SEC filings with temporal context",
        "Which companies have irregular filing patterns?",
        "Compare filing frequencies between tech companies over time",
        "Find companies that changed their filing behavior",
        "Show temporal relationships in SEC filing data"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 50)
        result = tool.forward(query)
        print(result)
        print()

if __name__ == "__main__":
    test_zep_integration()