import subprocess
import os

def create_all_datasets():
    """Create all datasets"""
    
    domains = [
        ('financial_data', 'Financial Markets'),
        ('sec_filings', 'SEC Filings'),
        ('clinical_trials', 'Clinical Trials'),
        ('supply_chain', 'Supply Chain')
    ]
    
    print("🚀 CREATING ALL TEMPORAL DATASETS")
    print("=" * 50)
    
    for domain, description in domains:
        print(f"\n📊 Creating {description} Dataset...")
        
        try:
            subprocess.run(['python', f'{domain}/collect_data.py'], check=True)
            print(f"✅ {description} dataset created")
        except Exception as e:
            print(f"❌ Error creating {description} dataset: {e}")
    
    print(f"\n🎉 All datasets created!")
    print(f"📁 Check the 'datasets/' folder for JSON files")

if __name__ == "__main__":
    create_all_datasets()
