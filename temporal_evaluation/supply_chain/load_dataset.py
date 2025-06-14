import os
import sys

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from neo4j_loader import Neo4jLoader

def load_supply_chain_dataset():
    """Load supply chain dataset into Neo4j"""
    
    dataset_file = 'datasets/supply_chain.json'
    
    if not os.path.exists(dataset_file):
        print(f"❌ Dataset file not found: {dataset_file}")
        print("Run 'python supply_chain/collect_data.py' first to create the dataset")
        return
    
    loader = Neo4jLoader()
    loader.load_dataset(dataset_file, clear_first=True)
    loader.close()
    
    print("✅ Supply chain dataset loaded into Neo4j")

if __name__ == "__main__":
    load_supply_chain_dataset()
