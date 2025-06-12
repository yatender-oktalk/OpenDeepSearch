from smolagents import Tool
from typing import Dict, Any, Optional, List
import re
import json
from datetime import datetime, timedelta
from neo4j import GraphDatabase
from litellm import completion

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
    
    # Cypher query templates
    CYPHER_TEMPLATES = {
        "SINGLE_EVENT": """
            MATCH (c:Customer {{id: $customer_id}})-[r:PERFORMED]->(e:Event)
            WHERE $event_type IN labels(e)
            RETURN c.name, c.id, e, labels(e) as event_labels, r.timestamp
            ORDER BY r.timestamp {order}
            LIMIT 1
        """,
        
        "EVENT_SEQUENCE": """
            MATCH (c:Customer {{id: $customer_id}})-[r:PERFORMED]->(e:Event)
            {event_filter}
            RETURN c.name, c.id, e, labels(e) as event_labels, r.timestamp
            ORDER BY r.timestamp
        """,
        
        "COMPARISON": """
            MATCH (c:Customer)-[r:PERFORMED]->(e:Event)
            WHERE c.id IN $customer_ids AND $event_type IN labels(e)
            WITH c, e, r
            ORDER BY r.timestamp ASC
            WITH c.id as customer_id, c.name as customer_name, 
                 collect({{event: e, timestamp: r.timestamp, labels: labels(e)}})[0] as first_event
            RETURN customer_name, customer_id, first_event.event as e, 
                   first_event.labels as event_labels, first_event.timestamp as timestamp
            ORDER BY first_event.timestamp
        """,
        
        "ALL_EVENTS": """
            MATCH (c:Customer)-[r:PERFORMED]->(e:Event)
            {customer_filter}
            {event_filter}
            RETURN c.name, c.id, e, labels(e) as event_labels, r.timestamp
            ORDER BY r.timestamp
        """
    }
    
    VALID_EVENT_TYPES = ['Signup', 'Upgrade', 'Login', 'Purchase', 'SupportTicket', 'TicketResolved', 'Cancellation']
    
    def __init__(self, neo4j_uri: str, username: str, password: str, model_name: str = "openrouter/google/gemini-2.0-flash-001"):
        super().__init__()
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        self.model_name = model_name
        
    def _llm_parse_query(self, query: str) -> Dict[str, Any]:
        """Use LLM to parse and understand the temporal query"""
        
        parsing_prompt = f"""
Parse this temporal query and extract structured information. Return valid JSON only.

Query: "{query}"

Extract and return JSON with these fields:
{{
    "customer_ids": ["CUST001"],  // List of customer IDs mentioned (extract CUST001, CUST002, etc.)
    "event_types": ["Purchase"],  // Types of events mentioned (capitalize: Signup, Purchase, Upgrade, Login, SupportTicket, Cancellation)
    "sequence_type": "first",     // Sequence indicator: "first", "last", "earliest", "latest", "all"
    "comparison": false,          // Is this comparing multiple entities?
    "intent": "SINGLE_EVENT",     // Intent: "SINGLE_EVENT", "EVENT_SEQUENCE", "COMPARISON", "ALL_EVENTS"
    "time_range": null,           // Time range if specified
    "order": "ASC"                // Sort order: "ASC" or "DESC"
}}

Rules:
- Extract customer IDs in format CUST001, CUST002, etc.
- Event types must be from: Signup, Upgrade, Login, Purchase, SupportTicket, Cancellation
- For "first/earliest" use sequence_type="first" and order="ASC"
- For "last/latest" use sequence_type="last" and order="DESC"
- For comparisons between customers, set comparison=true and intent="COMPARISON"
- For single specific events, use intent="SINGLE_EVENT"
- For full timelines, use intent="EVENT_SEQUENCE"

Examples:
"When did CUST001 make their first purchase?" → {{"customer_ids": ["CUST001"], "event_types": ["Purchase"], "sequence_type": "first", "comparison": false, "intent": "SINGLE_EVENT", "order": "ASC"}}

"Who signed up first, CUST001 or CUST002?" → {{"customer_ids": ["CUST001", "CUST002"], "event_types": ["Signup"], "sequence_type": "first", "comparison": true, "intent": "COMPARISON", "order": "ASC"}}

"Show me CUST003 timeline" → {{"customer_ids": ["CUST003"], "event_types": [], "sequence_type": "all", "comparison": false, "intent": "EVENT_SEQUENCE", "order": "ASC"}}

Return only the JSON, no other text.
"""

        try:
            response = completion(
                model=self.model_name,
                messages=[{"role": "user", "content": parsing_prompt}],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result_text = result_text[json_start:json_end]
            
            return json.loads(result_text)
            
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Simple fallback parsing for when LLM fails"""
        constraints = {
            "customer_ids": [],
            "event_types": [],
            "sequence_type": "all",
            "comparison": False,
            "intent": "EVENT_SEQUENCE",
            "order": "ASC"
        }
        
        # Extract customer IDs
        customer_matches = re.findall(r'CUST\d+', query, re.IGNORECASE)
        constraints["customer_ids"] = [match.upper() for match in customer_matches]
        
        # Extract event types
        for event_type in self.VALID_EVENT_TYPES:
            if event_type.lower() in query.lower():
                constraints["event_types"].append(event_type)
        
        # Check for sequence indicators
        if any(word in query.lower() for word in ['first', 'earliest']):
            constraints["sequence_type"] = "first"
            constraints["intent"] = "SINGLE_EVENT"
        elif any(word in query.lower() for word in ['last', 'latest']):
            constraints["sequence_type"] = "last"
            constraints["intent"] = "SINGLE_EVENT"
            constraints["order"] = "DESC"
        
        # Check for comparison
        if len(constraints["customer_ids"]) > 1 or "who" in query.lower():
            constraints["comparison"] = True
            constraints["intent"] = "COMPARISON"
        
        return constraints
    
    def _validate_constraints(self, constraints: Dict) -> Dict[str, Any]:
        """Validate and clean the extracted constraints"""
        
        # Ensure customer_ids is a list
        if not isinstance(constraints.get("customer_ids"), list):
            constraints["customer_ids"] = []
        
        # Ensure event_types is a list and contains valid types
        if not isinstance(constraints.get("event_types"), list):
            constraints["event_types"] = []
        
        constraints["event_types"] = [
            event for event in constraints["event_types"] 
            if event in self.VALID_EVENT_TYPES
        ]
        
        # Set default values
        constraints.setdefault("sequence_type", "all")
        constraints.setdefault("comparison", False)
        constraints.setdefault("intent", "EVENT_SEQUENCE")
        constraints.setdefault("order", "ASC")
        
        return constraints
    
    def _generate_cypher_query(self, constraints: Dict) -> tuple[str, Dict]:
        """Generate Cypher query from validated constraints"""
        
        intent = constraints["intent"]
        params = {}
        
        if intent == "SINGLE_EVENT":
            if not constraints["customer_ids"] or not constraints["event_types"]:
                raise ValueError("Single event queries require customer ID and event type")
            
            template = self.CYPHER_TEMPLATES["SINGLE_EVENT"]
            order = "ASC" if constraints["sequence_type"] in ["first", "earliest"] else "DESC"
            
            query = template.format(order=order)
            params = {
                "customer_id": constraints["customer_ids"][0],
                "event_type": constraints["event_types"][0]
            }
            
        elif intent == "COMPARISON":
            if not constraints["customer_ids"] or not constraints["event_types"]:
                raise ValueError("Comparison queries require customer IDs and event type")
            
            query = self.CYPHER_TEMPLATES["COMPARISON"]
            params = {
                "customer_ids": constraints["customer_ids"],
                "event_type": constraints["event_types"][0]
            }
            
        elif intent == "EVENT_SEQUENCE":
            template = self.CYPHER_TEMPLATES["EVENT_SEQUENCE"]
            
            # Build filters
            event_filter = ""
            if constraints["event_types"]:
                event_filter = f"WHERE '{constraints['event_types'][0]}' IN labels(e)"
            
            query = template.format(event_filter=event_filter)
            params = {"customer_id": constraints["customer_ids"][0]} if constraints["customer_ids"] else {}
            
        elif intent == "ALL_EVENTS":
            template = self.CYPHER_TEMPLATES["ALL_EVENTS"]
            
            # Build filters
            customer_filter = ""
            if constraints["customer_ids"]:
                customer_filter = f"WHERE c.id IN {constraints['customer_ids']}"
            
            event_filter = ""
            if constraints["event_types"]:
                event_filter = f"{'AND' if customer_filter else 'WHERE'} '{constraints['event_types'][0]}' IN labels(e)"
            
            query = template.format(customer_filter=customer_filter, event_filter=event_filter)
            params = {}
        
        else:
            raise ValueError(f"Unknown intent: {intent}")
        
        return query, params
    
    def _format_temporal_results(self, records: list, constraints: Dict) -> str:
        """Enhanced result formatting"""
        if not records:
            return "No temporal data found for this query."
        
        intent = constraints["intent"]
        
        if intent == "COMPARISON":
            return self._format_comparison_results(records, constraints)
        elif intent == "SINGLE_EVENT":
            return self._format_single_event_results(records, constraints)
        else:
            return self._format_timeline_results(records, constraints)
    
    def _format_comparison_results(self, records: list, constraints: Dict) -> str:
        """Format comparison query results"""
        result_text = f"Comparison of {constraints['event_types'][0]} events:\n\n"
        
        for i, record in enumerate(records, 1):
            customer_name = record.get('customer_name', 'Unknown')
            customer_id = record.get('customer_id', 'Unknown')
            timestamp = record.get('timestamp')
            
            if timestamp:
                result_text += f"{i}. {customer_name} ({customer_id}): {timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            else:
                result_text += f"{i}. {customer_name} ({customer_id}): No event found\n"
        
        return result_text.strip()
    
    def _format_single_event_results(self, records: list, constraints: Dict) -> str:
        """Format single event query results"""
        if not records:
            return f"No {constraints['event_types'][0]} event found for the specified customer."
        
        record = records[0]
        customer_name = record.get('c.name', 'Unknown')
        customer_id = record.get('c.id', 'Unknown')
        event = record['e']
        timestamp = record['r.timestamp']
        event_labels = record['event_labels']
        
        event_type = [label for label in event_labels if label != 'Event'][0]
        
        result_text = f"{customer_name} ({customer_id}) - {constraints['sequence_type']} {event_type}:\n"
        result_text += f"Date: {timestamp.strftime('%Y-%m-%d %H:%M')}\n"
        
        # Add event details
        if 'plan' in event:
            result_text += f"Plan: {event['plan']}\n"
        if 'from_plan' in event and 'to_plan' in event:
            result_text += f"Upgrade: {event['from_plan']} → {event['to_plan']}\n"
        
        return result_text.strip()
    
    def _format_timeline_results(self, records: list, constraints: Dict) -> str:
        """Format timeline query results"""
        # Group events by customer
        customer_events = {}
        for record in records:
            customer_id = record.get('c.id', 'Unknown')
            if customer_id not in customer_events:
                customer_events[customer_id] = []
            customer_events[customer_id].append(record)
        
        result_text = ""
        
        for customer_id, events in customer_events.items():
            customer_name = events[0].get('c.name', 'Unknown')
            result_text += f"\nTimeline for {customer_name} ({customer_id}):\n"
            
            for record in events:
                event = record['e']
                event_labels = record['event_labels']
                timestamp = record['r.timestamp']
                
                event_type = [label for label in event_labels if label != 'Event'][0]
                event_text = f"- {timestamp.strftime('%Y-%m-%d %H:%M')}: {event_type}"
                
                # Add event details
                if 'plan' in event:
                    event_text += f" (plan: {event['plan']})"
                if 'from_plan' in event and 'to_plan' in event:
                    event_text += f" (from {event['from_plan']} to {event['to_plan']})"
                
                result_text += event_text + "\n"
        
        return result_text.strip()
    
    def forward(self, query: str) -> str:
        """Execute temporal knowledge graph search"""
        try:
            # 1. Parse query using LLM
            constraints = self._llm_parse_query(query)
            
            # 2. Validate constraints
            constraints = self._validate_constraints(constraints)
            
            # 3. Generate Cypher query
            cypher_query, params = self._generate_cypher_query(constraints)
            
            # 4. Execute against Neo4j
            with self.driver.session() as session:
                result = session.run(cypher_query, params)
                records = [record.data() for record in result]
            
            # 5. Format results
            return self._format_temporal_results(records, constraints)
            
        except Exception as e:
            return f"Temporal search failed: {str(e)}"
