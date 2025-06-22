import os
import sys

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from neo4j_loader import Neo4jLoader

def load_financial_dataset():
    """Load financial dataset into Neo4j"""
    
    dataset_file = 'datasets/financial_data.json'
    
    if not os.path.exists(dataset_file):
        print(f"❌ Dataset file not found: {dataset_file}")
        print("Run 'python financial_data/collect_data.py' first to create the dataset")
        return
    
    loader = Neo4jLoader()
    loader.load_dataset(dataset_file, clear_first=True)
    loader.close()
    
    print("✅ Financial dataset loaded into Neo4j")

if __name__ == "__main__":
    load_financial_dataset()
