import sys
import os
sys.path.append('src')

from opendeepsearch.temporal_kg_tool import TemporalKGTool

# Test the tool
tool = TemporalKGTool(
    neo4j_uri="bolt://localhost:7687",
    username="neo4j", 
    password="maxx3169",  # Use your actual password
    model_name="test"
)

# Test queries
test_queries = [
    "What happened to Customer CUST001?",
    "Show me Customer CUST001 between 2023 and 2024"
]

for query in test_queries:
    print(f"\nQuery: {query}")
    result = tool.forward(query)
    print(f"Result: {result}")