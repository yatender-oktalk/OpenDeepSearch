from smolagents import Tool
from typing import Dict, Any, Optional
import re
from datetime import datetime
from neo4j import GraphDatabase

class TemporalKGTool(Tool):
    name = "temporal_kg_search"
    description = """Search temporal knowledge graph for time-sensitive customer information.
    Use this tool when you need information about customer events, timelines, or historical data."""
    inputs = {
        "query": {
            "type": "string", 
            "description": "The temporal query to search for (e.g., 'What happened to Customer CUST001?')",
        },
    }
    output_type = "string"
    
    def __init__(self, neo4j_uri: str, username: str, password: str):
        super().__init__()
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        
    def _extract_temporal_constraints(self, query: str) -> Dict[str, Any]:
        """Simple regex-based temporal extraction for now"""
        constraints = {}
        
        # Look for customer IDs
        customer_match = re.search(r'Customer (\w+)', query, re.IGNORECASE)
        if customer_match:
            constraints['customer_id'] = customer_match.group(1)
            
        # Look for year ranges
        year_range = re.search(r'between (\d{4})[- ]?and?[- ]?(\d{4})', query, re.IGNORECASE)
        if year_range:
            constraints['start_year'] = year_range.group(1)
            constraints['end_year'] = year_range.group(2)
        
        return constraints
        
    def _generate_cypher_query(self, query: str, temporal_constraints: Dict) -> str:
        """Simple hardcoded queries for MVP"""
        
        if 'customer_id' in temporal_constraints:
            customer_id = temporal_constraints['customer_id']
            
            if 'start_year' in temporal_constraints:
                # Date range query
                return f"""
                MATCH (c:Customer {{id: "{customer_id}"}})-[r:PERFORMED]->(e:Event)
                WHERE e.date >= datetime("{temporal_constraints['start_year']}-01-01") 
                  AND e.date <= datetime("{temporal_constraints['end_year']}-12-31")
                RETURN c.name, e, labels(e) as event_labels, r.timestamp
                ORDER BY r.timestamp
                """
            else:
                # All events for customer
                return f"""
                MATCH (c:Customer {{id: "{customer_id}"}})-[r:PERFORMED]->(e:Event)
                RETURN c.name, e, labels(e) as event_labels, r.timestamp
                ORDER BY r.timestamp
                """
        
        # Default fallback
        return "MATCH (c:Customer)-[r:PERFORMED]->(e:Event) RETURN c.name, e, labels(e) as event_labels, r.timestamp LIMIT 5"
        
    def _format_temporal_results(self, records: list, query: str) -> str:
        """Format results into readable text"""
        if not records:
            return "No temporal data found for this query."
            
        result_text = "Timeline of events:\n"
        for record in records:
            customer_name = record.get('c.name', 'Unknown')
            event = record['e']
            event_labels = record['event_labels']  # Now we have the labels
            timestamp = record['r.timestamp']
            
            # Get the event type (exclude 'Event' label)
            event_type = [label for label in event_labels if label != 'Event']
            event_type = event_type[0] if event_type else 'Event'
            
            result_text += f"- {timestamp.strftime('%Y-%m-%d')}: {customer_name} - {event_type}"
            
            # Add event-specific details
            if 'plan' in event:
                result_text += f" (plan: {event['plan']})"
            if 'from_plan' in event and 'to_plan' in event:
                result_text += f" (from {event['from_plan']} to {event['to_plan']})"
                
            result_text += "\n"
            
        return result_text.strip()
        
    def forward(self, query: str) -> str:
        """Execute temporal knowledge graph search"""
        try:
            # 1. Extract temporal constraints
            constraints = self._extract_temporal_constraints(query)
            
            # 2. Generate Cypher query
            cypher_query = self._generate_cypher_query(query, constraints)
            
            # 3. Execute against Neo4j
            with self.driver.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]
            
            # 4. Format results
            return self._format_temporal_results(records, query)
            
        except Exception as e:
            return f"Temporal search failed: {str(e)}"
