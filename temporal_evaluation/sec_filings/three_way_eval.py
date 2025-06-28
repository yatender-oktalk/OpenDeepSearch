#!/usr/bin/env python3
"""
Three-Way SEC Filing Evaluation: OpenDeepSearch vs GraphRAG vs Zep TKG

Compares:
1. Dynamic Web Search (OpenDeepSearch baseline)
2. Static GraphRAG (Your Neo4j implementation) 
3. Advanced TKG (Zep - if available)
"""

import json
import time
import os
import sys
from datetime import datetime

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def run_three_way_evaluation(num_queries=5):
    """Execute comprehensive three-way comparison"""
    
    # Import modules
    try:
        from smolagents import CodeAgent, LiteLLMModel
        from opendeepsearch import OpenDeepSearchTool
        from opendeepsearch.simplified_temporal_kg_tool import SimplifiedTemporalKGTool
        print("✅ Modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None
    
    # Validate API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not set!")
        return None
    
    # Load test queries
    try:
        with open('temporal_evaluation/sec_filings/sample_queries.json', 'r') as f:
            all_queries = json.load(f)
        test_queries = all_queries[:num_queries]
        print(f"📋 Loaded {len(test_queries)} test queries")
    except FileNotFoundError:
        # Fallback test queries
        test_queries = [
            "What are Apple's exact 10-Q filing dates for 2024?",
            "When did Microsoft file its 2024 annual report (10-K)?", 
            "Compare the number of SEC filings between Apple and Microsoft in 2024",
            "Show me Meta's recent 10-K filings",
            "List Tesla's SEC filings from Q1 2024"
        ]
        print(f"📋 Using fallback queries: {len(test_queries)}")
    
    # Model configuration
    model_config = {
        "model_id": "gemini/gemini-1.5-flash",
        "max_tokens": 2048,
        "temperature": 0.1
    }
    
    # Create tools
    search_tool = OpenDeepSearchTool(
        model_name="gemini/gemini-1.5-flash",
        reranker="jina",
        search_provider="serper"
    )
    
    graphrag_tool = SimplifiedTemporalKGTool(
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        username=os.getenv('NEO4J_USERNAME', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'maxx3169'),
        model_name="gemini/gemini-1.5-flash"
    )
    
    # Create agents
    # 1. BASELINE: Web Search only
    baseline_agent = CodeAgent(tools=[search_tool], model=LiteLLMModel(**model_config))
    
    # 2. GRAPHRAG: Web Search + Your Neo4j TKG
    graphrag_agent = CodeAgent(
        tools=[search_tool, graphrag_tool], 
        model=LiteLLMModel(
            **model_config,
            system_prompt="""You are a SEC filing specialist with access to comprehensive temporal data.

CRITICAL: For SEC filing queries, ALWAYS use 'sec_filing_temporal_search' tool FIRST.
This tool contains 25,000+ SEC filings with precise dates and structured data.

Only use web_search if the temporal search returns insufficient results.
Always prioritize the structured temporal knowledge graph for SEC-related queries."""
        )
    )
    
    print("🔍 BASELINE: Web Search + LLM only")
    print("🏗️ GRAPHRAG: Web Search + LLM + Neo4j TKG (25,606 filings)")
    
    # Test GraphRAG tool usage
    print(f"\n🧪 Testing GraphRAG tool...")
    try:
        test_response = graphrag_tool.forward("Show me Apple's recent 10-Q filings")
        if "SEC Filing Results:" in test_response:
            print("✅ GraphRAG tool working correctly!")
        else:
            print("⚠️ GraphRAG tool may not be working properly")
            print(f"Response preview: {test_response[:200]}...")
    except Exception as e:
        print(f"❌ GraphRAG tool test failed: {e}")
        return None
    
    # Run evaluation
    results = []
    
    print(f"\n🚀 Starting three-way evaluation...")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query}")
        
        # BASELINE evaluation
        print("  🔍 BASELINE (Web Search):")
        baseline_start = time.time()
        try:
            baseline_response = baseline_agent.run(query)
            baseline_time = time.time() - baseline_start
            baseline_metrics = analyze_response(str(baseline_response), query)
            baseline_metrics['response_time'] = baseline_time
            
            print(f"    ⏱️ Time: {baseline_time:.2f}s")
            print(f"    📄 Length: {len(str(baseline_response))} chars")
            print(f"    📊 Metrics: {baseline_metrics}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            baseline_response = f"Error: {e}"
            baseline_metrics = {'error': True, 'response_time': 0}
        
        # GRAPHRAG evaluation
        print("  🏗️ GRAPHRAG (Neo4j + Web Search):")
        graphrag_start = time.time()
        try:
            graphrag_response = graphrag_agent.run(query)
            graphrag_time = time.time() - graphrag_start
            graphrag_metrics = analyze_response(str(graphrag_response), query)
            graphrag_metrics['response_time'] = graphrag_time
            
            # Check if TKG tool was used
            used_tkg = "SEC Filing Results:" in str(graphrag_response)
            print(f"    🔧 TKG Used: {'✅' if used_tkg else '❌'}")
            print(f"    ⏱️ Time: {graphrag_time:.2f}s")
            print(f"    📄 Length: {len(str(graphrag_response))} chars")
            print(f"    📊 Metrics: {graphrag_metrics}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            graphrag_response = f"Error: {e}"
            graphrag_metrics = {'error': True, 'response_time': 0}
        
        # Store results
        result = {
            'query_id': i,
            'query': query,
            'baseline_response': str(baseline_response),
            'graphrag_response': str(graphrag_response),
            'baseline_metrics': baseline_metrics,
            'graphrag_metrics': graphrag_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        results.append(result)
        print("  " + "-" * 60)
        
        # Rate limiting
        if i < len(test_queries):
            print("    ⏳ Waiting 60 seconds...")
            time.sleep(60)
    
    # Save results
    results_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'num_queries': len(test_queries),
            'systems': ['baseline_web_search', 'graphrag_neo4j'],
            'dataset': 'sec_filings_enhanced (25,606 events)'
        },
        'results': results
    }
    
    os.makedirs('temporal_evaluation/sec_filings/results', exist_ok=True)
    with open('temporal_evaluation/sec_filings/results/three_way_evaluation.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n✅ Three-way evaluation completed!")
    print(f"📊 Results saved to: temporal_evaluation/sec_filings/results/three_way_evaluation.json")
    
    return results_data

def analyze_response(response_str, query):
    """Quick analysis of response quality"""
    
    # Count specific elements
    sec_terms = ['10-K', '10-Q', '8-K', 'DEF 14A', 'SEC', 'filing']
    dates_found = len(re.findall(r'\d{4}-\d{2}-\d{2}', response_str))
    sec_term_count = sum(1 for term in sec_terms if term in response_str)
    structured_data = "SEC Filing Results:" in response_str
    
    return {
        'dates_found': dates_found,
        'sec_terms': sec_term_count,
        'structured_data': structured_data,
        'word_count': len(response_str.split()),
        'char_count': len(response_str)
    }

if __name__ == "__main__":
    import re
    
    print("🚀 Three-Way SEC Filing Evaluation")
    print("=" * 60)
    print("Systems under test:")
    print("1. 🔍 Baseline: Web Search + LLM")
    print("2. 🏗️ GraphRAG: Web Search + LLM + Neo4j (25,606 filings)")
    print("=" * 60)
    
    results = run_three_way_evaluation(num_queries=5)
    
    if results:
        print(f"\n🎉 Evaluation completed!")
        baseline_avg = sum(r['baseline_metrics']['sec_terms'] for r in results['results']) / len(results['results'])
        graphrag_avg = sum(r['graphrag_metrics']['sec_terms'] for r in results['results']) / len(results['results'])
        
        print(f"📊 Quick comparison:")
        print(f"  Baseline SEC terms avg: {baseline_avg:.1f}")
        print(f"  GraphRAG SEC terms avg: {graphrag_avg:.1f}")
        print(f"  Improvement: {((graphrag_avg - baseline_avg) / max(baseline_avg, 0.1)) * 100:+.1f}%")