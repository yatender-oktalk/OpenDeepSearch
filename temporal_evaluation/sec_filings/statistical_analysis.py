import json
import scipy.stats as stats
import numpy as np

def perform_statistical_tests(results_file):
    """Perform statistical significance tests"""
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['detailed_results']
    
    # Extract paired data for t-tests
    baseline_precision = [r['baseline_metrics']['precision_score'] for r in results]
    enhanced_precision = [r['enhanced_metrics']['precision_score'] for r in results]
    
    baseline_completeness = [r['baseline_metrics']['completeness_score'] for r in results]
    enhanced_completeness = [r['enhanced_metrics']['completeness_score'] for r in results]
    
    # Paired t-tests
    precision_ttest = stats.ttest_rel(enhanced_precision, baseline_precision)
    completeness_ttest = stats.ttest_rel(enhanced_completeness, baseline_completeness)
    
    print("Statistical Significance Tests:")
    print(f"Precision Score - t-statistic: {precision_ttest.statistic:.3f}, p-value: {precision_ttest.pvalue:.3f}")
    print(f"Completeness Score - t-statistic: {completeness_ttest.statistic:.3f}, p-value: {completeness_ttest.pvalue:.3f}")
    
    return {
        'precision_test': {'t_stat': precision_ttest.statistic, 'p_value': precision_ttest.pvalue},
        'completeness_test': {'t_stat': completeness_ttest.statistic, 'p_value': completeness_ttest.pvalue}
    } 