import json
import os
from neo4j import GraphDatabase
from datetime import datetime
import re

def analyze_dataset_filing_types():
    """Analyze the dataset to understand filing type distribution"""
    
    # Load dataset
    with open('temporal_evaluation/datasets/sec_filings_enhanced.json', 'r') as f:
        dataset = json.load(f)
    
    events = dataset.get('events', [])
    
    print(f"🔍 Analyzing {len(events)} events for filing types...")
    
    # Analyze form_type distribution
    form_type_stats = {}
    missing_form_type = 0
    empty_form_type = 0
    has_form_type = 0
    
    # Check different sources of filing type info
    description_patterns = {}
    
    for i, event in enumerate(events[:100]):  # Sample first 100
        props = event.get('properties', {})
        form_type = props.get('form_type')
        description = event.get('details', '')
        
        # Count form_type status
        if form_type is None:
            missing_form_type += 1
        elif form_type == '' or form_type == 'Unknown':
            empty_form_type += 1  
        else:
            has_form_type += 1
            form_type_stats[form_type] = form_type_stats.get(form_type, 0) + 1
        
        # Extract patterns from description
        if description:
            # Look for "filed X" pattern
            match = re.search(r'filed\s+([A-Z0-9/-]+)', description)
            if match:
                desc_type = match.group(1)
                description_patterns[desc_type] = description_patterns.get(desc_type, 0) + 1
        
        # Debug first few entries
        if i < 5:
            print(f"\nEvent {i}:")
            print(f"  Description: {description}")
            print(f"  Properties form_type: '{form_type}'")
            print(f"  Properties keys: {list(props.keys())}")
    
    print(f"\n📊 FILING TYPE ANALYSIS (sample of 100):")
    print(f"  ✅ Has form_type: {has_form_type}")
    print(f"  ❌ Missing form_type: {missing_form_type}")
    print(f"  🔄 Empty/Unknown form_type: {empty_form_type}")
    
    print(f"\n📋 Form Types Found:")
    for form_type, count in sorted(form_type_stats.items()):
        print(f"  {form_type}: {count}")
    
    print(f"\n📝 Description Patterns:")
    for pattern, count in sorted(description_patterns.items()):
        print(f"  'filed {pattern}': {count}")
    
    return form_type_stats, description_patterns

