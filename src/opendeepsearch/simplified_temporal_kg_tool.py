from smolagents import Tool
from typing import Dict, Any, Optional
import json
from datetime import datetime
from neo4j import GraphDatabase
from litellm import completion

class SimplifiedTemporalKGTool(Tool):
    name = "sec_filing_temporal_search"
    description = """
    Search a comprehensive temporal knowledge graph containing SEC filing data for companies like Apple, Microsoft, Meta, Adobe, etc. 
    Use this tool for queries about:
    - SEC filing comparisons between companies
    - Filing schedules and patterns (10-K, 10-Q, 8-K, proxy statements)
    - Amendment patterns and filing dates
    - Company-specific SEC filing history
    - Temporal analysis of SEC filings
    
    This tool has access to 25,000+ SEC filings with precise dates and filing types.
    ALWAYS use this tool for SEC filing related queries instead of web search.
    """
    inputs = {
        "query": {
            "type": "string", 
            "description": "The temporal query about SEC filings",
        }
    }
    output_type = "string"
    
    def __init__(self, neo4j_uri: str, username: str, password: str, model_name: str):
        super().__init__()
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        self.model_name = model_name
    
    def forward(self, query: str) -> str:
        """Execute temporal knowledge graph search"""
        try:
            # Simple approach: use LLM to generate Cypher query
            cypher_query = self._generate_cypher_from_query(query)
            
            # Execute against Neo4j
            with self.driver.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]
            
            # Format results
            return self._format_results(records, query)
            
        except Exception as e:
            return f"Temporal search failed: {str(e)}"
    
    def _generate_cypher_from_query(self, query: str) -> str:
        """Enhanced Cypher generation for complex temporal queries"""
        response = completion(
            model=self.model_name,
            messages=[{
                "role": "system",
                "content": """You are a Cypher query generator for SEC filing data. Handle both simple and complex temporal queries.

DATABASE SCHEMA:
- Company nodes: {name, ticker, sector}  
- Filing nodes: {type, filing_date, description, accession_number}
- Relationship: (Company)-[:FILED]->(Filing)

MANDATORY RULES:
1. ALWAYS return exactly these fields: c.name, c.ticker, f.type, f.filing_date, f.description
2. For date filtering, use: f.filing_date >= date("YYYY-MM-DD") and f.filing_date <= date("YYYY-MM-DD")
3. ALWAYS add LIMIT (20-50 max)
4. Use exact ticker symbols: AAPL, MSFT, META, GOOGL, NFLX, ADBE, TSLA, AMZN
5. Use exact filing types: "10-K", "10-Q", "8-K"
6. ALWAYS filter out Unknown filing types: WHERE f.type <> "Unknown"

SIMPLE PATTERNS:
- Single company: MATCH (c:Company {ticker: "AAPL"})-[:FILED]->(f:Filing) RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY f.filing_date DESC LIMIT 20

COMPLEX PATTERNS:
- Compare two companies: MATCH (c:Company)-[:FILED]->(f:Filing) WHERE c.ticker IN ["AAPL", "META"] RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY c.ticker, f.filing_date DESC LIMIT 40

- Recent filings by type: MATCH (c:Company)-[:FILED]->(f:Filing {type: "10-K"}) WHERE f.filing_date >= date("2024-01-01") RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY f.filing_date DESC LIMIT 30

- Filing frequency comparison: MATCH (c:Company)-[:FILED]->(f:Filing) WHERE c.ticker IN ["AAPL", "MSFT"] AND f.filing_date >= date("2023-01-01") RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY c.ticker, f.filing_date DESC LIMIT 50

- Companies with specific filing types: MATCH (c:Company)-[:FILED]->(f:Filing) WHERE f.type IN ["10-K", "10-Q"] AND f.filing_date >= date("2024-01-01") RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY c.name, f.type, f.filing_date DESC LIMIT 40

- Timeline for single company: MATCH (c:Company {ticker: "META"})-[:FILED]->(f:Filing) WHERE f.filing_date >= date("2024-01-01") AND f.filing_date <= date("2024-12-31") RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY f.filing_date ASC LIMIT 30

- Recent filings: MATCH (c:Company)-[:FILED]->(f:Filing) WHERE f.filing_date >= date("2024-01-01") AND f.type <> "Unknown" RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY f.filing_date DESC LIMIT 25

QUERY ANALYSIS HINTS:
- "compare" + company names → use WHERE c.ticker IN [...]
- "most recent" → ORDER BY f.filing_date DESC
- "timeline" or "2024" → add date range filters
- "frequency" or "patterns" → include date ranges and multiple companies
- "both 10-K and 10-Q" → use WHERE f.type IN ["10-K", "10-Q"]

Return ONLY the Cypher query, no explanations."""
            }, {
                "role": "user", 
                "content": f"Generate a Cypher query for: {query}"
            }],
            temperature=0.1  # Slight randomness for variety
        )
        
        cypher_query = response.choices[0].message.content.strip()
        
        # Clean markdown formatting
        import re
        cypher_query = re.sub(r'^```(?:cypher)?\s*\n?', '', cypher_query)
        cypher_query = re.sub(r'\n?```\s*$', '', cypher_query)
        
        # Validate the query has required elements
        required_fields = ['c.name', 'c.ticker', 'f.type', 'f.filing_date', 'f.description']
        if not all(field in cypher_query for field in required_fields):
            # Fallback to a safe default query
            return 'MATCH (c:Company)-[:FILED]->(f:Filing) RETURN c.name, c.ticker, f.type, f.filing_date, f.description ORDER BY f.filing_date DESC LIMIT 20'
        
        # Add safety checks
        if 'LIMIT' not in cypher_query:
            cypher_query += ' LIMIT 30'
        
        return cypher_query.strip()
    
    def _format_results(self, records: list, query: str) -> str:
        """Enhanced formatting for complex query results"""
        if not records:
            return "No SEC filing data found for this query."
        
        result = "SEC Filing Results:\n\n"
        
        # Group by company for comparison queries
        if "compare" in query.lower() or len(set(r.get('c.ticker', '') for r in records)) > 1:
            # Group results by company
            companies = {}
            for record in records:
                ticker = record.get('c.ticker', 'Unknown')
                if ticker not in companies:
                    companies[ticker] = []
                companies[ticker].append(record)
            
            for ticker, company_records in companies.items():
                company_name = company_records[0].get('c.name', 'Unknown')
                result += f"📊 {company_name} ({ticker}):\n"
                
                for i, record in enumerate(company_records[:15], 1):  # Limit per company
                    filing_type = record.get('f.type', 'N/A')
                    filing_date_raw = record.get('f.filing_date')
                    
                    if filing_date_raw and hasattr(filing_date_raw, 'year'):
                        filing_date = f"{filing_date_raw.year}-{filing_date_raw.month:02d}-{filing_date_raw.day:02d}"
                    else:
                        filing_date = str(filing_date_raw) if filing_date_raw else 'N/A'
                    
                    description = record.get('f.description', 'N/A')
                    
                    result += f"  {i}. Filing Type: {filing_type} | Date: {filing_date} | {description}\n"
                
                result += "-" * 60 + "\n\n"
        
        else:
            # Standard formatting for single company or general queries
            for i, record in enumerate(records, 1):
                company_name = record.get('c.name', 'N/A')
                ticker = record.get('c.ticker', 'N/A')
                filing_type = record.get('f.type', 'N/A')
                
                filing_date_raw = record.get('f.filing_date')
                if filing_date_raw and hasattr(filing_date_raw, 'year'):
                    filing_date = f"{filing_date_raw.year}-{filing_date_raw.month:02d}-{filing_date_raw.day:02d}"
                else:
                    filing_date = str(filing_date_raw) if filing_date_raw else 'N/A'
                
                description = record.get('f.description', 'N/A')
                
                result += f"{i}. Company: {company_name} ({ticker})\n"
                result += f"   Filing Type: {filing_type}\n"
                result += f"   Date: {filing_date}\n"
                result += f"   Description: {description}\n"
                result += "-" * 50 + "\n"
        
        return result 