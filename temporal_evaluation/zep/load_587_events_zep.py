#!/usr/bin/env python3
"""
Complete SEC Filings Data Loading Script

Loads ALL 587 events from sec_filings.json into Zep for comprehensive evaluation.
This ensures maximum data coverage and optimal knowledge graph performance.
"""

from tools.zep_temporal_kg_tool import ZepTemporalKGTool
import json
import time
from datetime import datetime

def load_all_sec_filings():
    """Load ALL 587 SEC filing events into Zep."""
    print("🚀 Loading ALL SEC filings (587 events) into Zep...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tool = ZepTemporalKGTool()
    
    # Load the dataset
    try:
        with open('../datasets/sec_filings.json', 'r') as f:
            sec_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: '../datasets/sec_filings.json' not found")
        print("   Make sure you're running from temporal_evaluation/zep/ directory")
        return None
    
    print(f"📊 Dataset loaded successfully!")
    print(f"   Total events: {sec_data['metadata']['total_events']}")
    print(f"   Total entities: {sec_data['metadata']['total_entities']}")
    print(f"   Date range: {sec_data['metadata']['date_range']['start']} to {sec_data['metadata']['date_range']['end']}")
    
    # Create entity lookup for company names
    entities = {entity['id']: entity for entity in sec_data['entities']}
    
    print(f"\n📊 Companies in dataset:")
    for entity_id, entity in entities.items():
        company_name = entity.get('name', entity_id)
        ticker = entity.get('properties', {}).get('ticker', 'N/A')
        print(f"   {entity_id}: {company_name} ({ticker})")
    
    # Extract all events
    events = sec_data['events']
    print(f"\n🎯 Loading ALL {len(events)} events into Zep...")
    
    # Analyze what we're about to load
    print(f"\n📊 Pre-loading analysis:")
    
    # Company distribution
    company_counts = {}
    filing_type_counts = {}
    year_counts = {}
    
    for event in events:
        # Company analysis
        entity_id = event['entity_id']
        entity = entities.get(entity_id, {})
        company_name = entity.get('name', entity_id)
        company_counts[company_name] = company_counts.get(company_name, 0) + 1
        
        # Filing type analysis
        filing_type = event['properties']['form_type']
        filing_type_counts[filing_type] = filing_type_counts.get(filing_type, 0) + 1
        
        # Year analysis
        year = event['date'][:4]
        year_counts[year] = year_counts.get(year, 0) + 1
    
    print(f"   Companies (top 10):")
    for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"     {company}: {count} filings")
    
    print(f"   Filing types:")
    for filing_type, count in sorted(filing_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     {filing_type}: {count} filings")
    
    print(f"   By year:")
    for year, count in sorted(year_counts.items()):
        print(f"     {year}: {count} filings")
    
    # Apple specific analysis
    apple_events = [e for e in events if e['entity_id'] == 'AAPL']
    apple_2024_events = [e for e in apple_events if '2024' in e['date']]
    apple_10q_2024 = [e for e in apple_2024_events if e['properties']['form_type'] == '10-Q']
    
    print(f"\n🍎 Apple-specific analysis:")
    print(f"   Total Apple events: {len(apple_events)}")
    print(f"   Apple 2024 events: {len(apple_2024_events)}")
    print(f"   Apple 2024 10-Q filings: {len(apple_10q_2024)}")
    
    if apple_10q_2024:
        print(f"   Apple 2024 10-Q dates:")
        for event in apple_10q_2024:
            print(f"     {event['date']}: {event['properties']['form_type']}")
    
    # Start loading process
    print(f"\n🔄 Starting data loading process...")
    
    loaded_count = 0
    failed_count = 0
    start_time = time.time()
    
    for i, event in enumerate(events):
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
            else:
                failed_count += 1
                print(f"  ⚠️  Failed to load: {company_name} {event['properties']['form_type']} {event['date']}")
            
            # Progress reporting
            if i % 50 == 0 and i > 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                eta = (len(events) - i) / rate / 60  # ETA in minutes
                
                print(f"  📈 Progress: {i+1}/{len(events)} ({(i+1)/len(events)*100:.1f}%)")
                print(f"     Loaded: {loaded_count}, Failed: {failed_count}")
                print(f"     Rate: {rate:.1f} events/sec, ETA: {eta:.1f} minutes")
                print(f"     Current: {company_name} {event['properties']['form_type']} ({event['date']})")
                
                # Brief pause to avoid overwhelming Zep
                time.sleep(2)
            
            # Shorter pause between individual loads
            if i % 10 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error loading event {i}: {e}")
            print(f"     Event: {event}")
    
    total_time = time.time() - start_time
    
    print(f"\n🎉 LOADING COMPLETED!")
    print(f"   Total time: {total_time/60:.1f} minutes")
    print(f"   Successfully loaded: {loaded_count}/{len(events)} events")
    print(f"   Failed: {failed_count}/{len(events)} events")
    print(f"   Success rate: {loaded_count/len(events)*100:.1f}%")
    
    # Wait for Zep to process all relationships
    print(f"\n⏳ Waiting 60 seconds for Zep to process all relationships...")
    time.sleep(60)
    
    # Test comprehensive queries
    print(f"\n🔍 Testing comprehensive queries...")
    
    test_queries = [
        "Show me Apple's exact 10-Q filing dates for 2024 and identify the day-of-week pattern",
        "List all companies that filed 10-K reports in 2024", 
        "Compare Microsoft vs Apple filing frequencies in 2024",
        "Find all 8-K filings from Tesla in 2025",
        "Show temporal patterns in SEC filings across all companies"
    ]
    
    for query in test_queries:
        print(f"\n🎯 Query: {query}")
        try:
            response = tool.forward(query)
            
            # Analyze response quality
            response_str = str(response)
            has_dates = bool(re.findall(r'\d{4}-\d{2}-\d{2}', response_str))
            has_companies = any(company.lower() in response_str.lower() 
                              for company in ['apple', 'microsoft', 'tesla', 'alphabet', 'meta'])
            
            print(f"   Response length: {len(response_str)} chars")
            print(f"   Contains specific dates: {'✅' if has_dates else '❌'}")
            print(f"   Contains company names: {'✅' if has_companies else '❌'}")
            
            if has_dates:
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', response_str)
                print(f"   Dates found: {dates[:5]}{'...' if len(dates) > 5 else ''}")
            
            # Show response snippet
            print(f"   Response: {response_str[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
    
    print(f"\n✅ ALL DATA LOADING AND TESTING COMPLETED!")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return tool

def verify_complete_loading(tool):
    """Verify that all data was loaded correctly."""
    print(f"\n🔍 VERIFICATION: Testing data completeness...")
    
    # Test each company
    companies = ['Apple', 'Microsoft', 'Alphabet', 'Tesla', 'Meta']
    
    for company in companies:
        try:
            response = tool.forward(f"List all {company} filings")
            response_str = str(response)
            
            # Count years mentioned
            years_found = set(re.findall(r'20\d{2}', response_str))
            
            print(f"   {company}: {len(response_str)} chars, years: {sorted(years_found)}")
            
        except Exception as e:
            print(f"   {company}: ❌ Error: {e}")

if __name__ == "__main__":
    # Import regex for testing
    import re
    
    # Load all data
    tool = load_all_sec_filings()
    
    if tool:
        # Verify loading
        verify_complete_loading(tool)
        
        print(f"\n🎯 Ready for comprehensive evaluation!")
        print(f"   Run: python debug_zep.py")
        print(f"   Then: python run_zep_evaluation_after_review.py")