def load_sec_dataset_with_smart_extraction():
    """Enhanced loading with smart filing type extraction"""
    
    # Analyze first
    print("🔍 Analyzing dataset...")
    form_type_stats, desc_patterns = analyze_dataset_filing_types()
    
    # Load dataset
    with open('temporal_evaluation/datasets/sec_filings_enhanced.json', 'r') as f:
        dataset = json.load(f)
    
    # Connect to Neo4j
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'maxx3169'))
    
    def extract_filing_type_smart(event):
        """Smart filing type extraction with multiple fallbacks"""
        
        props = event.get('properties', {})
        
        # Method 1: Direct from properties.form_type
        form_type = props.get('form_type')
        if form_type and form_type != 'Unknown' and form_type.strip():
            return form_type.strip()
        
        # Method 2: Extract from description using regex
        description = event.get('details', '')
        if description:
            # Pattern: "Apple Inc. filed 4" -> "4"
            match = re.search(r'filed\s+([A-Z0-9/-]+)', description)
            if match:
                extracted_type = match.group(1)
                # Validate it's a known SEC form
                known_forms = ['10-K', '10-Q', '8-K', 'DEF 14A', '4', '3', '5', 'S-1', 'S-3', '13F', '11-K']
                if extracted_type in known_forms:
                    return extracted_type
                # Handle variants
                if extracted_type.startswith('10-'):
                    return extracted_type
                if extracted_type.startswith('8-'):
                    return extracted_type
        
        # Method 3: Check event_type
        event_type = event.get('event_type', '')
        if 'filing' in event_type.lower():
            # Try to extract from event_type
            for form in ['10-K', '10-Q', '8-K', 'DEF 14A', '4', '3', '5']:
                if form in event_type:
                    return form
        
        # Method 4: Check category in properties
        category = props.get('category', '')
        if category:
            category_mapping = {
                'annual_report': '10-K',
                'quarterly_report': '10-Q', 
                'current_report': '8-K',
                'insider_trading': '4',
                'proxy_statement': 'DEF 14A'
            }
            if category in category_mapping:
                return category_mapping[category]
        
        # Method 5: Default based on common patterns
        return 'Unknown'
    
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("🗑️ Database cleared")
        
        # Create indexes
        session.run("CREATE INDEX company_ticker IF NOT EXISTS FOR (c:Company) ON (c.ticker)")
        session.run("CREATE INDEX filing_date IF NOT EXISTS FOR (f:Filing) ON (f.filing_date)")
        session.run("CREATE INDEX filing_type IF NOT EXISTS FOR (f:Filing) ON (f.type)")
        print("📇 Indexes created")
        
        # Load companies
        entities = dataset.get('entities', [])
        companies = [e for e in entities if e.get('type') == 'public_company']
        
        for company in companies:
            props = company.get('properties', {})
            session.run("""
                CREATE (c:Company {
                    name: $name,
                    ticker: $ticker,
                    cik: $cik,
                    sector: $sector,
                    exchange: $exchange
                })
            """, {
                "name": company.get('name', 'Unknown'),
                "ticker": company.get('id', 'UNK'),
                "cik": props.get('cik', ''),
                "sector": props.get('sector', 'Unknown'),
                "exchange": props.get('exchange', 'Unknown')
            })
        
        print(f"✅ Created {len(companies)} company nodes")
        
        # Load events with smart type extraction
        events = dataset.get('events', [])
        print(f"📄 Loading {len(events)} events with smart type extraction...")
        
        filing_count = 0
        type_extraction_stats = {}
        
        for i, event in enumerate(events):
            if i % 1000 == 0:
                print(f"  Progress: {i}/{len(events)} ({i/len(events)*100:.1f}%)")
            
            # Smart filing type extraction
            filing_type = extract_filing_type_smart(event)
            type_extraction_stats[filing_type] = type_extraction_stats.get(filing_type, 0) + 1
            
            # Parse date
            date_str = event.get('date', event.get('timestamp', ''))
            try:
                if 'T' in date_str:
                    filing_date = datetime.fromisoformat(date_str.replace('Z', '')).date()
                else:
                    filing_date = datetime.strptime(date_str[:10], '%Y-%m-%d').date()
            except:
                continue
            
            # Get properties
            props = event.get('properties', {})
            entity_id = event.get('entity_id', '')
            
            # Create filing with extracted type
            try:
                session.run("""
                    MATCH (c:Company {ticker: $ticker})
                    CREATE (f:Filing {
                        type: $type,
                        filing_date: date($date),
                        description: $description,
                        accession_number: $accession,
                        file_size: $file_size,
                        category: $category,
                        quarter: $quarter,
                        fiscal_year: $fiscal_year
                    })
                    CREATE (c)-[:FILED {
                        date: date($date),
                        filing_type: $type
                    }]->(f)
                """, {
                    "ticker": entity_id,
                    "type": filing_type,  # Use smart-extracted type
                    "date": filing_date.strftime("%Y-%m-%d"),
                    "description": event.get('details', ''),
                    "accession": props.get('accession_number', f"acc_{filing_count}"),
                    "file_size": props.get('file_size', 0),
                    "category": props.get('category', 'unknown'),
                    "quarter": props.get('quarter', ''),
                    "fiscal_year": props.get('fiscal_year', '')
                })
                filing_count += 1
            except:
                continue
        
        print(f"✅ Created {filing_count} filing nodes")
        
        # Show extraction statistics
        print(f"\n📊 SMART TYPE EXTRACTION RESULTS:")
        for filing_type, count in sorted(type_extraction_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / sum(type_extraction_stats.values())) * 100
            print(f"  {filing_type}: {count} ({percentage:.1f}%)")
        
        # Verify the specific case you mentioned
        print(f"\n🔍 Checking Apple Form 4 filings:")
        result = session.run("""
            MATCH (c:Company {ticker: 'AAPL'})-[:FILED]->(f:Filing {type: '4'})
            RETURN f.filing_date, f.description, f.accession_number
            ORDER BY f.filing_date DESC
            LIMIT 5
        """)
        
        for record in result:
            print(f"  {record['f.filing_date']} - {record['f.description']} - {record['f.accession_number']}")
        
        # Final verification
        verification = session.run("""
            MATCH (f:Filing)
            RETURN f.type as filing_type, count(*) as count
            ORDER BY count DESC
        """)
        
        print(f"\n✅ FINAL DATABASE FILING TYPES:")
        total_filings = 0
        for record in verification:
            count = record['count']
            total_filings += count
            print(f"  {record['filing_type']}: {count}")
        
        unknown_count = session.run("MATCH (f:Filing {type: 'Unknown'}) RETURN count(*) as count").single()['count']
        unknown_percentage = (unknown_count / total_filings) * 100 if total_filings > 0 else 0
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total filings loaded: {total_filings}")
        print(f"  Unknown types: {unknown_count} ({unknown_percentage:.1f}%)")
        print(f"  Successfully typed: {total_filings - unknown_count} ({100 - unknown_percentage:.1f}%)")
    
    driver.close()

if __name__ == "__main__":
    load_sec_dataset_with_smart_extraction()