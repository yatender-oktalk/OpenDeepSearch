# Test script to check database content
from neo4j import GraphDatabase
import os

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    auth=(os.getenv('NEO4J_USERNAME', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'maxx3169'))
)

with driver.session() as session:
    # Check schema
    result = session.run("CALL db.schema.visualization()")
    print("Schema:", [record.data() for record in result])
    
    # Check sample data
    result = session.run("MATCH (c:Company)-[:FILED]->(f:Filing) RETURN c.name, c.ticker, f.type, f.filing_date, f.description LIMIT 5")
    records = [record.data() for record in result]
    print("Sample data:", records)
    
    # Check if data exists
    result = session.run("MATCH (c:Company) RETURN count(c) as company_count")
    company_count = result.single()['company_count']
    
    result = session.run("MATCH (f:Filing) RETURN count(f) as filing_count")
    filing_count = result.single()['filing_count']
    
    print(f"Companies: {company_count}, Filings: {filing_count}")

driver.close()
