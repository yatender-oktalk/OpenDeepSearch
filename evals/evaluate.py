"""
Enhanced evaluation script with TKG comparison
"""

import argparse
from compare_tkg import TKGComparison
from run_benchmarks import BenchmarkRunner
from temporal_accuracy import evaluate_temporal_response


def main():
    parser = argparse.ArgumentParser(description="OpenDeepSearch Evaluation")
    parser.add_argument(
        "--mode",
        choices=["compare", "benchmark", "temporal"],
        default="compare",
        help="Evaluation mode",
    )
    parser.add_argument(
        "--benchmark",
        choices=["simpleqa", "frames", "temporal"],
        default="temporal",
        help="Benchmark to run",
    )

    args = parser.parse_args()

    if args.mode == "compare":
        # Run TKG comparison
        comparison = TKGComparison()
        comparison.compare_all_queries()

    elif args.mode == "benchmark":
        # Run specific benchmark
        runner = BenchmarkRunner(args.benchmark)
        runner.run_benchmark(use_tkg=False)
        runner.run_benchmark(use_tkg=True)
        runner.save_results()

    elif args.mode == "temporal":
        # Test temporal accuracy evaluation
        test_query = "What happened to Customer CUST001?"
        test_response = "Customer CUST001 signed up in January 2023, then upgraded their plan in February 2023, and made their first purchase in March 2023."

        scores = evaluate_temporal_response(test_query, test_response)
        print(f"Temporal evaluation scores: {scores}")


if __name__ == "__main__":
    main()
