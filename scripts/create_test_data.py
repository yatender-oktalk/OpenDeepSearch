from neo4j import GraphDatabase

def create_sample_data():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "maxx3169"))
    
    with driver.session() as session:
        # Create one simple customer with a few events
        session.run("""
        CREATE (c:Customer {id: "CUST001", name: "Test Corp"})
        CREATE (s:Event:Signup {date: datetime("2023-01-15"), plan: "basic"})
        CREATE (u:Event:Upgrade {date: datetime("2023-06-01"), from_plan: "basic", to_plan: "premium"})
        CREATE (c)-[:PERFORMED {timestamp: datetime("2023-01-15")}]->(s)
        CREATE (c)-[:PERFORMED {timestamp: datetime("2023-06-01")}]->(u)
        """)
    
    driver.close()
    print("Test data created!")

if __name__ == "__main__":
    create_sample_data()
