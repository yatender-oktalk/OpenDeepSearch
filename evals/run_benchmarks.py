"""
Run SimpleQA and FRAMES benchmarks with TKG comparison
"""

import os
import json
import time
from typing import Dict, List
from opendeepsearch import OpenDeepSearchTool
from temporal_accuracy import TemporalAccuracyEvaluator


class BenchmarkRunner:
    def __init__(self, benchmark_name: str = "simpleqa"):
        self.benchmark_name = benchmark_name
        self.results = []
        self.temporal_evaluator = TemporalAccuracyEvaluator()

    def load_benchmark_queries(self) -> List[Dict]:
        """Load benchmark queries from file"""
        # For now, use a simple set of test queries
        # In production, load from SimpleQA or FRAMES dataset

        if self.benchmark_name == "temporal":
            return [
                {
                    "id": "temp_001",
                    "query": "What happened to Customer CUST001?",
                    "type": "temporal_timeline",
                },
                {
                    "id": "temp_002",
                    "query": "Which customers upgraded within 30 days of signup?",
                    "type": "temporal_multi_hop",
                },
                {
                    "id": "temp_003",
                    "query": "What events led to Customer CUST003's cancellation?",
                    "type": "temporal_causal",
                },
            ]
        else:
            # SimpleQA style queries
            return [
                {
                    "id": "sq_001",
                    "query": "What is the capital of France?",
                    "answer": "Paris",
                    "type": "factual",
                },
                {
                    "id": "sq_002",
                    "query": "Who wrote Romeo and Juliet?",
                    "answer": "William Shakespeare",
                    "type": "factual",
                },
            ]

    def run_benchmark(self, use_tkg: bool = False):
        """Run benchmark with or without TKG"""
        queries = self.load_benchmark_queries()

        print(f"\n🏃 Running {self.benchmark_name} benchmark (TKG: {use_tkg})")

        for query_data in queries:
            start_time = time.time()

            if use_tkg and query_data.get("type", "").startswith("temporal"):
                # Use multi-tool setup for temporal queries
                result = self._run_with_tkg(query_data["query"])
            else:
                # Use standard search
                result = self._run_baseline(query_data["query"])

            latency = time.time() - start_time

            # Evaluate result
            evaluation = self._evaluate_result(query_data, result)

            self.results.append(
                {
                    "query_id": query_data["id"],
                    "query": query_data["query"],
                    "latency": latency,
                    "use_tkg": use_tkg,
                    "evaluation": evaluation,
                }
            )

            print(f"  ✓ {query_data['id']}: {latency:.2f}s")

    def _run_baseline(self, query: str) -> str:
        """Run with standard search tool"""
        search_tool = OpenDeepSearchTool(
            model_name=os.getenv(
                "LITELLM_SEARCH_MODEL_ID", "openrouter/google/gemini-2.0-flash-001"
            ),
            reranker="jina",
        )
        return search_tool.forward(query)

    def _run_with_tkg(self, query: str) -> str:
        """Run with TKG integration"""
        # Implementation would use the multi-tool agent setup
        # For now, return placeholder
        return f"TKG-enhanced result for: {query}"

    def _evaluate_result(self, query_data: Dict, result: str) -> Dict:
        """Evaluate result based on query type"""
        evaluation = {}

        if query_data.get("type", "").startswith("temporal"):
            # Use temporal evaluator
            temporal_scores = self.temporal_evaluator.evaluate_response(
                query_data["query"],
                result,
                {},  # Would pass expected facts in production
            )
            evaluation.update(temporal_scores)

        if "answer" in query_data:
            # Simple accuracy check for factual queries
            evaluation["correct"] = query_data["answer"].lower() in result.lower()

        return evaluation

    def save_results(self):
        """Save benchmark results"""
        output_file = f"eval/results/{self.benchmark_name}_results.json"
        os.makedirs("eval/results", exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    # Run temporal benchmark
    runner = BenchmarkRunner("temporal")
    runner.run_benchmark(use_tkg=False)
    runner.run_benchmark(use_tkg=True)
    runner.save_results()
