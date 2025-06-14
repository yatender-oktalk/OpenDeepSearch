import json
import time
import random
from datetime import datetime

def load_queries(filename, limit=None):
    """Load queries from file"""
    queries = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip() and line[0].isdigit():
                query = line.split('. ', 1)[1].strip()
                queries.append(query)
    
    if limit:
        return queries[:limit]
    return queries

def run_batch_evaluation(num_queries=100):
    """Run evaluation on batch of queries"""
    import sys
    import os
    sys.path.append(os.getcwd())
    
    # Load queries
    all_queries = load_queries('test_queries_large.txt')
    test_queries = random.sample(all_queries, min(num_queries, len(all_queries)))
    
    print(f"Running evaluation on {len(test_queries)} queries...")
    
    # Import your agents
    try:
        from src.opendeepsearch.ods_agent import OpenDeepSearchAgent
        from src.opendeepsearch.temporal_kg_tool import TemporalKGTool
        from src.opendeepsearch.ods_tool import OpenDeepSearchTool
    except ImportError as e:
        print(f"Import error: {e}")
        return
    
    # Create agents
    baseline_agent = OpenDeepSearchAgent(
        tools=[OpenDeepSearchTool()],
        model_name="openrouter/google/gemini-2.0-flash-001"
    )
    
    tkg_tool = TemporalKGTool(
        neo4j_uri=os.getenv('NEO4J_URI'),
        username=os.getenv('NEO4J_USERNAME'), 
        password=os.getenv('NEO4J_PASSWORD')
    )
    
    enhanced_agent = OpenDeepSearchAgent(
        tools=[OpenDeepSearchTool(), tkg_tool],
        model_name="openrouter/google/gemini-2.0-flash-001"
    )
    
    results = []
    start_time = time.time()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Processing: {query[:50]}...")
        
        query_start = time.time()
        
        # Baseline response
        try:
            baseline_response = baseline_agent.run(query)
            baseline_time = time.time() - query_start
        except Exception as e:
            baseline_response = f"Error: {e}"
            baseline_time = 0
        
        # Enhanced response
        enhanced_start = time.time()
        try:
            enhanced_response = enhanced_agent.run(query)
            enhanced_time = time.time() - enhanced_start
        except Exception as e:
            enhanced_response = f"Error: {e}"
            enhanced_time = 0
        
        result = {
            'query_id': i,
            'query': query,
            'baseline_response': baseline_response,
            'enhanced_response': enhanced_response,
            'baseline_time': baseline_time,
            'enhanced_time': enhanced_time,
            'timestamp': datetime.now().isoformat()
        }
        
        results.append(result)
        
        # Save intermediate results every 10 queries
        if i % 10 == 0:
            with open(f'batch_results_partial_{i}.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Saved partial results ({i} queries)")
    
    total_time = time.time() - start_time
    
    # Save final results
    final_results = {
        'metadata': {
            'total_queries': len(test_queries),
            'total_time': total_time,
            'avg_time_per_query': total_time / len(test_queries),
            'timestamp': datetime.now().isoformat()
        },
        'results': results
    }
    
    with open('batch_evaluation_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n✅ Batch evaluation complete!")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per query: {total_time/len(test_queries):.2f} seconds")
    print(f"Results saved to batch_evaluation_results.json")
    
    return final_results

if __name__ == "__main__":
    # Start with 50 queries for quick results, then scale up
    results = run_batch_evaluation(num_queries=50)
