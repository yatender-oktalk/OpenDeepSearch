import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from smolagents import CodeAgent, LiteLLMModel
from opendeepsearch import OpenDeepSearchTool
from temporal_evaluation.zep.tools.zep_temporal_kg_tool import ZepTemporalKGTool

def create_zep_enhanced_agent():
    """Create ODS agent enhanced with Zep's temporal intelligence"""
    
    print("🚀 Creating Zep-enhanced ODS agent...")
    
    # Create model
    model = LiteLLMModel(
        model_id="gemini/gemini-1.5-flash",
        max_tokens=2048,
        temperature=0.1,
    )
    
    # Create tools
    search_tool = OpenDeepSearchTool(
        model_name="gemini/gemini-1.5-flash",
        reranker="jina",
        search_provider="serper"
    )
    
    zep_tool = ZepTemporalKGTool(
        api_key=os.getenv('ZEP_API_KEY'),
        base_url=os.getenv('ZEP_BASE_URL')
    )
    
    # Enhanced system prompt for Zep integration
    enhanced_model = LiteLLMModel(
        model_id="gemini/gemini-1.5-flash",
        max_tokens=2048,
        temperature=0.1,
        system_prompt="""You are an AI assistant enhanced with Zep's temporal knowledge graph capabilities.

Zep provides state-of-the-art agent memory that:
- Continuously learns and adapts from new information
- Tracks how facts change over time with temporal validity
- Provides 100% improved accuracy on complex recall tasks
- Offers 90% lower response latency for temporal queries
- Automatically detects patterns and correlations across time

When you receive queries involving:
- Temporal patterns, trends, or irregularities
- Historical analysis or time-based comparisons  
- Anomaly detection in time series data
- Multi-entity correlations across time
- Predictive analysis based on historical patterns
- Complex temporal reasoning about evolving states

You MUST use the 'temporal_kg_search' tool first, as Zep's temporal knowledge graph provides:
- Intelligent pattern detection beyond simple data retrieval
- Automated temporal correlation analysis with validity tracking
- Advanced anomaly detection in temporal sequences
- Predictive insights based on continuously updated patterns
- Multi-hop temporal reasoning with historical context

For general information not requiring temporal intelligence, use 'web_search'.

Always leverage Zep's temporal intelligence for time-sensitive analysis."""
    )
    
    # Create enhanced agent
    enhanced_agent = CodeAgent(
        tools=[search_tool, zep_tool],
        model=enhanced_model
    )
    
    print("✅ Zep-enhanced ODS agent created successfully!")
    return enhanced_agent

def test_zep_agent():
    """Test the Zep-enhanced agent with advanced temporal queries"""
    
    agent = create_zep_enhanced_agent()
    
    # Test queries that showcase Zep's temporal intelligence
    test_queries = [
        "Which companies show irregular filing patterns compared to their historical schedule?",
        "Find companies that tend to file SEC reports around the same time periods",
        "Identify any anomalies in Apple's filing timeline over the past 3 years", 
        "Based on historical patterns, predict which companies might file late this quarter",
        "Show me how filing behaviors have evolved over time across different sectors",
        "Detect seasonal patterns in SEC filing submissions",
        "Find correlations between market events and filing timing changes"
    ]
    
    print("\n🧪 Testing Zep temporal intelligence...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/7] Testing: {query}")
        print("-" * 60)
        
        try:
            response = agent.run(query)
            print(f"Response: {str(response)[:400]}...")
            
            # Check if Zep was used
            if "Zep Temporal Knowledge Graph Analysis:" in str(response):
                print("✅ Zep temporal intelligence activated")
            else:
                print("❌ Zep not used - may need prompt adjustment")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_zep_agent()