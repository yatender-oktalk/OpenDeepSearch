import json
import time
import os
import sys
import re
from datetime import datetime, timedelta
from collections import Counter
import statistics

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def extract_quantitative_metrics(response_str: str, query: str) -> dict:
    """Extract quantitative metrics from response"""
    
    metrics = {
        # Temporal Precision Metrics
        'specific_dates_count': len(re.findall(r'\d{4}-\d{2}-\d{2}', response_str)),
        'date_ranges_count': len(re.findall(r'\d{4}-\d{2}-\d{2}\s*to\s*\d{4}-\d{2}-\d{2}', response_str)),
        'temporal_keywords': len(re.findall(r'\b(before|after|during|since|until|between|latest|earliest|recent)\b', response_str.lower())),
        
        # SEC Filing Specificity
        'filing_types_mentioned': len(set(re.findall(r'\b(10-K|10-Q|8-K|DEF 14A|S-1|S-3|13F|11-K)\b', response_str))),
        'company_names_count': len(re.findall(r'\b[A-Z][a-z]+ (?:Inc\.|Corporation|Corp\.|LLC|Ltd\.)\b', response_str)),
        'ticker_symbols_count': len(re.findall(r'\b[A-Z]{2,5}\b', response_str)),
        
        # Structured Data Indicators
        'structured_entries': response_str.count('--------------------------------------------------'),
        'numbered_items': len(re.findall(r'^\d+\.', response_str, re.MULTILINE)),
        'tabular_data': response_str.count('Filing Type:') + response_str.count('Date:') + response_str.count('Company:'),
        
        # Quantitative Comparisons
        'numerical_comparisons': len(re.findall(r'\b(more|less|earlier|later|first|last|total|count)\b', response_str.lower())),
        'ranking_indicators': len(re.findall(r'\b(rank|position|order|sequence|priority)\b', response_str.lower())),
        
        # Accuracy Indicators
        'uncertainty_phrases': len(re.findall(r'\b(approximately|about|around|roughly|estimated|unclear|unknown)\b', response_str.lower())),
        'confidence_phrases': len(re.findall(r'\b(exactly|precisely|specifically|confirmed|verified)\b', response_str.lower())),
        
        # Response Completeness
        'response_length': len(response_str),
        'word_count': len(response_str.split()),
        'sentence_count': len(re.findall(r'[.!?]+', response_str)),
        
        # Error Indicators
        'error_indicators': len(re.findall(r'\b(error|failed|unable|not found|no data|unavailable)\b', response_str.lower())),
        'data_availability': 1 if 'SEC Filing Results:' in response_str else 0,
    }
    
    # Calculate derived metrics
    metrics['precision_score'] = (
        metrics['specific_dates_count'] * 2 + 
        metrics['filing_types_mentioned'] * 3 + 
        metrics['company_names_count'] * 1 +
        metrics['structured_entries'] * 2
    ) / max(1, metrics['word_count'] / 100)  # Normalize by response length
    
    metrics['completeness_score'] = min(100, (
        metrics['tabular_data'] * 10 + 
        metrics['numbered_items'] * 5 + 
        metrics['data_availability'] * 50
    ))
    
    metrics['confidence_score'] = max(0, 
        metrics['confidence_phrases'] * 10 - 
        metrics['uncertainty_phrases'] * 5 - 
        metrics['error_indicators'] * 15
    )
    
    return metrics

