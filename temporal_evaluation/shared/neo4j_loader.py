import os
import json
from neo4j import GraphDatabase
from dataset_schema import TemporalDataset

class Neo4jLoader:
    """Generic loader for temporal datasets into Neo4j"""
    
    def __init__(self, uri=None, username=None, password=None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'maxx3169')
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
    
    def clear_database(self):
        """Clear all data from Neo4j"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared")
    
    def load_dataset(self, dataset_file: str, clear_first: bool = True):
        """Load dataset from JSON file into Neo4j"""
        
        # Load dataset
        dataset = TemporalDataset.load(dataset_file)
        
        if clear_first:
            self.clear_database()
        
        print(f"Loading {dataset.metadata['domain']} dataset into Neo4j...")
        
        with self.driver.session() as session:
            # Create entities
            print(f"Creating {len(dataset.entities)} entities...")
            for entity in dataset.entities:
                session.run("""
                    CREATE (e:Entity {
                        id: $id,
                        type: $type,
                        name: $name,
                        domain: $domain,
                        properties: $properties
                    })
                """, 
                id=entity['id'],
                type=entity['type'],
                name=entity['name'],
                domain=entity['domain'],
                properties=json.dumps(entity['properties']))
            
            # Create events
            print(f"Creating {len(dataset.events)} events...")
            for event in dataset.events:
                # Create event node with dynamic label
                event_label = f"Event:{event['event_type'].title().replace('_', '')}"
                
                session.run(f"""
                    CREATE (e:{event_label} {{
                        id: $id,
                        event_type: $event_type,
                        date: datetime($timestamp),
                        details: $details,
                        domain: $domain,
                        properties: $properties
                    }})
                """,
                id=event['id'],
                event_type=event['event_type'],
                timestamp=event['timestamp'],
                details=event['details'],
                domain=event['domain'],
                properties=json.dumps(event['properties']))
                
                # Create relationship between entity and event
                session.run("""
                    MATCH (entity:Entity {id: $entity_id})
                    MATCH (event {id: $event_id})
                    CREATE (entity)-[:PERFORMED {timestamp: datetime($timestamp)}]->(event)
                """,
                entity_id=event['entity_id'],
                event_id=event['id'],
                timestamp=event['timestamp'])
            
            # Create relationships between entities
            if dataset.relationships:
                print(f"Creating {len(dataset.relationships)} relationships...")
                for rel in dataset.relationships:
                    session.run(f"""
                        MATCH (from:Entity {{id: $from_entity}})
                        MATCH (to:Entity {{id: $to_entity}})
                        CREATE (from)-[:{rel['type']} $properties]->(to)
                    """,
                    from_entity=rel['from_entity'],
                    to_entity=rel['to_entity'],
                    properties=rel['properties'])
        
        print(f"✅ Dataset loaded successfully!")
        print(f"  - Domain: {dataset.metadata['domain']}")
        print(f"  - Entities: {dataset.metadata['total_entities']}")
        print(f"  - Events: {dataset.metadata['total_events']}")
        print(f"  - Date range: {dataset.metadata['date_range']['start']} to {dataset.metadata['date_range']['end']}")
    
    def close(self):
        """Close database connection"""
        self.driver.close()

def load_all_datasets():
    """Load all available datasets"""
    loader = Neo4jLoader()
    
    dataset_files = [
        'datasets/financial_data.json',
        'datasets/sec_filings.json',
        'datasets/clinical_trials.json',
        'datasets/supply_chain.json'
    ]
    
    for dataset_file in dataset_files:
        if os.path.exists(dataset_file):
            print(f"\n📊 Loading {dataset_file}...")
            loader.load_dataset(dataset_file, clear_first=True)
        else:
            print(f"⚠️  Dataset not found: {dataset_file}")
    
    loader.close()

if __name__ == "__main__":
    load_all_datasets()
