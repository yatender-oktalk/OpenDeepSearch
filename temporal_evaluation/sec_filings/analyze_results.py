import json
import re
from collections import defaultdict

def analyze_sec_results():
    """Analyze SEC evaluation results"""
    
    try:
        with open('sec_filings/results/evaluation_final.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Results file not found. Run evaluation first.")
        return
    
    results = data['results']
    total_queries = len(results)
    
    print("=" * 60)
    print(f"SEC FILINGS EVALUATION ANALYSIS ({total_queries} queries)")
    print("=" * 60)
    
    # Performance metrics
    metrics = {
        'specific_dates': {'baseline': 0, 'enhanced': 0},
        'structured_response': {'baseline': 0, 'enhanced': 0},
        'filing_details': {'baseline': 0, 'enhanced': 0},
        'error_rate': {'baseline': 0, 'enhanced': 0},
        'response_time': {'baseline': [], 'enhanced': []},
        'completeness': {'baseline': 0, 'enhanced': 0}
    }
    
    for result in results:
        baseline = result['baseline_response']
        enhanced = result['enhanced_response']
        
        # Check for errors
        if 'Error:' in baseline:
            metrics['error_rate']['baseline'] += 1
        if 'Error:' in enhanced:
            metrics['error_rate']['enhanced'] += 1
        
        # Check for specific dates (YYYY-MM-DD format)
        if re.search(r'\d{4}-\d{2}-\d{2}', enhanced):
            metrics['specific_dates']['enhanced'] += 1
        if re.search(r'\d{4}-\d{2}-\d{2}', baseline):
            metrics['specific_dates']['baseline'] += 1
        
        # Check for structured responses
        structured_indicators = ['Timeline for', 'Found', 'filed', 'Filing', 'Form']
        if any(indicator in enhanced for indicator in structured_indicators):
            metrics['structured_response']['enhanced'] += 1
        if any(indicator in baseline for indicator in structured_indicators):
            metrics['structured_response']['baseline'] += 1
        
        # Check for filing details (form types, accession numbers)
        filing_indicators = ['10-K', '10-Q', '8-K', 'DEF 14A', 'accession']
        if any(indicator in enhanced for indicator in filing_indicators):
            metrics['filing_details']['enhanced'] += 1
        if any(indicator in baseline for indicator in filing_indicators):
            metrics['filing_details']['baseline'] += 1
        
        # Check completeness (longer, more detailed responses)
        if len(enhanced) > len(baseline) * 1.3:
            metrics['completeness']['enhanced'] += 1
        elif len(baseline) > len(enhanced) * 1.3:
            metrics['completeness']['baseline'] += 1
        
        # Response times
        metrics['response_time']['baseline'].append(result.get('baseline_time', 0))
        metrics['response_time']['enhanced'].append(result.get('enhanced_time', 0))
    
    # Calculate percentages and averages
    print(f"📊 PERFORMANCE METRICS:")
    print(f"\nSpecific Dates (YYYY-MM-DD format):")
    print(f"  Baseline: {metrics['specific_dates']['baseline']}/{total_queries} ({metrics['specific_dates']['baseline']/total_queries*100:.1f}%)")
    print(f"  Enhanced: {metrics['specific_dates']['enhanced']}/{total_queries} ({metrics['specific_dates']['enhanced']/total_queries*100:.1f}%)")
    
    print(f"\nStructured Responses:")
    print(f"  Baseline: {metrics['structured_response']['baseline']}/{total_queries} ({metrics['structured_response']['baseline']/total_queries*100:.1f}%)")
    print(f"  Enhanced: {metrics['structured_response']['enhanced']}/{total_queries} ({metrics['structured_response']['enhanced']/total_queries*100:.1f}%)")
    
    print(f"\nFiling Details Mentioned:")
    print(f"  Baseline: {metrics['filing_details']['baseline']}/{total_queries} ({metrics['filing_details']['baseline']/total_queries*100:.1f}%)")
    print(f"  Enhanced: {metrics['filing_details']['enhanced']}/{total_queries} ({metrics['filing_details']['enhanced']/total_queries*100:.1f}%)")
    
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
    for i, result in enumerate(results[:10]):  # Show first 10
        baseline = result['baseline_response']
        enhanced = result['enhanced_response']
        
        if (metrics['specific_dates']['enhanced'] > 0 and 
            re.search(r'\d{4}-\d{2}-\d{2}', enhanced) and 
            not re.search(r'\d{4}-\d{2}-\d{2}', baseline)):
            print(f"✅ Query {i+1}: Enhanced provided specific dates vs general timeframes")
            improvements += 1
        elif len(enhanced) > len(baseline) * 1.5:
            print(f"✅ Query {i+1}: Enhanced provided more comprehensive response")
            improvements += 1
    
    # Overall summary
    total_improvements = (
        metrics['specific_dates']['enhanced'] - metrics['specific_dates']['baseline'] +
        metrics['structured_response']['enhanced'] - metrics['structured_response']['baseline'] +
        metrics['filing_details']['enhanced'] - metrics['filing_details']['baseline'] +
        metrics['error_rate']['baseline'] - metrics['error_rate']['enhanced']
    )
    
    print(f"\n🏆 OVERALL SUMMARY:")
    print(f"Total Queries Evaluated: {total_queries}")
    print(f"Net Improvements: {total_improvements}")
    print(f"Improvement Rate: {total_improvements/total_queries*100:.1f}%")
    
    # Save analysis
    analysis_results = {
        'total_queries': total_queries,
        'metrics': metrics,
        'improvement_rate': f"{total_improvements/total_queries*100:.1f}%",
        'summary': {
            'specific_dates_improvement': metrics['specific_dates']['enhanced'] - metrics['specific_dates']['baseline'],
            'structured_response_improvement': metrics['structured_response']['enhanced'] - metrics['structured_response']['baseline'],
            'filing_details_improvement': metrics['filing_details']['enhanced'] - metrics['filing_details']['baseline'],
            'error_reduction': metrics['error_rate']['baseline'] - metrics['error_rate']['enhanced']
        }
    }
    
    with open('sec_filings/results/analysis_summary.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n📄 Analysis saved to sec_filings/results/analysis_summary.json")

if __name__ == "__main__":
    analyze_sec_results()
