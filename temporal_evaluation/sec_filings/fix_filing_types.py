import json
from neo4j import GraphDatabase

def fix_filing_types():
    """Fix filing types that are showing as Unknown"""
    
    # Load the original dataset to see the actual event structure
    with open('temporal_evaluation/datasets/sec_filings_enhanced.json', 'r') as f:
        dataset = json.load(f)
    
    # Check a few events to see their structure
    events = dataset.get('events', [])
    print("Sample event structures:")
    for i, event in enumerate(events[:3]):
        print(f"\nEvent {i+1}:")
        print(f"  event_type: {event.get('event_type')}")
        print(f"  details: {event.get('details', '')[:100]}...")
        print(f"  properties: {event.get('properties', {})}")
    
    # Connect to Neo4j and update filing types
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'maxx3169'))
    
    with driver.session() as session:
        # Update filing types based on event details or properties
        for event in events[:100]:  # Test with first 100 events
            event_id = event.get('id')
            details = event.get('details', '')
            event_type = event.get('event_type', '')
            properties = event.get('properties', {})
            
            # Try to extract filing type from various fields
            filing_type = "Unknown"
            
            # Check event_type field
            if any(ft in event_type for ft in ['10-K', '10-Q', '8-K', 'DEF 14A']):
                for ft in ['10-K', '10-Q', '8-K', 'DEF 14A']:
                    if ft in event_type:
                        filing_type = ft
                        break
            
            # Check details field
            elif any(ft in details for ft in ['10-K', '10-Q', '8-K', 'DEF 14A']):
                for ft in ['10-K', '10-Q', '8-K', 'DEF 14A']:
                    if ft in details:
                        filing_type = ft
                        break
            
            # Check properties if it's a dict
            elif isinstance(properties, dict):
                form_type = properties.get('form_type', properties.get('filing_type', ''))
                if form_type and form_type != 'Unknown':
                    filing_type = form_type
            
            # Update the filing type in Neo4j
            if filing_type != "Unknown":
                session.run("""
                    MATCH (f:Filing {accession_number: $event_id})
                    SET f.type = $filing_type
                """, {
                    "event_id": event_id,
                    "filing_type": filing_type
                })
        
        # Check results
        result = session.run("""
            MATCH (c:Company)-[:FILED]->(f:Filing)
            WHERE f.type <> "Unknown"
            RETURN c.name, c.ticker, f.type, f.filing_date
            ORDER BY f.filing_date DESC
            LIMIT 10
        """)
        
        print("\n📊 Updated filing data:")
        for record in result:
            print(f"  {record['c.name']} ({record['c.ticker']}) - {record['f.type']} on {record['f.filing_date']}")
    
    driver.close()

if __name__ == "__main__":
    fix_filing_types() 