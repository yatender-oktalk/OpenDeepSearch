from smolagents import Tool
from typing import Dict, Any, Optional, List
import re
import json
from datetime import datetime, timedelta
from neo4j import GraphDatabase
from litellm import completion
import zep
from graphiti import GraphitiClient
import os
from dotenv import load_dotenv

load_dotenv()

class EnhancedTemporalKGTool(Tool):
    name = "enhanced_temporal_kg_search"
    description = """Search temporal knowledge graph with conversational memory and graph reasoning.
    Use this tool when you need information about customer events, timelines, or historical data with context awareness."""
    inputs = {
        "query": {
            "type": "string", 
            "description": "The temporal query to search for (e.g., 'What happened to Customer CUST001?')",
        },
        "conversation_id": {
            "type": "string",
            "description": "Optional conversation ID for context",
            "optional": True
        }
    }
    output_type = "string"
    
    # Cypher query templates with Graphiti enhancements
    CYPHER_TEMPLATES = {
        "SINGLE_FILING": """
            MATCH (c:Company {ticker: $ticker})-[r:FILED]->(f:Filing)
            WHERE f.type = $filing_type
            WITH c, f, r, 
                 apoc.text.similarity(c.name, $company_name) as name_similarity,
                 apoc.text.similarity(f.description, $filing_details) as details_similarity
            WHERE name_similarity > 0.7 OR details_similarity > 0.7
            RETURN c.name, c.ticker, f, f.type as filing_type, r.filing_date,
                   name_similarity, details_similarity
            ORDER BY name_similarity + details_similarity DESC, r.filing_date {order}
            LIMIT 1
        """,
        
        "FILING_SEQUENCE": """
            MATCH (c:Company {ticker: $ticker})-[r:FILED]->(f:Filing)
            {filing_filter}
            WITH c, f, r,
                 apoc.text.similarity(c.name, $company_name) as name_similarity,
                 apoc.text.similarity(f.description, $filing_details) as details_similarity
            WHERE name_similarity > 0.7 OR details_similarity > 0.7
            RETURN c.name, c.ticker, f, f.type as filing_type, r.filing_date,
                   name_similarity, details_similarity
            ORDER BY r.filing_date
        """,
        
        "COMPARISON": """
            MATCH (c:Company)-[r:FILED]->(f:Filing)
            WHERE c.ticker IN $tickers AND f.type = $filing_type
            WITH c, f, r,
                 apoc.text.similarity(c.name, $company_name) as name_similarity,
                 apoc.text.similarity(f.description, $filing_details) as details_similarity
            WHERE name_similarity > 0.7 OR details_similarity > 0.7
            ORDER BY r.filing_date ASC
            WITH c.ticker as ticker, c.name as company_name, 
                 collect({filing: f, filing_date: r.filing_date, type: f.type,
                         name_similarity: name_similarity,
                         details_similarity: details_similarity})[0] as first_filing
            RETURN company_name, ticker, first_filing.filing as f, 
                   first_filing.type as filing_type, first_filing.filing_date as filing_date,
                   first_filing.name_similarity as name_similarity,
                   first_filing.details_similarity as details_similarity
            ORDER BY first_filing.filing_date
        """,
        
        "ALL_FILINGS": """
            MATCH (c:Company)-[r:FILED]->(f:Filing)
            {company_filter}
            {filing_filter}
            WITH c, f, r,
                 apoc.text.similarity(c.name, $company_name) as name_similarity,
                 apoc.text.similarity(f.description, $filing_details) as details_similarity
            WHERE name_similarity > 0.7 OR details_similarity > 0.7
            RETURN c.name, c.ticker, f, f.type as filing_type, r.filing_date,
                   name_similarity, details_similarity
            ORDER BY r.filing_date
        """
    }
    
    VALID_FILING_TYPES = ['10-K', '10-Q', '8-K', 'DEF 14A', 'S-1', 'S-3', 'S-4', 'S-8', '13F', '13G', '13D']
    
    def __init__(
        self, 
        neo4j_uri: str, 
        username: str, 
        password: str, 
        model_name: str = "openrouter/google/gemini-2.0-flash-001",
        zep_api_url: Optional[str] = None,
        zep_api_key: Optional[str] = None
    ):
        super().__init__()
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        self.model_name = model_name
        
        # Initialize Zep client for conversational memory
        self.zep_client = zep.Client(
            api_url=zep_api_url or os.getenv('ZEP_API_URL', 'http://localhost:8000'),
            api_key=zep_api_key or os.getenv('ZEP_API_KEY')
        )
        
        # Initialize Graphiti client for graph reasoning
        self.graphiti_client = GraphitiClient(
            neo4j_uri=neo4j_uri,
            username=username,
            password=password
        )
        
    def _get_conversation_context(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get relevant context from conversation history using Zep"""
        if not conversation_id:
            return {}
            
        try:
            # Get conversation history from Zep
            conversation = self.zep_client.get_conversation(conversation_id)
            if not conversation:
                return {}
                
            # Extract relevant entities and events from conversation
            context = {
                'tickers': [],
                'filing_types': [],
                'temporal_constraints': {},
                'mentioned_entities': set()
            }
            
            for message in conversation.messages:
                # Extract entities and events using LLM
                entities = self._extract_entities(message.content)
                context['tickers'].extend(entities.get('tickers', []))
                context['filing_types'].extend(entities.get('filing_types', []))
                context['mentioned_entities'].update(entities.get('entities', []))
                
                # Extract temporal constraints
                temporal = self._extract_temporal_constraints(message.content)
                context['temporal_constraints'].update(temporal)
            
            return context
            
        except Exception as e:
            print(f"Warning: Failed to get conversation context: {e}")
            return {}
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using LLM"""
        try:
            response = completion(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "Extract tickers, filing types, and other entities from the text. Return as JSON."
                }, {
                    "role": "user",
                    "content": text
                }],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Warning: Failed to extract entities: {e}")
            return {'tickers': [], 'filing_types': [], 'entities': []}
    
    def _extract_temporal_constraints(self, text: str) -> Dict[str, Any]:
        """Extract temporal constraints from text using LLM"""
        try:
            response = completion(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "Extract temporal constraints (dates, ranges, relative times) from the text. Return as JSON."
                }, {
                    "role": "user",
                    "content": text
                }],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Warning: Failed to extract temporal constraints: {e}")
            return {}
    
    def _llm_parse_query(self, query: str, conversation_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Use LLM to parse and understand the temporal query with conversation context"""
        try:
            # Combine query with conversation context
            context_str = ""
            if conversation_context:
                context_str = f"\nConversation Context:\n{json.dumps(conversation_context, indent=2)}"
            
            response = completion(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "Parse the temporal query and extract intent, entities, and constraints. Return as JSON."
                }, {
                    "role": "user",
                    "content": f"Query: {query}{context_str}"
                }],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Warning: Failed to parse query: {e}")
            return {
                "intent": "ALL_FILINGS",
                "tickers": [],
                "filing_types": [],
                "temporal_constraints": {}
            }
    
    def _generate_cypher_query(self, constraints: Dict, conversation_context: Dict[str, Any] = None) -> tuple[str, Dict]:
        """Generate Cypher query from validated constraints with conversation context"""
        intent = constraints["intent"]
        params = {}
        
        # Merge conversation context with query constraints
        if conversation_context:
            constraints['tickers'].extend(conversation_context.get('tickers', []))
            constraints['filing_types'].extend(conversation_context.get('filing_types', []))
            constraints['temporal_constraints'].update(conversation_context.get('temporal_constraints', {}))
        
        if intent == "SINGLE_FILING":
            if not constraints["tickers"] or not constraints["filing_types"]:
                raise ValueError("Single filing queries require ticker and filing type")
            
            template = self.CYPHER_TEMPLATES["SINGLE_FILING"]
            order = "ASC" if constraints["sequence_type"] in ["first", "earliest"] else "DESC"
            
            query = template.format(order=order)
            params = {
                "ticker": constraints["tickers"][0],
                "filing_type": constraints["filing_types"][0],
                "company_name": constraints.get("company_name", ""),
                "filing_details": constraints.get("filing_details", "")
            }
            
        elif intent == "COMPARISON":
            if not constraints["tickers"] or not constraints["filing_types"]:
                raise ValueError("Comparison queries require tickers and filing type")
            
            query = self.CYPHER_TEMPLATES["COMPARISON"]
            params = {
                "tickers": constraints["tickers"],
                "filing_type": constraints["filing_types"][0],
                "company_name": constraints.get("company_name", ""),
                "filing_details": constraints.get("filing_details", "")
            }
            
        elif intent == "FILING_SEQUENCE":
            template = self.CYPHER_TEMPLATES["FILING_SEQUENCE"]
            
            # Build filters
            filing_filter = ""
            if constraints["filing_types"]:
                filing_filter = f"WHERE '{constraints['filing_types'][0]}' IN labels(f)"
            
            query = template.format(filing_filter=filing_filter)
            params = {
                "ticker": constraints["tickers"][0] if constraints["tickers"] else "",
                "company_name": constraints.get("company_name", ""),
                "filing_details": constraints.get("filing_details", "")
            }
            
        elif intent == "ALL_FILINGS":
            template = self.CYPHER_TEMPLATES["ALL_FILINGS"]
            
            # Build filters
            company_filter = ""
            if constraints["tickers"]:
                company_filter = f"WHERE c.ticker IN {constraints['tickers']}"
            
            filing_filter = ""
            if constraints["filing_types"]:
                filing_filter = f"{'AND' if company_filter else 'WHERE'} '{constraints['filing_types'][0]}' IN labels(f)"
            
            query = template.format(company_filter=company_filter, filing_filter=filing_filter)
            params = {
                "company_name": constraints.get("company_name", ""),
                "filing_details": constraints.get("filing_details", "")
            }
        
        else:
            raise ValueError(f"Unknown intent: {intent}")
        
        return query, params
    
    def _format_temporal_results(self, records: list, constraints: Dict, conversation_context: Dict[str, Any] = None) -> str:
        """Enhanced result formatting with conversation context"""
        if not records:
            return "No temporal data found for this query."
        
        intent = constraints["intent"]
        
        # Use Graphiti for enhanced reasoning
        try:
            # Get graph insights
            insights = self.graphiti_client.get_insights(
                records=records,
                intent=intent,
                context=conversation_context
            )
        except Exception as e:
            print(f"Warning: Failed to get graph insights: {e}")
            insights = {}
        
        if intent == "COMPARISON":
            return self._format_comparison_results(records, constraints, insights)
        elif intent == "SINGLE_FILING":
            return self._format_single_filing_results(records, constraints, insights)
        else:
            return self._format_timeline_results(records, constraints, insights)
    
    def _format_comparison_results(self, records: list, constraints: Dict, insights: Dict) -> str:
        """Format comparison results with insights"""
        if not records:
            return "No comparison data found."
            
        result = "Comparison Results:\n\n"
        
        for record in records:
            result += f"Company: {record['company_name']} ({record['ticker']})\n"
            result += f"Filing: {record['f']['filing_type']}\n"
            result += f"Date: {record['filing_date']}\n"
            result += f"Details: {record['f']['details']}\n"
            
            # Add relevant insights
            if insights.get('patterns'):
                result += f"\nPatterns:\n{insights['patterns']}\n"
            
            result += "\n" + "-" * 40 + "\n"
        
        return result
    
    def _format_single_filing_results(self, records: list, constraints: Dict, insights: Dict) -> str:
        """Format single filing results with insights"""
        if not records:
            return "No filing data found."
            
        record = records[0]
        result = f"Filing Details:\n\n"
        result += f"Company: {record['company_name']} ({record['ticker']})\n"
        result += f"Filing Type: {record['f']['filing_type']}\n"
        result += f"Date: {record['filing_date']}\n"
        result += f"Details: {record['f']['details']}\n"
        
        # Add relevant insights
        if insights.get('context'):
            result += f"\nContext:\n{insights['context']}\n"
        
        return result
    
    def _format_timeline_results(self, records: list, constraints: Dict, insights: Dict) -> str:
        """Format timeline results with insights"""
        if not records:
            return "No timeline data found."
            
        result = "Timeline:\n\n"
        
        # Group filings by date
        filings_by_date = {}
        for record in records:
            date = record['filing_date'].date()
            if date not in filings_by_date:
                filings_by_date[date] = []
            filings_by_date[date].append(record)
        
        # Format timeline
        for date in sorted(filings_by_date.keys()):
            result += f"\n{date}:\n"
            for record in filings_by_date[date]:
                result += f"- {record['f']['filing_type']}: {record['f']['details']}\n"
        
        # Add insights
        if insights.get('summary'):
            result += f"\nSummary:\n{insights['summary']}\n"
        
        if insights.get('patterns'):
            result += f"\nPatterns:\n{insights['patterns']}\n"
        
        return result
    
    def forward(self, query: str, conversation_id: Optional[str] = None) -> str:
        """Execute enhanced temporal knowledge graph search with conversation context"""
        try:
            # Get conversation context
            conversation_context = self._get_conversation_context(conversation_id)
            
            # 1. Parse query using LLM with conversation context
            constraints = self._llm_parse_query(query, conversation_context)
            
            # 2. Validate constraints
            constraints = self._validate_constraints(constraints)
            
            # 3. Generate Cypher query
            cypher_query, params = self._generate_cypher_query(constraints, conversation_context)
            
            # 4. Execute against Neo4j
            with self.driver.session() as session:
                result = session.run(cypher_query, params)
                records = [record.data() for record in result]
            
            # 5. Format results with insights
            return self._format_temporal_results(records, constraints, conversation_context)
            
        except Exception as e:
            return f"Temporal search failed: {str(e)}"
    
    def _validate_constraints(self, constraints: Dict) -> Dict:
        """Validate and clean up constraints"""
        if 'tickers' not in constraints:
            constraints['tickers'] = []
        if 'filing_types' not in constraints:
            constraints['filing_types'] = []
        if 'temporal_constraints' not in constraints:
            constraints['temporal_constraints'] = {}
            
        # Validate filing types
        constraints['filing_types'] = [
            ft for ft in constraints['filing_types']
            if ft in self.VALID_FILING_TYPES
        ]
        
        return constraints 