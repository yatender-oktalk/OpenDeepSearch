import sys
import os
import time

# Add the tools directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.join(current_dir, 'tools')
sys.path.insert(0, tools_dir)

from zep_temporal_kg_tool import ZepTemporalKGTool

def test_basic_zep():
    """Test if Zep can extract ANY entities properly"""
    print("🧪 Basic Zep Entity Extraction Test")
    
    tool = ZepTemporalKGTool()
    
    # Super simple, clear data
    simple_facts = [
        "Apple Inc. is a technology company.",
        "Apple filed a 10-K report on March 15, 2024.",
        "Microsoft Corporation filed a 10-Q report on January 20, 2024.",
        "Google filed an 8-K report on February 10, 2024."
    ]
    
    print("📝 Adding simple facts to Zep...")
    for fact in simple_facts:
        tool.client.graph.add(
            user_id=tool.user_id,
            type="text", 
            data=fact
        )
    
    print("⏳ Waiting for processing...")
    time.sleep(10)
    
    # Test basic queries
    queries = [
        "What companies are in the knowledge graph?",
        "Show me Apple's information",
        "What filings did Microsoft make?"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        result = tool.forward(query)
        print(f"📝 Result: {result[:300]}...")
        
        # Better entity recognition check based on query intent
        if "companies" in query.lower():
            # For "what companies" query, check if multiple companies mentioned
            companies_found = sum(1 for company in ["Apple", "Microsoft", "Google"] if company in result)
            if companies_found >= 2:
                print("✅ Excellent entity recognition - multiple companies found!")
            elif companies_found == 1:
                print("⚠️ Partial entity recognition - only one company found")
            else:
                print("❌ Poor entity recognition - no companies found")
            
        elif "apple" in query.lower():
            if "Apple" in result:
                if "Microsoft" in result:
                    print("⚠️ Mixed results - Apple found but also other companies")
                else:
                    print("✅ Excellent entity recognition - Apple-specific results!")
            else:
                print("❌ Poor entity recognition - Apple not found")
            
        elif "microsoft" in query.lower():
            if "Microsoft" in result:
                if "Apple" in result:
                    print("⚠️ Mixed results - Microsoft found but also other companies")
                else:
                    print("✅ Excellent entity recognition - Microsoft-specific results!")
            else:
                print("❌ Poor entity recognition - Microsoft not found")
        
        # Check for temporal intelligence indicators
        temporal_indicators = ["2024", "filed", "Valid From", "Temporal Fact"]
        temporal_score = sum(1 for indicator in temporal_indicators if indicator in result)
        
        if temporal_score >= 3:
            print("✅ Strong temporal intelligence detected!")
        elif temporal_score >= 2:
            print("⚠️ Some temporal intelligence detected")
        else:
            print("❌ Limited temporal intelligence")
        
        print("-" * 50)
    
    return tool

def debug_zep_raw_results(tool):
    """See what Zep actually returns"""
    print("\n" + "="*50)
    print("🔍 DEBUG: Raw Zep Results")
    print("="*50)
    
    # Test raw Zep responses
    query = "Show me Microsoft information"
    
    print(f"🔍 Raw Zep search for: {query}")
    
    try:
        # Get raw edge results
        edge_results = tool.client.graph.search(
            user_id=tool.user_id,
            query=query,
            scope="edges",
            limit=10
        )
        
        print(f"📊 Raw edge results: {len(edge_results.edges) if hasattr(edge_results, 'edges') else 'No edges'}")
        if hasattr(edge_results, 'edges') and edge_results.edges:
            for i, edge in enumerate(edge_results.edges[:3]):
                print(f"  {i+1}. Edge: {edge}")
                print(f"      Attributes: {dir(edge)}")
        
        # Get raw node results  
        node_results = tool.client.graph.search(
            user_id=tool.user_id,
            query=query,
            scope="nodes",
            limit=5
        )
        
        print(f"📊 Raw node results: {len(node_results.nodes) if hasattr(node_results, 'nodes') else 'No nodes'}")
        if hasattr(node_results, 'nodes') and node_results.nodes:
            for i, node in enumerate(node_results.nodes[:3]):
                print(f"  {i+1}. Node: {node}")
                print(f"      Attributes: {dir(node)}")
                
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    tool = test_basic_zep()
    debug_zep_raw_results(tool)