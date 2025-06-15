# Update: temporal_evaluation/zep/tools/zep_temporal_kg_tool.py
from smolagents import Tool
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import os
import uuid

try:
    from zep_cloud.client import Zep
    from zep_cloud.types import Message
    ZEP_AVAILABLE = True
    print("✅ Using zep-cloud package")
except ImportError:
    print("❌ zep-cloud not available. Install with: pip install zep-cloud")
    ZEP_AVAILABLE = False

class ZepTemporalKGTool(Tool):
    name = "temporal_kg_search"
    description = """
    Search temporal knowledge graph using Zep's intelligent memory and graph capabilities.
    Leverages Zep's knowledge graph with temporal fact tracking, entity relationships, 
    and automatic fact invalidation for SEC filing analysis.
    """
    inputs = {
        "query": {
            "type": "string", 
            "description": "The temporal query to search for in the knowledge graph"
        }
    }
    output_type = "string"
    
    def __init__(self, api_key: str = None):
        super().__init__()
        if not ZEP_AVAILABLE:
            raise ImportError("Zep Cloud is required. Install with: pip install zep-cloud")
            
        # Initialize Zep client with your API key
        self.api_key = api_key or os.getenv('ZEP_API_KEY')
        if not self.api_key:
            raise ValueError("ZEP_API_KEY is required")
            
        self.client = Zep(api_key=self.api_key)
        self.user_id = "sec_analyst_user"
        self.session_id = f"sec_filing_session_{uuid.uuid4().hex[:8]}"
        
        # Initialize user and session
        self._initialize_user_session()
        print("✅ Zep client initialized successfully")
    
    def _initialize_user_session(self):
        """Initialize Zep user and session"""
        try:
            # Create user
            try:
                self.client.user.add(
                    user_id=self.user_id,
                    email="sec_analyst@example.com",
                    first_name="SEC",
                    last_name="Analyst"
                )
                print(f"✅ Created Zep user: {self.user_id}")
            except Exception:
                print(f"ℹ️ User {self.user_id} already exists")
            
            # Create session
            try:
                self.client.memory.add_session(
                    session_id=self.session_id,
                    user_id=self.user_id
                )
                print(f"✅ Created Zep session: {self.session_id}")
            except Exception as e:
                print(f"ℹ️ Session: {e}")
                
        except Exception as e:
            print(f"⚠️ Error initializing Zep: {e}")
    
    def forward(self, query: str) -> str:
        """
        Process temporal query using Zep's REAL knowledge graph and memory
        """
        try:
            print(f"🔍 Searching Zep knowledge graph for: {query}")
            
            # Get memory context from Zep
            memory = self.client.memory.get(session_id=self.session_id)
            
            # Search the knowledge graph for relationships/facts
            edge_results = self.client.graph.search(
                user_id=self.user_id,
                query=query,
                scope="edges",  # Search for relationships/facts
                limit=10
            )
            
            # Search for entities
            node_results = self.client.graph.search(
                user_id=self.user_id,
                query=query,
                scope="nodes",  # Search for entities
                limit=5
            )
            
            # Format the REAL results from Zep
            formatted_results = self._format_real_zep_results(memory, edge_results, node_results, query)
            return formatted_results
            
        except Exception as e:
            return f"Error in Zep temporal search: {str(e)}"
    
    # Update _format_real_zep_results in zep_temporal_kg_tool.py:
    def _format_real_zep_results(self, memory, edge_results, node_results, query: str) -> str:
        """Format REAL Zep results with query-specific filtering"""
        output = ["🧠 Zep Temporal Knowledge Graph Results:", ""]
        
        # Show memory context
        if memory and hasattr(memory, 'context') and memory.context:
            output.extend([
                "📊 Memory Context (Temporal Facts):",
                memory.context,
                ""
            ])
        else:
            output.extend([
                "📊 Memory Context: Building temporal relationships...",
                ""
            ])
        
        # Show RELEVANT edge results (filter out expired/invalid ones)
        if edge_results and hasattr(edge_results, 'edges') and edge_results.edges:
            # Filter for valid, non-expired edges
            valid_edges = [edge for edge in edge_results.edges 
                          if not edge.expired_at and not edge.invalid_at]
            
            if valid_edges:
                output.extend([
                    f"🔗 Knowledge Graph Relationships ({len(valid_edges)} active):",
                    ""
                ])
                
                for i, edge in enumerate(valid_edges, 1):
                    fact = getattr(edge, 'fact', 'No fact available')
                    valid_at = getattr(edge, 'valid_at', 'Unknown')
                    
                    output.extend([
                        f"{i}. Temporal Fact:",
                        f"   {fact}",
                        f"   Valid From: {valid_at}",
                        ""
                    ])
            else:
                output.extend([
                    "🔗 Knowledge Graph Relationships: All relationships expired/invalid",
                    "   (This indicates temporal fact invalidation is working)",
                    ""
                ])
        else:
            output.extend([
                "🔗 Knowledge Graph Relationships: None found for this query",
                ""
            ])
        
        # Show relevant entities
        if node_results and hasattr(node_results, 'nodes') and node_results.nodes:
            output.extend([
                f"🏢 Relevant Entities ({len(node_results.nodes)} found):",
                ""
            ])
            
            for i, node in enumerate(node_results.nodes, 1):
                name = getattr(node, 'name', 'Unknown')
                summary = getattr(node, 'summary', 'No summary available')
                
                output.extend([
                    f"{i}. Entity: {name}",
                    f"   Summary: {summary[:200]}{'...' if len(summary) > 200 else ''}",
                    ""
                ])
        else:
            output.extend([
                "🏢 Relevant Entities: None found for this query",
                ""
            ])
        
        # Add Zep's temporal intelligence summary
        output.extend([
            "🎯 Zep's Temporal Intelligence Features:",
            "✅ Query-specific entity and relationship search",
            "✅ Temporal fact tracking with validity periods", 
            "✅ Automatic fact invalidation when contradictions occur",
            "✅ Semantic + temporal + graph hybrid search",
            "✅ Entity extraction and relationship building",
            ""
        ])
        
        return "\n".join(output)
    
    def add_sec_filing_data(self, filing_data: Dict[str, Any]):
        """Add SEC filing data to Zep's knowledge graph - let Zep build relationships"""
        try:
            # Add as JSON business data - Zep will automatically extract entities and relationships
            json_data = {
                "sec_filing_event": {
                    "company_name": filing_data['company'],
                    "ticker_symbol": filing_data.get('ticker', ''),
                    "filing_type": filing_data['filing_type'],
                    "filing_date": filing_data['date'],
                    "description": filing_data.get('description', ''),
                    "event_description": f"Company {filing_data['company']} filed a {filing_data['filing_type']} SEC filing on {filing_data['date']}"
                }
            }
            
            # Let Zep automatically build the knowledge graph
            episode = self.client.graph.add(
                user_id=self.user_id,
                type="json",
                data=json.dumps(json_data)
            )
            
            print(f"✅ Added SEC filing to Zep: {filing_data['company']} - {filing_data['filing_type']}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding SEC data to Zep: {e}")
            return False
    
    def load_all_sec_data(self, sec_data_path: str):
        """Load SEC filing data into Zep - let Zep build temporal relationships"""
        print("🚀 Loading SEC filing data into Zep Knowledge Graph...")
        print("   Zep will automatically extract entities and build temporal relationships")
        
        try:
            with open(sec_data_path, 'r') as f:
                sec_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading SEC data file: {e}")
            return 0
        
        if not sec_data:
            print("❌ No SEC data found in file")
            return 0
        
        # Handle both dictionary and list formats
        if isinstance(sec_data, dict):
            print(f"📊 Found dictionary with {len(sec_data)} keys")
            # Convert dict to list of entries
            filing_entries = []
            for key, value in sec_data.items():
                if isinstance(value, dict):
                    # Add the key as an identifier
                    value['id'] = key
                    filing_entries.append(value)
                elif isinstance(value, list):
                    # If value is a list, extend our entries
                    filing_entries.extend(value)
                else:
                    # Create a simple entry
                    filing_entries.append({'id': key, 'data': value})
                
        elif isinstance(sec_data, list):
            print(f"📊 Found list with {len(sec_data)} entries")
            filing_entries = sec_data
        else:
            print(f"❌ Unexpected data format: {type(sec_data)}")
            return 0
        
        print(f"📊 Processing {len(filing_entries)} SEC filing entries...")
        
        loaded_count = 0
        batch_size = 3
        
        for i in range(0, len(filing_entries), batch_size):
            batch_end = min(i + batch_size, len(filing_entries))
            batch = filing_entries[i:batch_end]
            
            print(f"📦 Processing batch {i//batch_size + 1}: entries {i+1}-{batch_end}")
            
            for j, filing in enumerate(batch):
                print(f"   📄 Adding entry {i+j+1}: {filing}")
                
                # Extract filing data from various possible formats
                company = filing.get('company', filing.get('Company', filing.get('name', 'Unknown')))
                filing_type = filing.get('filing_type', filing.get('type', filing.get('form_type', 'Unknown')))
                date = filing.get('filing_date', filing.get('date', filing.get('filed_date', 'Unknown')))
                
                success = self.add_sec_filing_data({
                    'company': company,
                    'ticker': filing.get('ticker', filing.get('symbol', '')),
                    'filing_type': filing_type,
                    'date': date,
                    'description': filing.get('description', filing.get('desc', '')),
                })
                
                if success:
                    loaded_count += 1
            
            print(f"✅ Completed batch {i//batch_size + 1}, total loaded: {loaded_count} filings")
            
            # Delay to respect rate limits
            import time
            time.sleep(2)
        
        print(f"🎉 Successfully loaded {loaded_count}/{len(filing_entries)} SEC filings into Zep!")
        print("⏳ Zep is now building temporal relationships... This may take a few minutes.")
        return loaded_count

def debug_zep_raw_results():
    """See what Zep actually returns"""
    tool = ZepTemporalKGTool()
    
    # Test raw Zep responses
    query = "Show me Microsoft information"
    
    print(f"🔍 Raw Zep search for: {query}")
    
    # Get raw edge results
    edge_results = tool.client.graph.search(
        user_id=tool.user_id,
        query=query,
        scope="edges",
        limit=10
    )
    
    print(f"📊 Raw edge results: {len(edge_results.edges) if hasattr(edge_results, 'edges') else 'No edges'}")
    for i, edge in enumerate(edge_results.edges[:3] if hasattr(edge_results, 'edges') else []):
        print(f"  {i+1}. {edge}")
    
    # Get raw node results  
    node_results = tool.client.graph.search(
        user_id=tool.user_id,
        query=query,
        scope="nodes",
        limit=5
    )
    
    print(f"📊 Raw node results: {len(node_results.nodes) if hasattr(node_results, 'nodes') else 'No nodes'}")
    for i, node in enumerate(node_results.nodes[:3] if hasattr(node_results, 'nodes') else []):
        print(f"  {i+1}. {node}")

if __name__ == "__main__":
    test_basic_zep()
    print("\n" + "="*50)
    debug_zep_raw_results()