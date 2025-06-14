import os
import subprocess
import json

def setup_complete_evaluation():
    """One-click setup for complete evaluation"""
    
    print("🚀 TEMPORAL KNOWLEDGE GRAPH EVALUATION SETUP")
    print("=" * 50)
    
    # Step 1: Check if datasets exist, if not create them
    datasets_to_create = [
        ('financial_data', 'Financial Markets Dataset'),
        ('sec_filings', 'SEC Filings Dataset'),
        # Add others as implemented
    ]
    
    for domain, description in datasets_to_create:
        dataset_file = f'datasets/{domain}.json'
        
        if os.path.exists(dataset_file):
            print(f"✅ {description} already exists")
        else:
            print(f"📊 Creating {description}...")
            try:
                subprocess.run(['python', f'{domain}/collect_data.py'], check=True)
                print(f"✅ {description} created")
            except Exception as e:
                print(f"❌ Error creating {description}: {e}")
    
    # Step 2: Load datasets into Neo4j
    print("\n📥 Loading datasets into Neo4j...")
    try:
        subprocess.run(['python', 'shared/neo4j_loader.py'], check=True)
        print("✅ All datasets loaded into Neo4j")
    except Exception as e:
        print(f"❌ Error loading datasets: {e}")
        return
    
    # Step 3: Generate queries for each domain
    print("\n❓ Generating evaluation queries...")
    for domain, _ in datasets_to_create:
        if os.path.exists(f'{domain}/generate_queries.py'):
            try:
                subprocess.run(['python', f'{domain}/generate_queries.py'], check=True)
                print(f"✅ {domain} queries generated")
            except Exception as e:
                print(f"❌ Error generating {domain} queries: {e}")
    
    # Step 4: Show dataset summaries
    print("\n📋 DATASET SUMMARIES:")
    print("-" * 30)
    
    for domain, description in datasets_to_create:
        dataset_file = f'datasets/{domain}.json'
        if os.path.exists(dataset_file):
            with open(dataset_file, 'r') as f:
                data = json.load(f)
                metadata = data['metadata']
                print(f"\n{description}:")
                print(f"  Entities: {metadata['total_entities']}")
                print(f"  Events: {metadata['total_events']}")
                print(f"  Event Types: {len(metadata['event_types'])}")
                print(f"  Date Range: {metadata['date_range']['start']} to {metadata['date_range']['end']}")
    
    print("\n🎉 SETUP COMPLETE!")
    print("\nNext steps:")
    print("1. Run individual evaluations: python financial_data/run_evaluation.py")
    print("2. Run all evaluations: python run_all_evaluations.py")
    print("3. View results in each domain's results/ folder")

if __name__ == "__main__":
    setup_complete_evaluation()
