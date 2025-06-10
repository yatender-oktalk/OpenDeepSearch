from neo4j import GraphDatabase

def add_strategic_data():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "maxx3169"))
    
    with driver.session() as session:
        # Add more events to CUST001
        session.run("""
        MATCH (c:Customer {id: "CUST001"})
        CREATE (l1:Event:Login {timestamp: datetime("2023-01-16T09:30:00"), device: "desktop"})
        CREATE (l2:Event:Login {timestamp: datetime("2023-06-02T14:15:00"), device: "mobile"}) 
        CREATE (p1:Event:Purchase {date: datetime("2023-07-15"), amount: 299.99, product: "Analytics Suite"})
        CREATE (c)-[:PERFORMED {timestamp: datetime("2023-01-16T09:30:00")}]->(l1)
        CREATE (c)-[:PERFORMED {timestamp: datetime("2023-06-02T14:15:00")}]->(l2)
        CREATE (c)-[:PERFORMED {timestamp: datetime("2023-07-15")}]->(p1)
        """)
        
        # Add more events to CUST002
        session.run("""
        MATCH (c2:Customer {id: "CUST002"})
        CREATE (tr:Event:TicketResolved {date: datetime("2023-04-18"), resolution: "billing correction"})
        CREATE (l3:Event:Login {timestamp: datetime("2023-04-20T11:00:00"), device: "desktop"})
        CREATE (c2)-[:PERFORMED {timestamp: datetime("2023-04-18")}]->(tr)
        CREATE (c2)-[:PERFORMED {timestamp: datetime("2023-04-20T11:00:00")}]->(l3)
        """)
        
        # Create CUST003 with all events
        session.run("""
        CREATE (c3:Customer {id: "CUST003", name: "StartupXYZ"})
        CREATE (s3:Event:Signup {date: datetime("2023-02-01"), plan: "basic"})
        CREATE (l4:Event:Login {timestamp: datetime("2023-02-02T08:00:00"), device: "desktop"})
        CREATE (l5:Event:Login {timestamp: datetime("2023-02-05T16:30:00"), device: "mobile"})
        CREATE (t3:Event:SupportTicket {created_date: datetime("2023-02-10"), issue_type: "feature_request", priority: "low"})
        CREATE (tr2:Event:TicketResolved {date: datetime("2023-02-12"), resolution: "feature planned for Q2"})
        CREATE (cancel:Event:Cancellation {date: datetime("2023-02-28"), reason: "cost"})
        
        CREATE (c3)-[:PERFORMED {timestamp: datetime("2023-02-01")}]->(s3)
        CREATE (c3)-[:PERFORMED {timestamp: datetime("2023-02-02T08:00:00")}]->(l4)
        CREATE (c3)-[:PERFORMED {timestamp: datetime("2023-02-05T16:30:00")}]->(l5)
        CREATE (c3)-[:PERFORMED {timestamp: datetime("2023-02-10")}]->(t3)
        CREATE (c3)-[:PERFORMED {timestamp: datetime("2023-02-12")}]->(tr2)
        CREATE (c3)-[:PERFORMED {timestamp: datetime("2023-02-28")}]->(cancel)
        """)
    
    driver.close()
    print("Strategic test data created!")
    print("Now you can test:")
    print("- Multi-step customer journeys")
    print("- Different event types (Login, Purchase, Cancellation)")
    print("- Temporal patterns (signup → usage → purchase)")
    print("- Churn analysis")

if __name__ == "__main__":
    add_strategic_data() 