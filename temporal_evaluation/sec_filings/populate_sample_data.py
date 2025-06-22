# Not using this for ZEP yet

from neo4j import GraphDatabase
import os
from datetime import datetime, timedelta

def populate_sample_sec_data():
    """Populate Neo4j with sample SEC filing data for testing"""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USERNAME', 'neo4j'), 
              os.getenv('NEO4J_PASSWORD', 'maxx3169'))
    )
    
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create sample companies
        companies = [
            {"name": "Apple Inc.", "ticker": "AAPL"},
            {"name": "Meta Platforms, Inc.", "ticker": "META"},
            {"name": "Google LLC", "ticker": "GOOGL"},
            {"name": "Netflix Inc.", "ticker": "NFLX"},
            {"name": "Adobe Inc.", "ticker": "ADBE"}
        ]
        
        for company in companies:
            session.run("""
                CREATE (c:Company {name: $name, ticker: $ticker})
            """, company)
        
        # Create sample filings
        base_date = datetime(2024, 1, 1)
        filing_types = ["10-K", "10-Q", "8-K", "DEF 14A"]
        
        for i, company in enumerate(companies):
            for j, filing_type in enumerate(filing_types):
                filing_date = base_date + timedelta(days=i*30 + j*7)
                
                session.run("""
                    MATCH (c:Company {ticker: $ticker})
                    CREATE (f:Filing {
                        type: $type,
                        filing_date: date($date),
                        description: $description
                    })
                    CREATE (c)-[:FILED {filing_date: date($date)}]->(f)
                """, {
                    "ticker": company["ticker"],
                    "type": filing_type,
                    "date": filing_date.strftime("%Y-%m-%d"),
                    "description": f"{company['name']} {filing_type} filing"
                })
        
        # Verify data was created
        result = session.run("MATCH (n) RETURN count(n) as total")
        total_nodes = result.single()["total"]
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
        total_relationships = result.single()["total"]
        
        print(f"✅ Created {total_nodes} nodes and {total_relationships} relationships")
        
        # Show sample data
        result = session.run("""
            MATCH (c:Company)-[r:FILED]->(f:Filing)
            RETURN c.name, c.ticker, f.type, f.filing_date
            ORDER BY f.filing_date
            LIMIT 5
        """)
        
        print("\n📊 Sample data:")
        for record in result:
            print(f"  {record['c.name']} ({record['c.ticker']}) filed {record['f.type']} on {record['f.filing_date']}")
    
    driver.close()

if __name__ == "__main__":
    populate_sample_sec_data() 