from smolagents import CodeAgent, GradioUI, LiteLLMModel
from opendeepsearch import OpenDeepSearchTool
from opendeepsearch.temporal_kg_tool import TemporalKGTool
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Add command line argument parsing
parser = argparse.ArgumentParser(description='Run the Gradio demo with custom models and temporal KG')
parser.add_argument('--model-name',
                   default=os.getenv("LITELLM_SEARCH_MODEL_ID", os.getenv("LITELLM_MODEL_ID", "openrouter/google/gemini-2.0-flash-001")),
                   help='Model name for search')
parser.add_argument('--orchestrator-model',
                   default=os.getenv("LITELLM_ORCHESTRATOR_MODEL_ID", os.getenv("LITELLM_MODEL_ID", "openrouter/google/gemini-2.0-flash-001")),
                   help='Model name for orchestration')
parser.add_argument('--reranker',
                   choices=['jina', 'infinity'],
                   default='jina',
                   help='Reranker to use (jina or infinity)')
parser.add_argument('--search-provider',
                   choices=['serper', 'searxng'],
                   default='serper',
                   help='Search provider to use (serper or searxng)')
parser.add_argument('--searxng-instance',
                   help='SearXNG instance URL (required if search-provider is searxng)')
parser.add_argument('--searxng-api-key',
                   help='SearXNG API key (optional)')
parser.add_argument('--serper-api-key',
                   help='Serper API key (optional, will use SERPER_API_KEY env var if not provided)')
parser.add_argument('--openai-base-url',
                   help='OpenAI API base URL (optional, will use OPENAI_BASE_URL env var if not provided)')

# Temporal Knowledge Graph arguments
parser.add_argument('--enable-temporal-kg',
                   action='store_true',
                   help='Enable temporal knowledge graph capabilities')
parser.add_argument('--neo4j-uri',
                   default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                   help='Neo4j database URI')
parser.add_argument('--neo4j-username',
                   default=os.getenv("NEO4J_USERNAME", "neo4j"),
                   help='Neo4j username')
parser.add_argument('--neo4j-password',
                   default=os.getenv("NEO4J_PASSWORD"),
                   help='Neo4j password (required if --enable-temporal-kg is used)')

parser.add_argument('--server-port',
                   type=int,
                   default=7860,
                   help='Port to run the Gradio server on')

args = parser.parse_args()

# Validate arguments
if args.search_provider == 'searxng' and not (args.searxng_instance or os.getenv('SEARXNG_INSTANCE_URL')):
    parser.error("--searxng-instance is required when using --search-provider=searxng")

if args.enable_temporal_kg and not args.neo4j_password:
    parser.error("--neo4j-password is required when using --enable-temporal-kg")

# Set OpenAI base URL if provided via command line
if args.openai_base_url:
    os.environ["OPENAI_BASE_URL"] = args.openai_base_url

# Create the web search tool
search_tool = OpenDeepSearchTool(
    model_name=args.model_name,
    reranker=args.reranker,
    search_provider=args.search_provider,
    serper_api_key=args.serper_api_key,
    searxng_instance_url=args.searxng_instance,
    searxng_api_key=args.searxng_api_key
)

# Create tools list
tools = [search_tool]

# Create temporal KG tool if enabled
if args.enable_temporal_kg:
    print(f"🔍 Enabling Temporal Knowledge Graph:")
    print(f"   Neo4j URI: {args.neo4j_uri}")
    print(f"   Neo4j Username: {args.neo4j_username}")
    
    try:
        temporal_tool = TemporalKGTool(
            neo4j_uri=args.neo4j_uri,
            username=args.neo4j_username,
            password=args.neo4j_password
        )
        tools.append(temporal_tool)
        print(f"✅ Temporal Knowledge Graph tool added successfully!")
        print(f"📊 Available customer data: CUST001, CUST002, CUST003")
        print(f"💡 Try queries like: 'What happened to Customer CUST001?'")
    except Exception as e:
        print(f"❌ Failed to initialize Temporal KG tool: {e}")
        print(f"🔄 Continuing with web search only...")

# Create the model
model = LiteLLMModel(
    model_id=args.orchestrator_model,
    temperature=0.2,
)

# Initialize the agent with all available tools
agent = CodeAgent(tools=tools, model=model)

print(f"\n🚀 Starting Gradio Demo:")
print(f"   Web Search: ✅ ({args.search_provider})")
print(f"   Temporal KG: {'✅' if args.enable_temporal_kg else '❌'}")
print(f"   Tools Available: {len(tools)}")
print(f"   Server Port: {args.server_port}")

# Add a name when initializing GradioUI
GradioUI(agent).launch(server_name="127.0.0.1", server_port=args.server_port, share=False)
