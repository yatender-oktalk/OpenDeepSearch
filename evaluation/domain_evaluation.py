import time
import json
from typing import Dict, List, Tuple

class DomainTemporalEvaluator:
    def __init__(self, baseline_agent, enhanced_agent):
        self.baseline = baseline_agent
        self.enhanced = enhanced_agent
        self.domains = ["medical", "financial", "security"]
        
    def evaluate_domain(self, domain: str, queries: List[str], ground_truth: Dict) -> Dict:
        """Evaluate temporal reasoning across different domains"""
        
        results = {
            "domain": domain,
            "total_queries": len(queries),
            "baseline_scores": [],
            "enhanced_scores": [],
            "performance_gap": []
        }
        
        for query in queries:
            # Test both agents
            baseline_result = self.test_agent(self.baseline, query)
            enhanced_result = self.test_agent(self.enhanced, query)
            
            # Calculate scores
            expected = ground_truth.get(query, [])
            baseline_score = self.calculate_temporal_accuracy(baseline_result, expected)
            enhanced_score = self.calculate_temporal_accuracy(enhanced_result, expected)
            
            results["baseline_scores"].append(baseline_score)
            results["enhanced_scores"].append(enhanced_score)
            results["performance_gap"].append(enhanced_score - baseline_score)
            
        return results
    
    def calculate_temporal_accuracy(self, response: str, expected_facts: List[str]) -> float:
        """Calculate temporal reasoning accuracy"""
        if not expected_facts:
            return 0.0
            
        correct_facts = 0
        for fact in expected_facts:
            if self.fact_mentioned(response, fact):
                correct_facts += 1
                
        return correct_facts / len(expected_facts)
    
    def fact_mentioned(self, response: str, fact: str) -> bool:
        """Check if temporal fact is correctly mentioned"""
        # More sophisticated matching for temporal facts
        response_lower = response.lower()
        fact_lower = fact.lower()
        
        # Handle date formats, sequences, etc.
        return fact_lower in response_lower 