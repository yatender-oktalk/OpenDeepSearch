#!/usr/bin/env python3
"""
compare_tkg.py - Compare baseline (without TKG) vs TKG-enhanced performance
Fixed version with correct smolagents imports
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os
import sys

# Try to import the required modules
try:
    from opendeepsearch import OpenDeepSearchTool
except ImportError:
    print(
        "Error: OpenDeepSearchTool not found. Make sure you're in the correct environment."
    )
    sys.exit(1)

try:
    from opendeepsearch.temporal_kg_tool import TemporalKGTool
except ImportError:
    print("Warning: TemporalKGTool not found. TKG tests will be skipped.")
    TemporalKGTool = None

try:
    from smolagents import CodeAgent, LiteLLMModel
except ImportError:
    print("Error: smolagents not found. Please install it with: pip install smolagents")
    sys.exit(1)


class TKGComparison:
    def __init__(self):
        self.results = {
            "baseline": [],
            "tkg_enhanced": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Test queries organized by type
        self.test_queries = {
            "simple_factual": [
                "What is machine learning?",
                "Who is the CEO of OpenAI?",
            ],
            "temporal_queries": [
                "What happened to Customer CUST001?",
                "Show me the timeline for Customer CUST003",
                "What events occurred after Customer CUST001's upgrade?",
            ],
            "multi_hop_temporal": [
                "Which customers upgraded within 30 days of signup?",
                "What led to Customer CUST003's cancellation?",
            ],
        }

        # Check if required environment variables are set
        self._check_env_vars()

    def _check_env_vars(self):
        """Check if required environment variables are set"""
        required_vars = ["SERPER_API_KEY", "JINA_API_KEY"]
        optional_vars = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]

        missing_required = [var for var in required_vars if not os.getenv(var)]
        if missing_required:
            print(
                f"⚠️  Warning: Missing required environment variables: {', '.join(missing_required)}"
            )
            print("   Some tests may fail. Please set these variables.")

        if TemporalKGTool:
            missing_optional = [var for var in optional_vars if not os.getenv(var)]
            if missing_optional:
                print(
                    f"⚠️  Warning: Missing Neo4j environment variables: {', '.join(missing_optional)}"
                )
                print("   TKG tests will be skipped.")

    def run_baseline_test(self, query: str) -> Tuple[str, float, Dict]:
        """Run query without TKG"""
        try:
            search_tool = OpenDeepSearchTool(
                model_name=os.getenv(
                    "LITELLM_SEARCH_MODEL_ID", "openrouter/google/gemini-2.0-flash-001"
                ),
                reranker="jina",
            )

            if not search_tool.is_initialized:
                search_tool.setup()

            start_time = time.time()
            result = search_tool.forward(query)
            latency = time.time() - start_time

            return result, latency, {"tool_calls": 1, "mode": "baseline"}
        except Exception as e:
            return f"Error: {str(e)}", 0.0, {"error": str(e), "mode": "baseline"}

    def run_tkg_test(self, query: str) -> Tuple[str, float, Dict]:
        """Run query with TKG integration"""
        if not TemporalKGTool:
            return (
                "TKG not available",
                0.0,
                {"error": "TemporalKGTool not imported", "mode": "tkg_enhanced"},
            )

        # Check Neo4j credentials
        if not all(
            [
                os.getenv("NEO4J_URI"),
                os.getenv("NEO4J_USERNAME"),
                os.getenv("NEO4J_PASSWORD"),
            ]
        ):
            return (
                "Neo4j not configured",
                0.0,
                {"error": "Neo4j credentials missing", "mode": "tkg_enhanced"},
            )

        try:
            # Create tools
            search_tool = OpenDeepSearchTool(
                model_name=os.getenv(
                    "LITELLM_SEARCH_MODEL_ID", "openrouter/google/gemini-2.0-flash-001"
                ),
                reranker="jina",
            )

            if not search_tool.is_initialized:
                search_tool.setup()

            temporal_tool = TemporalKGTool(
                neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "password"),
            )

            # Create multi-tool agent
            model = LiteLLMModel(
                model_id=os.getenv(
                    "LITELLM_ORCHESTRATOR_MODEL_ID",
                    "openrouter/google/gemini-2.0-flash-001",
                )
            )
            agent = CodeAgent(tools=[search_tool, temporal_tool], model=model)

            start_time = time.time()
            result = agent.run(query)
            latency = time.time() - start_time

            # Extract tool usage info from agent logs if available
            tool_info = {
                "mode": "tkg_enhanced",
                "tools_available": ["search", "temporal_kg"],
                "agent_type": "CodeAgent",
            }

            return result, latency, tool_info
        except Exception as e:
            return f"Error: {str(e)}", 0.0, {"error": str(e), "mode": "tkg_enhanced"}

    def compare_single_query(self, query: str, category: str):
        """Compare a single query between baseline and TKG"""
        print(f"\n  Query: {query}")

        # Baseline test
        baseline_result, baseline_latency, baseline_info = self.run_baseline_test(query)
        self.results["baseline"].append(
            {
                "query": query,
                "category": category,
                "latency": baseline_latency,
                "result_length": len(baseline_result)
                if isinstance(baseline_result, str)
                else 0,
                "info": baseline_info,
            }
        )

        if "error" in baseline_info:
            print(f"    ✗ Baseline error: {baseline_info['error']}")
        else:
            print(f"    ✓ Baseline: {baseline_latency:.2f}s")

        # TKG test - only run if it makes sense for the query type
        if category in ["temporal_queries", "multi_hop_temporal"] and TemporalKGTool:
            tkg_result, tkg_latency, tkg_info = self.run_tkg_test(query)
            self.results["tkg_enhanced"].append(
                {
                    "query": query,
                    "category": category,
                    "latency": tkg_latency,
                    "result_length": len(tkg_result)
                    if isinstance(tkg_result, str)
                    else 0,
                    "info": tkg_info,
                }
            )

            if "error" in tkg_info:
                print(f"    ✗ TKG error: {tkg_info['error']}")
            else:
                print(f"    ✓ TKG: {tkg_latency:.2f}s")

                # Quick comparison
                if baseline_latency > 0:
                    improvement = (
                        (baseline_latency - tkg_latency) / baseline_latency
                    ) * 100
                    print(f"    📈 Latency difference: {improvement:+.1f}%")
        else:
            print(f"    ⏭️  Skipping TKG test (not applicable for {category})")

    def compare_all_queries(self):
        """Run comparison for all test queries"""
        print("🔄 Starting TKG comparison evaluation...\n")

        for category, queries in self.test_queries.items():
            print(f"\n📊 Testing {category}:")

            for query in queries:
                self.compare_single_query(query, category)

        # Save results
        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save results to JSON file"""
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)

        output_file = (
            f"results/tkg_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

    def print_summary(self):
        """Print comparison summary"""
        print("\n" + "=" * 50)
        print("📊 COMPARISON SUMMARY")
        print("=" * 50)

        # Calculate averages by category
        for category in self.test_queries.keys():
            baseline_latencies = [
                r["latency"]
                for r in self.results["baseline"]
                if r["category"] == category and r["latency"] > 0
            ]
            tkg_latencies = [
                r["latency"]
                for r in self.results["tkg_enhanced"]
                if r["category"] == category and r["latency"] > 0
            ]

            if baseline_latencies:
                avg_baseline = sum(baseline_latencies) / len(baseline_latencies)
                print(f"\n{category}:")
                print(f"  Baseline avg: {avg_baseline:.2f}s")

                if tkg_latencies:
                    avg_tkg = sum(tkg_latencies) / len(tkg_latencies)
                    improvement = ((avg_baseline - avg_tkg) / avg_baseline) * 100
                    print(f"  TKG avg: {avg_tkg:.2f}s")
                    print(f"  Improvement: {improvement:+.1f}%")
                else:
                    print(f"  TKG: No results (skipped or failed)")

        # Print error summary if any
        baseline_errors = [
            r for r in self.results["baseline"] if "error" in r.get("info", {})
        ]
        tkg_errors = [
            r for r in self.results["tkg_enhanced"] if "error" in r.get("info", {})
        ]

        if baseline_errors or tkg_errors:
            print("\n⚠️  Errors encountered:")
            if baseline_errors:
                print(f"  Baseline: {len(baseline_errors)} errors")
            if tkg_errors:
                print(f"  TKG: {len(tkg_errors)} errors")


def main():
    """Main entry point"""
    print("OpenDeepSearch TKG Comparison Tool")
    print("==================================\n")

    # Quick environment check
    print("Environment check:")
    print(f"  SERPER_API_KEY: {'✓' if os.getenv('SERPER_API_KEY') else '✗'}")
    print(f"  JINA_API_KEY: {'✓' if os.getenv('JINA_API_KEY') else '✗'}")
    print(f"  OPENROUTER_API_KEY: {'✓' if os.getenv('OPENROUTER_API_KEY') else '✗'}")
    print(
        f"  NEO4J configured: {'✓' if all([os.getenv('NEO4J_URI'), os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD')]) else '✗'}"
    )
    print(f"  TemporalKGTool available: {'✓' if TemporalKGTool else '✗'}")

    # Run comparison
    comparison = TKGComparison()
    comparison.compare_all_queries()


if __name__ == "__main__":
    main()
