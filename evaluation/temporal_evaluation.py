import time
import json
from typing import Dict, List

class TemporalEvaluator:
    def __init__(self, baseline_agent, enhanced_agent):
        self.baseline = baseline_agent
        self.enhanced = enhanced_agent
        self.results = {"baseline": [], "enhanced": []}
    
    def evaluate_query(self, query: str, expected_facts: List[str]) -> Dict:
        """Evaluate single query against both agents"""
        
        # Test baseline
        start_time = time.time()
        baseline_response = self.baseline.forward(query)
        baseline_time = time.time() - start_time
        
        # Test enhanced  
        start_time = time.time()
        enhanced_response = self.enhanced.run(query)
        enhanced_time = time.time() - start_time
        
        return {
            "query": query,
            "baseline_response": baseline_response,
            "enhanced_response": enhanced_response,
            "baseline_time": baseline_time,
            "enhanced_time": enhanced_time,
            "expected_facts": expected_facts
        }
    
    def calculate_accuracy(self, response: str, expected_facts: List[str]) -> float:
        """Calculate what percentage of expected facts are mentioned"""
        mentioned_facts = 0
        for fact in expected_facts:
            if fact.lower() in response.lower():
                mentioned_facts += 1
        return mentioned_facts / len(expected_facts) if expected_facts else 0
    
    def detect_hallucination(self, response: str, query: str) -> bool:
        """Detect if response contains fabricated temporal information"""
        # Look for specific patterns that indicate hallucination
        hallucination_indicators = [
            "based on general knowledge",
            "typically customers",
            "usually takes",
            "estimated timeline"
        ]
        return any(indicator in response.lower() for indicator in hallucination_indicators)

# Ground truth for evaluation
ground_truth = {
    "What happened to Customer CUST001?": [
        "signed up on 2023-01-15",
        "basic plan",
        "upgraded on 2023-06-01", 
        "premium plan",
        "login on 2023-01-16",
        "purchase on 2023-07-15"
    ],
    "What happened to Customer CUST003?": [
        "signed up on 2023-02-01",
        "login on 2023-02-02",
        "support ticket on 2023-02-10",
        "cancelled on 2023-02-28",
        "reason: cost"
    ]
} 