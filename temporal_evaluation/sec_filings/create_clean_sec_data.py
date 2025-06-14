from neo4j import GraphDatabase
import os
from datetime import datetime, timedelta

def create_clean_sec_data():
    """Create clean SEC filing data with simple schema"""
    
    driver = GraphDatabase.driver(
        'bolt://localhost:7687',
        auth=('neo4j', 'maxx3169')
    )
    
    with driver.session() as session:
        # Verify database is empty
        result = session.run("MATCH (n) RETURN count(n) as total")
        if result.single()['total'] > 0:
            print("❌ Database not empty! Please clear it first.")
            return
        
        print("✅ Database is clean. Creating SEC data...")
        
        # Create companies
        companies = [
            {"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology"},
            {"name": "Meta Platforms Inc.", "ticker": "META", "sector": "Technology"},
            {"name": "Alphabet Inc.", "ticker": "GOOGL", "sector": "Technology"},
            {"name": "Netflix Inc.", "ticker": "NFLX", "sector": "Communication"},
            {"name": "Adobe Inc.", "ticker": "ADBE", "sector": "Technology"}
        ]
        
        for company in companies:
            session.run("""
                CREATE (c:Company {
                    name: $name,
                    ticker: $ticker,
                    sector: $sector
                })
            """, company)
        
        print(f"Created {len(companies)} companies")
        
        # Create filings for each company
        filing_types = ["10-K", "10-Q", "8-K", "DEF 14A"]
        base_date = datetime(2024, 1, 1)
        
        filing_count = 0
        for i, company in enumerate(companies):
            for j, filing_type in enumerate(filing_types):
                # Stagger filing dates
                filing_date = base_date + timedelta(days=i*15 + j*30)
                
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
                    "ticker": company["ticker"],
                    "type": filing_type,
                    "date": filing_date.strftime("%Y-%m-%d"),
                    "description": f"{company['name']} {filing_type} Annual/Quarterly Report",
                    "accession": f"000{i}{j:02d}-24-{filing_date.strftime('%m%d')}"
                })
                filing_count += 1
        
        print(f"Created {filing_count} filings")
        
        # Verify data
        result = session.run("""
            MATCH (c:Company)-[:FILED]->(f:Filing)
            RETURN c.name, c.ticker, f.type, f.filing_date
            ORDER BY f.filing_date
            LIMIT 5
        """)
        
        print("\n📊 Sample data:")
        for record in result:
            print(f"  {record['c.name']} ({record['c.ticker']}) - {record['f.type']} on {record['f.filing_date']}")
        
        # Final count
        result = session.run("MATCH (n) RETURN count(n) as total")
        total_nodes = result.single()['total']
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
        total_rels = result.single()['total']
        
        print(f"\n✅ Database populated: {total_nodes} nodes, {total_rels} relationships")
    
    driver.close()

if __name__ == "__main__":
    create_clean_sec_data() 