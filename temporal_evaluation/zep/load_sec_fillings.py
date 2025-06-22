# Replace the entire content of temporal_evaluation/zep/load_sec_fillings.py:
from tools.zep_temporal_kg_tool import ZepTemporalKGTool
import json
import time

def load_sec_filings():
    """Load the sec_filings.json dataset (587 events)"""
    print("🚀 Loading sec_filings.json into Zep...")
    
    tool = ZepTemporalKGTool()
    
    # Load the dataset
    with open('../datasets/sec_filings.json', 'r') as f:
        sec_data = json.load(f)
    
    print(f"📊 Metadata: {sec_data['metadata']['total_events']} events, {sec_data['metadata']['total_entities']} entities")
    print(f"📊 Date range: {sec_data['metadata']['date_range']['start']} to {sec_data['metadata']['date_range']['end']}")
    
    # Create entity lookup for company names
    entities = {entity['id']: entity for entity in sec_data['entities']}
    
    # Extract filings from events
    events = sec_data['events']
    print(f"📊 Processing {len(events)} SEC filing events...")
    
    # Load first 150 events for meaningful analysis
    events_to_load = events[:150]
    print(f"📊 Loading {len(events_to_load)} filing events...")
    
    loaded_count = 0
    for i, event in enumerate(events_to_load):
        try:
            # Get company info from entities
            entity_id = event['entity_id']
            entity = entities.get(entity_id, {})
            company_name = entity.get('name', f"Company {entity_id}")
            ticker = entity.get('properties', {}).get('ticker', entity_id)
            
            # Extract filing info
            filing_data = {
                'company': company_name,
                'ticker': ticker,
                'filing_type': event['properties']['form_type'],
                'date': event['date'],
                'description': event['details']
            }
            
            success = tool.add_sec_filing_data(filing_data)
            
            if success:
                loaded_count += 1
                
            if i % 25 == 0:
                print(f"  ✅ Loaded {i+1}/{len(events_to_load)} - {company_name} {event['properties']['form_type']}")
                time.sleep(1)  # Brief pause
                
        except Exception as e:
            print(f"  ❌ Error loading event {i}: {e}")
    
    print(f"🎉 Successfully loaded {loaded_count} SEC filings!")
    print("⏳ Waiting 30 seconds for Zep to process relationships...")
    time.sleep(30)
    
    return tool

if __name__ == "__main__":
    load_sec_filings()