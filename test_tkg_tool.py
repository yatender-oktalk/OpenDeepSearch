# Create this file: test_tkg_tool.py
from src.opendeepsearch.simplified_temporal_kg_tool import SimplifiedTemporalKGTool
import os

def test_tkg_tool():
    print("🔍 Testing Temporal KG Tool with Complex Queries")
    print("=" * 60)
    
    # Initialize the tool
    tool = SimplifiedTemporalKGTool(
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        username=os.getenv('NEO4J_USERNAME', 'neo4j'), 
        password=os.getenv('NEO4J_PASSWORD', 'maxx3169'),
        model_name="gemini/gemini-1.5-flash"
    )
    
    # Updated complex test queries
    test_queries = [
        "Show me Apple's 10-Q filings",
        "Compare filing frequency between Apple and Meta over the last 2 years",
        "Which companies filed 10-K reports most recently?", 
        "Show me all 8-K filings from 2024 sorted by date",
        "Compare Apple and Microsoft's quarterly filing patterns",
        "Which company has more 10-Q filings: Netflix or Adobe?",
        "Show me the filing timeline for Meta in 2024",
        "List companies that filed both 10-K and 10-Q in 2024",
        "Compare the filing dates of Apple's and Google's most recent 10-K",
        "Which companies have the most consistent quarterly filing schedule?"
    ]
    
    success_count = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/10] Testing: {query}")
        print("-" * 50)
        
        try:
            result = tool.forward(query)
            
            # Check if successful
            if "SEC Filing Results:" in result and ("Company:" in result or "📊" in result):
                print("✅ SUCCESS")
                success_count += 1
                # Show first few lines
                lines = result.split('\n')[:10]
                for line in lines:
                    if line.strip():  # Skip empty lines
                        print(f"  {line}")
                if len(result.split('\n')) > 10:
                    print("  ...")
            else:
                print("❌ FAILED - No proper results")
                print(f"  Response: {result[:150]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 RESULTS: {success_count}/10 queries successful ({success_count*10}%)")
    
    if success_count >= 8:
        print("🎉 Tool is working well! Ready for complex evaluation.")
    elif success_count >= 5:
        print("⚠️  Tool is partially working. Some complex queries need refinement.")
    else:
        print("❌ Tool needs fixes for complex queries.")
    
    print(f"\n🔧 Next steps:")
    if success_count >= 8:
        print("  → Run full evaluation: python temporal_evaluation/sec_filings/run_evaluation_quantitative.py")
    else:
        print("  → Debug failing queries and improve Cypher generation")

if __name__ == "__main__":
    test_tkg_tool()