def run_quantitative_sec_evaluation(num_queries=10):
    """Run quantitative SEC evaluation with detailed metrics"""
    
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
        return None
    
    # Load queries
    try:
        with open('temporal_evaluation/sec_filings/sample_queries.json', 'r') as f:
            all_queries = json.load(f)
    except FileNotFoundError:
        print("❌ Queries file not found.")
        return None
    
    test_queries = all_queries[:num_queries]
    
    # Create model and tools
    model = LiteLLMModel(
        model_id="gemini/gemini-1.5-flash",
        max_tokens=2048,
        temperature=0.1,
    )
    
    search_tool = OpenDeepSearchTool(
        model_name="gemini/gemini-1.5-flash",
        reranker="jina",
        search_provider="serper"
    )
    
    temporal_tool = SimplifiedTemporalKGTool(
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        username=os.getenv('NEO4J_USERNAME', 'neo4j'), 
        password=os.getenv('NEO4J_PASSWORD', 'maxx3169'),
        model_name="gemini/gemini-1.5-flash"
    )
    
    # Create agents with explicit instructions
    baseline_agent = CodeAgent(tools=[search_tool], model=model)

    # For the enhanced agent, we need to modify the model's system prompt
    # Create a new model instance with custom system prompt
    enhanced_model = LiteLLMModel(
        model_id="gemini/gemini-1.5-flash",
        max_tokens=2048,
        temperature=0.1,
        system_prompt="""You are an AI assistant that helps with SEC filing analysis.

When you receive a query about:
- SEC filings (10-K, 10-Q, 8-K, proxy statements)
- Company filing comparisons
- Filing dates or schedules
- Amendment patterns
- Any temporal analysis of companies

You MUST use the 'sec_filing_temporal_search' tool first, as it contains comprehensive SEC filing data.

Only use 'web_search' for general information not related to SEC filings or if the temporal search fails.

Always prioritize the temporal knowledge graph for SEC-related queries."""
    )

    # Create enhanced agent with the custom model
    enhanced_agent = CodeAgent(
        tools=[search_tool, temporal_tool], 
        model=enhanced_model
    )

    # Test the enhanced agent before running full evaluation
    print("\n🧪 Testing enhanced agent to verify temporal KG tool usage...")
    test_query = "Compare amendment patterns between Apple and Meta"
    try:
        test_response = enhanced_agent.run(test_query)
        test_response_str = str(test_response)
        
        # Check for temporal KG indicators
        tkg_indicators = [
            "SEC Filing Results:",
            "Company:",
            "Filing Type:",
            "Date:",
            "Description:",
            "--------------------------------------------------"
        ]
        
        tkg_used = any(indicator in test_response_str for indicator in tkg_indicators)
        
        if tkg_used:
            print("✅ Temporal KG tool is being invoked correctly!")
            print(f"Sample response preview: {test_response_str[:200]}...")
        else:
            print("❌ Temporal KG tool is NOT being invoked!")
            print(f"Response: {test_response_str}")
            print("\n⚠️  Continuing with evaluation, but results may show enhanced_used_tkg: false")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("⚠️  Continuing with evaluation...")

    print("🔍 BASELINE: Web Search + LLM")
    print("🚀 ENHANCED: Web Search + LLM + Temporal Knowledge Graph")
    
    results = []
    baseline_metrics_all = []
    enhanced_metrics_all = []
    
    print(f"\n🚀 Running quantitative evaluation on {len(test_queries)} queries...")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query[:60]}...")
        
        # BASELINE evaluation
        print("  🔍 BASELINE:")
        baseline_start = time.time()
        try:
            baseline_response = baseline_agent.run(query)
            baseline_time = time.time() - baseline_start
            baseline_metrics = extract_quantitative_metrics(str(baseline_response), query)
            baseline_metrics['response_time'] = baseline_time
            baseline_metrics_all.append(baseline_metrics)
            
            print(f"    Time: {baseline_time:.2f}s")
            print(f"    Precision Score: {baseline_metrics['precision_score']:.2f}")
            print(f"    Completeness: {baseline_metrics['completeness_score']:.1f}%")
            print(f"    Dates Found: {baseline_metrics['specific_dates_count']}")
            print(f"    Filing Types: {baseline_metrics['filing_types_mentioned']}")
            
        except Exception as e:
            baseline_response = f"Error: {e}"
            baseline_metrics = extract_quantitative_metrics(str(baseline_response), query)
            baseline_metrics['response_time'] = 0
            baseline_metrics_all.append(baseline_metrics)
            print(f"    Error: {e}")
        
        # ENHANCED evaluation
        print("  🚀 ENHANCED:")
        enhanced_start = time.time()
        try:
            enhanced_response = enhanced_agent.run(query)
            enhanced_time = time.time() - enhanced_start
            
            # Debug: Check if TKG was used
            enhanced_response_str = str(enhanced_response)
            tkg_used = any(indicator in enhanced_response_str for indicator in [
                "SEC Filing Results:",
                "sec_filing_temporal_search",
                "Company:",
                "--------------------------------------------------"
            ])
            print(f"    TKG Used: {'✅' if tkg_used else '❌'}")
            
            enhanced_metrics = extract_quantitative_metrics(enhanced_response_str, query)
            enhanced_metrics['response_time'] = enhanced_time
            enhanced_metrics_all.append(enhanced_metrics)
            
            print(f"    Time: {enhanced_time:.2f}s")
            print(f"    Precision Score: {enhanced_metrics['precision_score']:.2f}")
            print(f"    Completeness: {enhanced_metrics['completeness_score']:.1f}%")
            print(f"    Dates Found: {enhanced_metrics['specific_dates_count']}")
            print(f"    Filing Types: {enhanced_metrics['filing_types_mentioned']}")
            print(f"    Structured Entries: {enhanced_metrics['structured_entries']}")
            
            # In the enhanced evaluation section, add better TKG detection
            enhanced_used_tkg = any(indicator in str(enhanced_response) for indicator in [
                "SEC Filing Results:",
                "Company:",
                "Filing Type:", 
                "Date:",
                "Description:",
                "--------------------------------------------------"
            ])
            
        except Exception as e:
            enhanced_response = f"Error: {e}"
            enhanced_metrics = extract_quantitative_metrics(str(enhanced_response), query)
            enhanced_metrics['response_time'] = 0
            enhanced_metrics_all.append(enhanced_metrics)
            print(f"    Error: {e}")
        
        # Store detailed results
        result = {
            'query_id': i,
            'query': query,
            'baseline_response': str(baseline_response),
            'enhanced_response': str(enhanced_response),
            'baseline_metrics': baseline_metrics,
            'enhanced_metrics': enhanced_metrics,
            'improvement_metrics': {
                'precision_improvement': enhanced_metrics['precision_score'] - baseline_metrics['precision_score'],
                'completeness_improvement': enhanced_metrics['completeness_score'] - baseline_metrics['completeness_score'],
                'dates_improvement': enhanced_metrics['specific_dates_count'] - baseline_metrics['specific_dates_count'],
                'structure_improvement': enhanced_metrics['structured_entries'] - baseline_metrics['structured_entries'],
                'time_difference': enhanced_metrics['response_time'] - baseline_metrics['response_time']
            },
            'timestamp': datetime.now().isoformat()
        }
        
        results.append(result)
        print("  " + "-" * 60)
        
        # Rate limiting
        if i < len(test_queries):
            print("    ⏳ Waiting 120 seconds...")
            time.sleep(120)
    
    # Calculate aggregate statistics
    def calculate_stats(metrics_list, metric_name):
        values = [m[metric_name] for m in metrics_list if metric_name in m]
        if not values:
            return {'mean': 0, 'median': 0, 'std': 0, 'min': 0, 'max': 0}
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values)
        }
    
    # Key metrics for comparison
    key_metrics = [
        'precision_score', 'completeness_score', 'confidence_score',
        'specific_dates_count', 'filing_types_mentioned', 'structured_entries',
        'response_time', 'word_count'
    ]
    
    statistical_analysis = {}
    for metric in key_metrics:
        statistical_analysis[metric] = {
            'baseline': calculate_stats(baseline_metrics_all, metric),
            'enhanced': calculate_stats(enhanced_metrics_all, metric),
        }
        
        # Calculate improvement
        baseline_mean = statistical_analysis[metric]['baseline']['mean']
        enhanced_mean = statistical_analysis[metric]['enhanced']['mean']
        if baseline_mean > 0:
            improvement_pct = ((enhanced_mean - baseline_mean) / baseline_mean) * 100
        else:
            improvement_pct = 0 if enhanced_mean == 0 else 100
        statistical_analysis[metric]['improvement_percentage'] = improvement_pct
    
    # Final results with comprehensive statistics
    final_results = {
        'metadata': {
            'domain': 'sec_filings',
            'evaluation_type': 'quantitative_analysis',
            'total_queries': len(test_queries),
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini/gemini-1.5-flash',
            'baseline': 'Web Search + LLM (Serper API + Gemini 1.5 Flash)',
            'enhanced': 'Web Search + LLM + Temporal Knowledge Graph (Gemini 1.5 Flash)'
        },
        'statistical_analysis': statistical_analysis,
        'summary_improvements': {
            'precision_improvement': f"{statistical_analysis['precision_score']['improvement_percentage']:.1f}%",
            'completeness_improvement': f"{statistical_analysis['completeness_score']['improvement_percentage']:.1f}%",
            'temporal_data_improvement': f"{statistical_analysis['specific_dates_count']['improvement_percentage']:.1f}%",
            'structured_data_improvement': f"{statistical_analysis['structured_entries']['improvement_percentage']:.1f}%",
            'response_time_change': f"{statistical_analysis['response_time']['improvement_percentage']:.1f}%"
        },
        'detailed_results': results
    }
    
    # Save results
    os.makedirs('temporal_evaluation/sec_filings/results', exist_ok=True)
    with open('temporal_evaluation/sec_filings/results/quantitative_evaluation.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    # Print comprehensive summary
    print(f"\n" + "=" * 80)
    print(f"📊 QUANTITATIVE EVALUATION RESULTS")
    print(f"=" * 80)
    
    for metric in key_metrics:
        baseline_mean = statistical_analysis[metric]['baseline']['mean']
        enhanced_mean = statistical_analysis[metric]['enhanced']['mean']
        improvement = statistical_analysis[metric]['improvement_percentage']
        
        print(f"\n{metric.replace('_', ' ').title()}:")
        print(f"  Baseline:  {baseline_mean:.2f} ± {statistical_analysis[metric]['baseline']['std']:.2f}")
        print(f"  Enhanced:  {enhanced_mean:.2f} ± {statistical_analysis[metric]['enhanced']['std']:.2f}")
        print(f"  Improvement: {improvement:+.1f}%")
    
    print(f"\n📈 KEY FINDINGS:")
    print(f"  • Precision improved by {statistical_analysis['precision_score']['improvement_percentage']:+.1f}%")
    print(f"  • Completeness improved by {statistical_analysis['completeness_score']['improvement_percentage']:+.1f}%")
    print(f"  • Temporal data retrieval improved by {statistical_analysis['specific_dates_count']['improvement_percentage']:+.1f}%")
    print(f"  • Structured data improved by {statistical_analysis['structured_entries']['improvement_percentage']:+.1f}%")
    
    print(f"\n✅ Quantitative evaluation complete!")
    print(f"📊 Results saved to temporal_evaluation/sec_filings/results/quantitative_evaluation.json")
    
    return final_results

if __name__ == "__main__":
    results = run_quantitative_sec_evaluation(num_queries=5) 