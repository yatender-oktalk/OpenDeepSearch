import json
import os
from neo4j import GraphDatabase
from datetime import datetime

def load_sec_dataset():
    """Load existing SEC dataset into clean schema format"""
    
    # Check for dataset file
    dataset_files = [
        'temporal_evaluation/datasets/sec_filings_enhanced.json',
        'datasets/sec_filings_enhanced.json',
        'temporal_evaluation/datasets/sec_filings.json',
        'datasets/sec_filings.json'
    ]
    
    dataset_file = None
    for file_path in dataset_files:
        if os.path.exists(file_path):
            dataset_file = file_path
            break
    
    if not dataset_file:
        print("❌ SEC dataset file not found!")
        print("Looking for:")
        for f in dataset_files:
            print(f"  - {f}")
        return
    
    print(f"📊 Loading dataset from: {dataset_file}")
    
    # Load the dataset
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)
    
    print(f"Dataset structure: {list(dataset.keys())}")
    
    # Connect to Neo4j
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'maxx3169'))
    
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared")
        
        # Extract entities (companies)
        entities = dataset.get('entities', [])
        companies = [e for e in entities if e.get('type') == 'public_company' or 'company' in e.get('type', '').lower()]
        
        print(f"Found {len(companies)} companies in dataset")
        
        # Create company nodes
        for company in companies:
            # Extract properties from JSON string if needed
            props = company.get('properties', {})
            if isinstance(props, str):
                try:
                    props = json.loads(props)
                except:
                    props = {}
            
            session.run("""
                CREATE (c:Company {
                    name: $name,
                    ticker: $ticker,
                    sector: $sector
                })
            """, {
                "name": company.get('name', 'Unknown'),
                "ticker": company.get('id', props.get('ticker', 'UNK')),
                "sector": props.get('sector', 'Unknown')
            })
        
        print(f"Created {len(companies)} company nodes")
        
        # Extract events (SEC filings)
        events = dataset.get('events', [])
        sec_events = [e for e in events if 'filing' in e.get('event_type', '').lower() or 
                     e.get('domain') == 'sec_filings_enhanced']
        
        print(f"Found {len(sec_events)} SEC filing events")
        
        # Create filing nodes and relationships
        filing_count = 0
        for event in sec_events:
            # Parse event details to extract filing type
            details = event.get('details', '')
            event_type = event.get('event_type', '')
            
            # Try to extract filing type from details or event_type
            filing_type = "Unknown"
            for ft in ['10-K', '10-Q', '8-K', 'DEF 14A', 'S-1', 'S-3', '13F']:
                if ft in details or ft in event_type:
                    filing_type = ft
                    break
            
            # Get company ticker from entity_id
            entity_id = event.get('entity_id', '')
            
            # Parse timestamp
            timestamp = event.get('timestamp', event.get('date', ''))
            if timestamp:
                try:
                    if 'T' in timestamp:
                        filing_date = datetime.fromisoformat(timestamp.replace('Z', '')).date()
                    else:
                        filing_date = datetime.strptime(timestamp[:10], '%Y-%m-%d').date()
                except:
                    filing_date = datetime(2024, 1, 1).date()
            else:
                filing_date = datetime(2024, 1, 1).date()
            
            # Create filing and relationship
            session.run("""
                MATCH (c:Company {ticker: $ticker})
                CREATE (f:Filing {
                    type: $type,
                    filing_date: date($date),
                    description: $description,
                    accession_number: $accession
                })
                CREATE (c)-[:FILED {date: date($date)}]->(f)
            """, {
                "ticker": entity_id,
                "type": filing_type,
                "date": filing_date.strftime("%Y-%m-%d"),
                "description": details,
                "accession": event.get('id', f"acc_{filing_count}")
            })
            filing_count += 1
        
        print(f"Created {filing_count} filing nodes and relationships")
        
        # Final count
        result = session.run("MATCH (n) RETURN count(n) as total")
        total_nodes = result.single()['total']
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
        total_rels = result.single()['total']
        
        print(f"\n✅ Dataset loaded: {total_nodes} nodes, {total_rels} relationships")
        
        # Show sample data
        result = session.run("""
            MATCH (c:Company)-[:FILED]->(f:Filing)
            RETURN c.name, c.ticker, f.type, f.filing_date
            ORDER BY f.filing_date DESC
            LIMIT 10
        """)
        
        print("\n📊 Sample loaded data:")
        for record in result:
            print(f"  {record['c.name']} ({record['c.ticker']}) - {record['f.type']} on {record['f.filing_date']}")
    
    driver.close()

if __name__ == "__main__":
    load_sec_dataset() 