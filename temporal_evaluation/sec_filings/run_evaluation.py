import json
import time
import os
import sys
import re
from datetime import datetime

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def run_sec_evaluation(num_queries=10):
    """Run SEC filings evaluation: Web Search + LLM vs Web Search + LLM + TKG"""
    
    # Import required modules
    try:
        from smolagents import CodeAgent, LiteLLMModel
        from opendeepsearch import OpenDeepSearchTool
        from opendeepsearch.simplified_temporal_kg_tool import SimplifiedTemporalKGTool
        print("✅ Successfully imported OpenDeepSearch modules")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None
    
    # Check for Gemini API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY environment variable not set!")
        print("Get your API key from https://makersuite.google.com/app/apikey")
        return None
    
    # Load queries
    try:
        with open('temporal_evaluation/sec_filings/sample_queries.json', 'r') as f:
            all_queries = json.load(f)
    except FileNotFoundError:
        print("❌ Queries file not found. Run generate_queries.py first.")
        return None
    
    test_queries = all_queries[:num_queries]
    
    # Create the model using Gemini 1.5 Flash
    model = LiteLLMModel(
        model_id="gemini/gemini-1.5-flash",  # Flash model - fast and efficient
        max_tokens=2048,
        temperature=0.1,
    )
    
    # Create tools
    print("Creating tools...")
    
    # Web search tool (baseline)
    search_tool = OpenDeepSearchTool(
        model_name="gemini/gemini-1.5-flash",
        reranker="jina",
        search_provider="serper"
    )
    
    # Simplified Temporal KG tool
    temporal_tool = SimplifiedTemporalKGTool(
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        username=os.getenv('NEO4J_USERNAME', 'neo4j'), 
        password=os.getenv('NEO4J_PASSWORD', 'maxx3169'),
        model_name="gemini/gemini-1.5-flash"  # Flash model
    )
    
    # Create agents
    print("Creating agents...")
    
    # BASELINE: Web Search + LLM only
    baseline_agent = CodeAgent(tools=[search_tool], model=model)
    
    # ENHANCED: Web Search + LLM + TKG
    enhanced_agent = CodeAgent(tools=[search_tool, temporal_tool], model=model)
    
    print("🔍 BASELINE: Web Search + LLM (using Serper API + Gemini 1.5 Flash)")
    print("🚀 ENHANCED: Web Search + LLM + Temporal Knowledge Graph (using Gemini 1.5 Flash)")
    
    results = []
    
    print(f"\n🚀 Running SEC evaluation on {len(test_queries)} queries...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query[:80]}...")
        
        # BASELINE: Web Search + LLM only
        print("  🔍 BASELINE (Web Search + LLM):")
        baseline_start = time.time()
        try:
            baseline_response = baseline_agent.run(query)
            baseline_time = time.time() - baseline_start
            print(f"    Response: {str(baseline_response)[:100]}...")
            print(f"    Time: {baseline_time:.2f}s")
        except Exception as e:
            baseline_response = f"Error: {e}"
            baseline_time = 0
            print(f"    Error: {e}")
        
        # ENHANCED: Web Search + LLM + TKG
        print("  🚀 ENHANCED (Web Search + LLM + TKG):")
        enhanced_start = time.time()
        try:
            enhanced_response = enhanced_agent.run(query)
            enhanced_time = time.time() - enhanced_start
            print(f"    Response: {str(enhanced_response)[:100]}...")
            print(f"    Time: {enhanced_time:.2f}s")
        except Exception as e:
            enhanced_response = f"Error: {e}"
            enhanced_time = 0
            print(f"    Error: {e}")
        
        # Analyze response characteristics
        baseline_str = str(baseline_response)
        enhanced_str = str(enhanced_response)
        
        # Check for specific dates
        baseline_has_dates = bool(re.search(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', baseline_str))
        enhanced_has_dates = bool(re.search(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', enhanced_str))
        
        # Check for SEC filing specific terms
        sec_terms = ['10-K', '10-Q', '8-K', 'DEF 14A', 'filing', 'SEC', 'accession']
        baseline_has_sec_terms = any(term in baseline_str for term in sec_terms)
        enhanced_has_sec_terms = any(term in enhanced_str for term in sec_terms)
        
        # Check if TKG was likely used (look for structured temporal data)
        tkg_indicators = ['SEC Filing Results:', 'Company:', 'Filing Type:', 'Date:', 'Description:']
        enhanced_used_tkg = any(indicator in enhanced_str for indicator in tkg_indicators)
        
        result = {
            'query_id': i,
            'query': query,
            'baseline_response': baseline_str,
            'enhanced_response': enhanced_str,
            'baseline_time': baseline_time,
            'enhanced_time': enhanced_time,
            'baseline_has_dates': baseline_has_dates,
            'enhanced_has_dates': enhanced_has_dates,
            'baseline_has_sec_terms': baseline_has_sec_terms,
            'enhanced_has_sec_terms': enhanced_has_sec_terms,
            'enhanced_used_tkg': enhanced_used_tkg,
            'response_length_baseline': len(baseline_str),
            'response_length_enhanced': len(enhanced_str),
            'domain': 'sec_filings',
            'timestamp': datetime.now().isoformat()
        }
        
        results.append(result)
        
        # Save intermediate results every 5 queries
        if i % 5 == 0:
            os.makedirs('temporal_evaluation/sec_filings/results', exist_ok=True)
            with open(f'temporal_evaluation/sec_filings/results/evaluation_partial_{i}.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"    💾 Saved partial results ({i} queries)")
        
        print("  " + "-" * 50)
        
        # Add delay between queries to avoid rate limits
        if i < len(test_queries):
            print("    ⏳ Waiting 60 seconds to avoid rate limits...")
            time.sleep(60)
    
    # Calculate summary statistics
    tkg_usage = sum(1 for r in results if r['enhanced_used_tkg'])
    baseline_dates = sum(1 for r in results if r['baseline_has_dates'])
    enhanced_dates = sum(1 for r in results if r['enhanced_has_dates'])
    baseline_sec_terms = sum(1 for r in results if r['baseline_has_sec_terms'])
    enhanced_sec_terms = sum(1 for r in results if r['enhanced_has_sec_terms'])
    
    avg_baseline_length = sum(r['response_length_baseline'] for r in results) / len(results)
    avg_enhanced_length = sum(r['response_length_enhanced'] for r in results) / len(results)
    
    # Save final results
    final_results = {
        'metadata': {
            'domain': 'sec_filings',
            'total_queries': len(test_queries),
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini/gemini-1.5-flash',  # Flash model
            'baseline': 'Web Search + LLM (Serper API + Gemini 1.5 Flash)',
            'enhanced': 'Web Search + LLM + Temporal Knowledge Graph (Gemini 1.5 Flash)',
            'summary': {
                'tkg_usage_rate': f"{tkg_usage}/{len(test_queries)} ({tkg_usage/len(test_queries)*100:.1f}%)",
                'baseline_dates_found': f"{baseline_dates}/{len(test_queries)} ({baseline_dates/len(test_queries)*100:.1f}%)",
                'enhanced_dates_found': f"{enhanced_dates}/{len(test_queries)} ({enhanced_dates/len(test_queries)*100:.1f}%)",
                'baseline_sec_terms': f"{baseline_sec_terms}/{len(test_queries)} ({baseline_sec_terms/len(test_queries)*100:.1f}%)",
                'enhanced_sec_terms': f"{enhanced_sec_terms}/{len(test_queries)} ({enhanced_sec_terms/len(test_queries)*100:.1f}%)",
                'avg_response_length_baseline': f"{avg_baseline_length:.0f} chars",
                'avg_response_length_enhanced': f"{avg_enhanced_length:.0f} chars"
            }
        },
        'results': results
    }
    
    os.makedirs('temporal_evaluation/sec_filings/results', exist_ok=True)
    with open('temporal_evaluation/sec_filings/results/evaluation_final.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n✅ SEC evaluation complete!")
    print(f"📊 Results saved to temporal_evaluation/sec_filings/results/evaluation_final.json")
    print(f"\n📈 SUMMARY:")
    print(f"  TKG Usage: {tkg_usage}/{len(test_queries)} queries ({tkg_usage/len(test_queries)*100:.1f}%)")
    print(f"  Baseline found dates: {baseline_dates}/{len(test_queries)} ({baseline_dates/len(test_queries)*100:.1f}%)")
    print(f"  Enhanced found dates: {enhanced_dates}/{len(test_queries)} ({enhanced_dates/len(test_queries)*100:.1f}%)")
    print(f"  Baseline SEC terms: {baseline_sec_terms}/{len(test_queries)} ({baseline_sec_terms/len(test_queries)*100:.1f}%)")
    print(f"  Enhanced SEC terms: {enhanced_sec_terms}/{len(test_queries)} ({enhanced_sec_terms/len(test_queries)*100:.1f}%)")
    print(f"  Avg response length - Baseline: {avg_baseline_length:.0f}, Enhanced: {avg_enhanced_length:.0f}")
    
    return final_results

if __name__ == "__main__":
    # Run evaluation with 5 queries for testing
    results = run_sec_evaluation(num_queries=5)
