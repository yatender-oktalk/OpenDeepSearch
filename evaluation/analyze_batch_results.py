import json
import re
from collections import defaultdict

def analyze_batch_results():
    """Analyze the batch evaluation results"""
    
    with open('batch_evaluation_results.json', 'r') as f:
        data = json.load(f)
    
    results = data['results']
    total_queries = len(results)
    
    print("="*60)
    print(f"BATCH EVALUATION ANALYSIS ({total_queries} queries)")
    print("="*60)
    
    # Performance metrics
    metrics = {
        'date_precision': {'baseline': 0, 'enhanced': 0},
        'completeness': {'baseline': 0, 'enhanced': 0},
        'structured_response': {'baseline': 0, 'enhanced': 0},
        'error_rate': {'baseline': 0, 'enhanced': 0},
        'response_time': {'baseline': [], 'enhanced': []}
    }
    
    for result in results:
        baseline = result['baseline_response']
        enhanced = result['enhanced_response']
        
        # Check for errors
        if 'Error:' in baseline:
            metrics['error_rate']['baseline'] += 1
        if 'Error:' in enhanced:
            metrics['error_rate']['enhanced'] += 1
        
        # Check for date precision (exact dates vs approximate)
        if re.search(r'\d{4}-\d{2}-\d{2}', enhanced):
            metrics['date_precision']['enhanced'] += 1
        if re.search(r'\d{4}-\d{2}-\d{2}', baseline):
            metrics['date_precision']['baseline'] += 1
        
        # Check for structured responses
        if 'Timeline for' in enhanced or 'Found' in enhanced:
            metrics['structured_response']['enhanced'] += 1
        
        # Check completeness (longer, more detailed responses)
        if len(enhanced) > len(baseline) * 1.2:
            metrics['completeness']['enhanced'] += 1
        elif len(baseline) > len(enhanced) * 1.2:
            metrics['completeness']['baseline'] += 1
        
        # Response times
        metrics['response_time']['baseline'].append(result.get('baseline_time', 0))
        metrics['response_time']['enhanced'].append(result.get('enhanced_time', 0))
    
    # Calculate percentages and averages
    print(f"📊 PERFORMANCE METRICS:")
    print(f"Date Precision:")
    print(f"  Baseline: {metrics['date_precision']['baseline']}/{total_queries} ({metrics['date_precision']['baseline']/total_queries*100:.1f}%)")
    print(f"  Enhanced: {metrics['date_precision']['enhanced']}/{total_queries} ({metrics['date_precision']['enhanced']/total_queries*100:.1f}%)")
    
    print(f"\nStructured Responses:")
    print(f"  Baseline: {metrics['structured_response']['baseline']}/{total_queries} ({metrics['structured_response']['baseline']/total_queries*100:.1f}%)")
    print(f"  Enhanced: {metrics['structured_response']['enhanced']}/{total_queries} ({metrics['structured_response']['enhanced']/total_queries*100:.1f}%)")
    
    print(f"\nError Rate:")
    print(f"  Baseline: {metrics['error_rate']['baseline']}/{total_queries} ({metrics['error_rate']['baseline']/total_queries*100:.1f}%)")
    print(f"  Enhanced: {metrics['error_rate']['enhanced']}/{total_queries} ({metrics['error_rate']['enhanced']/total_queries*100:.1f}%)")
    
    # Response time analysis
    if metrics['response_time']['baseline'] and metrics['response_time']['enhanced']:
        avg_baseline_time = sum(metrics['response_time']['baseline']) / len(metrics['response_time']['baseline'])
        avg_enhanced_time = sum(metrics['response_time']['enhanced']) / len(metrics['response_time']['enhanced'])
        
        print(f"\nResponse Time:")
        print(f"  Baseline: {avg_baseline_time:.2f}s average")
        print(f"  Enhanced: {avg_enhanced_time:.2f}s average")
    
    # Sample improvements
    print(f"\n🎯 SAMPLE IMPROVEMENTS:")
    improvements = 0
    for result in results[:10]:  # Show first 10
        baseline = result['baseline_response']
        enhanced = result['enhanced_response']
        
        if ('Timeline for' in enhanced or 'Found' in enhanced) and len(enhanced) > len(baseline):
            print(f"✅ Query: {result['query'][:60]}...")
            print(f"   Enhanced provided structured timeline vs general response")
            improvements += 1
    
    print(f"\nShowing {improvements} sample improvements out of first 10 queries")
    
    # Overall summary
    total_improvements = (
        metrics['date_precision']['enhanced'] - metrics['date_precision']['baseline'] +
        metrics['structured_response']['enhanced'] - metrics['structured_response']['baseline'] +
        metrics['error_rate']['baseline'] - metrics['error_rate']['enhanced']
    )
    
    print(f"\n🏆 OVERALL SUMMARY:")
    print(f"Total Queries Evaluated: {total_queries}")
    print(f"Net Improvements: {total_improvements}")
    print(f"Improvement Rate: {total_improvements/total_queries*100:.1f}%")

if __name__ == "__main__":
    analyze_batch_results()
