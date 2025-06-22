from neo4j import GraphDatabase
import os
from datetime import datetime, timedelta
import random

def create_rich_sec_data():
    """Create comprehensive SEC filing data"""
    
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'maxx3169'))
    
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared")
        
        # Major companies with real tickers
        companies = [
            {"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology"},
            {"name": "Meta Platforms Inc.", "ticker": "META", "sector": "Technology"},
            {"name": "Alphabet Inc.", "ticker": "GOOGL", "sector": "Technology"},
            {"name": "Microsoft Corporation", "ticker": "MSFT", "sector": "Technology"},
            {"name": "Amazon.com Inc.", "ticker": "AMZN", "sector": "Consumer Discretionary"},
            {"name": "Tesla Inc.", "ticker": "TSLA", "sector": "Consumer Discretionary"},
            {"name": "Netflix Inc.", "ticker": "NFLX", "sector": "Communication"},
            {"name": "Adobe Inc.", "ticker": "ADBE", "sector": "Technology"},
            {"name": "Salesforce Inc.", "ticker": "CRM", "sector": "Technology"},
            {"name": "NVIDIA Corporation", "ticker": "NVDA", "sector": "Technology"},
            {"name": "PayPal Holdings Inc.", "ticker": "PYPL", "sector": "Financial Services"},
            {"name": "Intel Corporation", "ticker": "INTC", "sector": "Technology"},
            {"name": "Cisco Systems Inc.", "ticker": "CSCO", "sector": "Technology"},
            {"name": "Oracle Corporation", "ticker": "ORCL", "sector": "Technology"},
            {"name": "IBM Corporation", "ticker": "IBM", "sector": "Technology"}
        ]
        
        # Create companies
        for company in companies:
            session.run("""
                CREATE (c:Company {
                    name: $name,
                    ticker: $ticker,
                    sector: $sector
                })
            """, company)
        
        print(f"Created {len(companies)} companies")
        
        # Create 5 years of filings (2020-2024)
        filing_types = ["10-K", "10-Q", "8-K", "DEF 14A", "S-1", "S-3", "13F"]
        
        filing_count = 0
        for year in range(2020, 2025):  # 5 years
            for company in companies:
                # Annual 10-K (once per year)
                filing_date = datetime(year, random.randint(1, 3), random.randint(1, 28))
                session.run("""
                    MATCH (c:Company {ticker: $ticker})
                    CREATE (f:Filing {
                        type: "10-K",
                        filing_date: date($date),
                        description: $description,
                        accession_number: $accession
                    })
                    CREATE (c)-[:FILED {date: date($date)}]->(f)
                """, {
                    "ticker": company["ticker"],
                    "date": filing_date.strftime("%Y-%m-%d"),
                    "description": f"{company['name']} Annual Report (Form 10-K)",
                    "accession": f"{random.randint(1000000, 9999999)}-{year}-{random.randint(10000, 99999)}"
                })
                filing_count += 1
                
                # Quarterly 10-Q (4 times per year)
                for quarter in range(1, 5):
                    q_date = datetime(year, quarter*3, random.randint(1, 28))
                    session.run("""
                        MATCH (c:Company {ticker: $ticker})
                        CREATE (f:Filing {
                            type: "10-Q",
                            filing_date: date($date),
                            description: $description,
                            accession_number: $accession
                        })
                        CREATE (c)-[:FILED {date: date($date)}]->(f)
                    """, {
                        "ticker": company["ticker"],
                        "date": q_date.strftime("%Y-%m-%d"),
                        "description": f"{company['name']} Quarterly Report Q{quarter} {year}",
                        "accession": f"{random.randint(1000000, 9999999)}-{year}-{random.randint(10000, 99999)}"
                    })
                    filing_count += 1
                
                # Random 8-K filings (2-5 per year)
                for _ in range(random.randint(2, 5)):
                    k_date = datetime(year, random.randint(1, 12), random.randint(1, 28))
                    session.run("""
                        MATCH (c:Company {ticker: $ticker})
                        CREATE (f:Filing {
                            type: "8-K",
                            filing_date: date($date),
                            description: $description,
                            accession_number: $accession
                        })
                        CREATE (c)-[:FILED {date: date($date)}]->(f)
                    """, {
                        "ticker": company["ticker"],
                        "date": k_date.strftime("%Y-%m-%d"),
                        "description": f"{company['name']} Current Report (Form 8-K)",
                        "accession": f"{random.randint(1000000, 9999999)}-{year}-{random.randint(10000, 99999)}"
                    })
                    filing_count += 1
        
        print(f"Created {filing_count} filings across 5 years")
        
        # Final count
        result = session.run("MATCH (n) RETURN count(n) as total")
        total_nodes = result.single()['total']
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
        total_rels = result.single()['total']
        
        print(f"\n✅ Rich database created: {total_nodes} nodes, {total_rels} relationships")
        
        # Show sample data
        result = session.run("""
            MATCH (c:Company)-[:FILED]->(f:Filing)
            RETURN c.name, c.ticker, f.type, f.filing_date
            ORDER BY f.filing_date DESC
            LIMIT 10
        """)
        
        print("\n📊 Recent filings sample:")
        for record in result:
            print(f"  {record['c.name']} ({record['c.ticker']}) - {record['f.type']} on {record['f.filing_date']}")
    
    driver.close()

if __name__ == "__main__":
    create_rich_sec_data() 