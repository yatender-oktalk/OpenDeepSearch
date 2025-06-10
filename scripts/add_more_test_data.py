from neo4j import GraphDatabase

def add_more_data():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "maxx3169"))
    
    with driver.session() as session:
        session.run("""
        CREATE (c2:Customer {id: "CUST002", name: "Acme Inc"})
        CREATE (s2:Event:Signup {date: datetime("2023-03-10"), plan: "premium"})
        CREATE (t2:Event:SupportTicket {created_date: datetime("2023-04-15"), issue_type: "billing", priority: "medium"})
        CREATE (c2)-[:PERFORMED {timestamp: datetime("2023-03-10")}]->(s2)
        CREATE (c2)-[:PERFORMED {timestamp: datetime("2023-04-15")}]->(t2)
        """)
    
    driver.close()
    print("Additional test data created!")

if __name__ == "__main__":
    add_more_data() 