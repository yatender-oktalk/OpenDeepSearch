from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class TemporalDataset:
    """Standard schema for temporal datasets"""
    
    def __init__(self, domain: str, description: str):
        self.metadata = {
            "domain": domain,
            "description": description,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "schema_version": "1.0",
            "total_entities": 0,
            "total_events": 0,
            "date_range": {"start": None, "end": None},
            "event_types": [],
            "data_sources": []
        }
        self.entities = []
        self.events = []
        self.relationships = []
    
    def add_entity(self, entity_id: str, entity_type: str, name: str, 
                   properties: Dict[str, Any] = None):
        """Add an entity (company, person, organization, etc.)"""
        entity = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "properties": properties or {},
            "domain": self.metadata["domain"]
        }
        self.entities.append(entity)
        self.metadata["total_entities"] = len(self.entities)
    
    def add_event(self, event_id: str, entity_id: str, event_type: str,
                  date: str, timestamp: str, details: str,
                  properties: Dict[str, Any] = None):
        """Add a temporal event"""
        event = {
            "id": event_id,
            "entity_id": entity_id,
            "event_type": event_type,
            "date": date,  # YYYY-MM-DD format
            "timestamp": timestamp,  # ISO format
            "details": details,
            "properties": properties or {},
            "domain": self.metadata["domain"]
        }
        self.events.append(event)
        
        # Update metadata
        self.metadata["total_events"] = len(self.events)
        
        if event_type not in self.metadata["event_types"]:
            self.metadata["event_types"].append(event_type)
        
        # Update date range
        if not self.metadata["date_range"]["start"] or date < self.metadata["date_range"]["start"]:
            self.metadata["date_range"]["start"] = date
        if not self.metadata["date_range"]["end"] or date > self.metadata["date_range"]["end"]:
            self.metadata["date_range"]["end"] = date
    
    def add_relationship(self, from_entity: str, to_entity: str, 
                        relationship_type: str, properties: Dict[str, Any] = None):
        """Add relationship between entities"""
        relationship = {
            "from_entity": from_entity,
            "to_entity": to_entity,
            "type": relationship_type,
            "properties": properties or {}
        }
        self.relationships.append(relationship)
    
    def add_data_source(self, source: str, url: str = None, description: str = None):
        """Add data source information"""
        source_info = {
            "name": source,
            "url": url,
            "description": description,
            "accessed_at": datetime.now().isoformat()
        }
        self.metadata["data_sources"].append(source_info)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "metadata": self.metadata,
            "entities": self.entities,
            "events": self.events,
            "relationships": self.relationships
        }
    
    def save(self, filename: str):
        """Save dataset to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Dataset saved to {filename}")
        print(f"  - {self.metadata['total_entities']} entities")
        print(f"  - {self.metadata['total_events']} events")
        print(f"  - Date range: {self.metadata['date_range']['start']} to {self.metadata['date_range']['end']}")
    
    @classmethod
    def load(cls, filename: str):
        """Load dataset from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        dataset = cls(
            domain=data["metadata"]["domain"],
            description=data["metadata"]["description"]
        )
        dataset.metadata = data["metadata"]
        dataset.entities = data["entities"]
        dataset.events = data["events"]
        dataset.relationships = data.get("relationships", [])
        
        return dataset
    
    def get_summary(self):
        """Get dataset summary"""
        return {
            "domain": self.metadata["domain"],
            "entities": self.metadata["total_entities"],
            "events": self.metadata["total_events"],
            "event_types": len(self.metadata["event_types"]),
            "date_range": f"{self.metadata['date_range']['start']} to {self.metadata['date_range']['end']}",
            "data_sources": len(self.metadata["data_sources"])
        }
