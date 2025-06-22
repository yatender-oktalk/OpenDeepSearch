# Create: temporal_evaluation/zep/load_sec_data_to_zep.py
import json
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from temporal_evaluation.zep.tools.zep_temporal_kg_tool import ZepTemporalKGTool

def load_sec_filings_to_zep():
    """Load SEC filing data into Zep's temporal knowledge graph"""
    
    print("🚀 Loading SEC filing data into Zep...")
    
    # Initialize Zep tool (you'll need to get API key from Zep)
    zep_tool = ZepTemporalKGTool(
        api_key=os.getenv('ZEP_API_KEY'),  # Get from https://www.getzep.com/
        base_url=os.getenv('ZEP_BASE_URL')  # Optional: for self-hosted
    )
    
    # Load SEC filing data
    try:
        with open('temporal_evaluation/datasets/sec_filings_enhanced.json', 'r') as f:
            sec_data = json.load(f)
        
        print(f"📊 Found {len(sec_data)} SEC filings to load into Zep")
        
        # Process and load data
        loaded_count = 0
        for filing in sec_data:
            # Convert to required format
            filing_data = {
                'company_name': filing.get('company_name', 'Unknown'),
                'ticker': filing.get('ticker', 'N/A'),
                'filing_type': filing.get('filing_type', 'Unknown'),
                'filing_date': filing.get('filing_date', ''),
                'description': filing.get('description', '')
            }
            
            # Add to Zep's temporal knowledge graph
            if zep_tool.add_sec_filing_data(filing_data):
                loaded_count += 1
                
            # Progress update
            if loaded_count % 1000 == 0:
                print(f"  Loaded {loaded_count} filings into Zep...")
        
        print(f"✅ Successfully loaded {loaded_count} SEC filings into Zep")
        print("🧠 Zep is now building temporal relationships and patterns...")
        
    except FileNotFoundError:
        print("❌ SEC filing data file not found")
    except Exception as e:
        print(f"❌ Error loading data: {e}")

if __name__ == "__main__":
    load_sec_filings_to_zep()