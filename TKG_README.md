# Temporal Knowledge Graph Integration for OpenDeepSearch (TKG-ODS)

## Project Overview

### Core Innovation
Integrating Temporal Knowledge Graphs (TKGs) into Open Deep Search (ODS) agents to enable time-aware reasoning capabilities.

### Problem Statement
Current LLM agents lack temporal awareness - they cannot reliably answer "when did X happen?" or understand chronological context, significantly limiting their effectiveness in enterprise scenarios where historical context matters.

### Solution
Create a `TemporalKGTool` that allows ODS agents to query structured temporal data stored in Neo4j during their reasoning process, enabling accurate timeline-aware responses.

### Value Proposition
Enhanced agents can provide accurate, chronological responses for questions like:
- "What happened to Customer X between 2020-2022?"
- "Show me the timeline of events for Company Y"
- "What was the sequence of interactions before the upgrade?"

Instead of hallucinating or missing temporal context.

## Architecture Overview

### Integration Points in ODS 

#### Current ODS Flow:

```
User Query → ODS Agent → Tools Selection:
├── OpenDeepSearchTool (web search)
└── WolframTool (math/computation)
```
#### Enhanced ODS Flow:

```
User Query → ODS Agent → Tools Selection:
├── OpenDeepSearchTool (web search)
├── WolframTool (math/computation)
└── TemporalKGTool (time-aware queries) ← NEW
```

### TemporalKGTool Pipeline

```
Natural Language Query
            ↓
Temporal Constraint Extraction
            ↓
Cypher Query Generation (LLM-powered)
            ↓
Neo4j Execution
            ↓
Result Formatting & Context Building
            ↓
Timeline-Aware Response
```


## Technical Implementation

### Core Components

#### 1. TemporalKGTool Class
```python
# Location: src/opendeepsearch/temporal_kg_tool.py
class TemporalKGTool:
    name = "temporal_kg_search"
    description = """Search temporal knowledge graph for time-sensitive information."""
    
    def __init__(self, neo4j_uri, username, password, model_name)
    def _extract_temporal_constraints(self, query) -> Dict[str, Any]
    def _generate_cypher_query(self, query, temporal_constraints) -> str
    def _format_temporal_results(self, records, query) -> str
    def forward(self, query) -> str
```

#### 2. Integration Points
- **Agent Integration**: `src/opendeepsearch/ods_agent.py`
- **Prompt Enhancement**: `src/opendeepsearch/prompts.py`
- **Tool Registration**: Following existing pattern from `wolfram_tool.py`

#### 3. Key Methods to Implement

##### Temporal Constraint Extraction
```python
def _extract_temporal_constraints(self, query: str) -> Dict[str, Any]:
    """
    Extract temporal information from natural language:
    - Date ranges: "between 2020-2022", "after January 2023"
    - Relative times: "last month", "past year", "since signup"
    - Event sequences: "before upgrade", "after support ticket"
    - Chronological markers: "first", "last", "previous", "next"
    """
```

##### Cypher Query Generation
```python
def _generate_cypher_query(self, query: str, temporal_constraints: Dict) -> str:
    """
    LLM-powered generation of Cypher queries with temporal awareness:
    - Convert natural language to graph traversal patterns
    - Apply temporal filters and constraints
    - Handle complex temporal relationships
    - Optimize for Neo4j performance
    """
```

##### Result Formatting
```python
def _format_temporal_results(self, records: List[Dict], query: str) -> str:
    """
    Format Neo4j results for agent consumption:
    - Chronological ordering of events
    - Timeline visualization in text
    - Contextual summaries
    - Relationship explanations
    """
```

## Data Model & Schema

### Neo4j Schema Design

#### Core Node Types
```cypher
// Entities
(:Customer {id, name, industry, created_date})
(:Product {id, name, category})
(:User {id, email, role, created_date})

// Events (time-stamped activities)
(:Event:Signup {date, plan, source})
(:Event:Login {timestamp, ip_address, device})
(:Event:Purchase {date, amount, product_id})
(:Event:Upgrade {date, from_plan, to_plan, reason})
(:Event:SupportTicket {created_date, resolved_date, issue_type, priority})
(:Event:Interaction {timestamp, channel, type, outcome})
```

#### Temporal Relationships
```cypher
// Time-based relationships with timestamps
(:Customer)-[:PERFORMED {timestamp}]->(:Event)
(:Event)-[:FOLLOWED_BY {duration}]->(:Event)
(:Event)-[:OCCURRED_DURING {period}]->(:TimeWindow)
(:Customer)-[:IN_STATE {from_date, to_date, state}]->(:Status)
```

#### Sample Data Structure
```cypher
// Customer lifecycle example
CREATE (c:Customer {id: "CUST001", name: "Acme Corp", industry: "Tech"})
CREATE (s:Event:Signup {date: datetime("2020-01-15"), plan: "basic", source: "web"})
CREATE (l1:Event:Login {timestamp: datetime("2020-01-16T09:00:00"), device: "desktop"})
CREATE (u:Event:Upgrade {date: datetime("2020-06-01"), from_plan: "basic", to_plan: "premium"})
CREATE (t:Event:SupportTicket {
  created_date: datetime("2020-08-15"), 
  resolved_date: datetime("2020-08-17"),
  issue_type: "integration", 
  priority: "high"
})

// Temporal relationships
CREATE (c)-[:PERFORMED {timestamp: datetime("2020-01-15")}]->(s)
CREATE (c)-[:PERFORMED {timestamp: datetime("2020-01-16T09:00:00")}]->(l1)
CREATE (c)-[:PERFORMED {timestamp: datetime("2020-06-01")}]->(u)
CREATE (c)-[:PERFORMED {timestamp: datetime("2020-08-15")}]->(t)
CREATE (s)-[:FOLLOWED_BY {duration: duration("P136D")}]->(u)
```

## Prompt Engineering

### Temporal Reasoning Prompts

#### Tool Selection Prompt
```python
TEMPORAL_REASONING_PROMPT = """
You have access to a temporal knowledge graph tool for time-sensitive queries.

Use temporal_kg_search when queries involve:
- Specific time periods: "between 2020-2022", "after January 2023"
- Chronological sequences: "what happened first", "timeline of events"
- Temporal relationships: "before signup", "during trial period" 
- Historical context: "previous interactions", "past behavior"
- Event causality: "what led to", "what happened after"

Examples requiring temporal_kg_search:
✓ "What happened to Customer X between 2020-2022?"
✓ "Show me the timeline of support tickets for Company Y"
✓ "What events occurred after the user's last login?"
✓ "Which customers upgraded within 30 days of signup?"

Use web search for:
✗ Current events, news, general knowledge
✗ Non-temporal factual information
"""
```

#### Cypher Generation Prompt
```python
CYPHER_GENERATION_PROMPT = """
Generate a Cypher query for Neo4j based on the natural language query and temporal constraints.

Schema Overview:
- Nodes: Customer, User, Event (Signup, Login, Purchase, Upgrade, SupportTicket)
- Relationships: PERFORMED (with timestamp), FOLLOWED_BY (with duration)

Temporal Constraint Patterns:
- Date ranges: WHERE event.date >= datetime("{start}") AND event.date <= datetime("{end}")
- Relative time: WHERE event.timestamp > datetime() - duration("{period}")
- Event sequences: MATCH (e1)-[:FOLLOWED_BY]->(e2)

Query: {query}
Constraints: {temporal_constraints}

Generate optimized Cypher:
"""
```

## Evaluation Framework

### Test Categories

#### 1. Single-hop Temporal Queries
- "When did Customer X sign up?"
- "What was the last login date for User Y?"
- "How many support tickets were created in Q1 2023?"

#### 2. Multi-hop Temporal Queries  
- "What happened between Customer X's signup and first support ticket?"
- "Show me all events for Customer Y in chronological order"
- "What was the average time from signup to first purchase?"

#### 3. Temporal Reasoning
- "Which customers upgraded within 30 days of signup?"
- "What patterns exist in support ticket creation times?"
- "How did customer behavior change after the product update?"

#### 4. Chronological Context
- "What was the sequence of events leading to Customer X's cancellation?"
- "Compare Customer A and B's first-month activity timelines"
- "What happened before and after the major system outage?"

### Success Metrics

#### Quantitative Metrics
- **Temporal Accuracy**: % of correct temporal facts vs baseline agents
- **Completeness**: % of relevant temporal context captured
- **Tool Selection**: Appropriate use of temporal tool vs web search
- **Query Success Rate**: % of valid Cypher queries generated
- **Response Latency**: Time to generate temporal responses

#### Qualitative Metrics
- **Timeline Coherence**: Logical chronological ordering
- **Context Relevance**: Appropriate temporal context inclusion
- **Relationship Clarity**: Clear explanation of temporal relationships
- **Narrative Quality**: Coherent storytelling with temporal elements

## Setup & Configuration

### Prerequisites
```bash
# Neo4j Database
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Python Dependencies
pip install neo4j-driver python-dateutil dateparser
```

### Environment Variables
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"  
export NEO4J_PASSWORD="password"
export TEMPORAL_KG_ENABLED="true"
```

### ODS Integration Configuration
```python
# Enhanced ODS initialization with temporal capabilities
search_agent = OpenDeepSearchTool(
    model_name="openrouter/google/gemini-2.0-flash-001",
    reranker="jina",
    enable_temporal_kg=True,
    neo4j_config={
        "uri": os.getenv("NEO4J_URI"),
        "username": os.getenv("NEO4J_USERNAME"),
        "password": os.getenv("NEO4J_PASSWORD")
    }
)
```

## Dataset Generation

### Synthetic Customer Lifecycle Data
```python
# Generate realistic temporal data for evaluation
entities = {
    "customers": 1000,      # B2B customers
    "users": 5000,          # Individual users  
    "events_per_customer": 20-50,  # Signup → Login → Usage → Support → Upgrade/Churn
    "time_span": "2020-2024",      # 4 years of historical data
    "event_types": [
        "signup", "login", "feature_usage", "support_ticket", 
        "upgrade", "downgrade", "payment", "churn"
    ]
}
```

### Temporal Patterns to Model
- Customer lifecycle stages with realistic durations
- Seasonal patterns in signups and usage
- Support ticket clustering around product releases
- Upgrade patterns based on usage milestones
- Churn patterns with leading indicators

## Novelty & Impact

### Innovation Claims
- **First open-source implementation** of temporal graph integration in LLM agent systems
- **Novel architecture** for time-aware reasoning in conversational agents
- **Practical solution** for enterprise temporal reasoning requirements

### Competitive Advantage
- ODS currently has no temporal capabilities
- Zep's temporal approach is proprietary and closed-source
- This enhancement positions ODS as the leading open-source solution for temporal reasoning

### Enterprise Applications
- Customer journey analysis
- Historical data exploration  
- Compliance and audit queries
- Trend analysis and forecasting
- Root cause analysis with temporal context

## Future Enhancements

### Phase 2 Features
- **Temporal Embeddings**: Vector representations of time-aware entities
- **Multi-scale Temporal Reasoning**: From seconds to years
- **Temporal Conflict Resolution**: Handling inconsistent timestamps
- **Predictive Temporal Queries**: "What is likely to happen next?"

### Phase 3 Vision
- **Distributed Temporal Graphs**: Multi-database temporal reasoning
- **Real-time Temporal Updates**: Live event stream integration
- **Temporal Explanation Generation**: "Why did this temporal pattern occur?"
- **Cross-domain Temporal Transfer**: Learning temporal patterns across industries

---

## Development Status

### Current Implementation
- [x] Basic TemporalKGTool structure (`src/opendeepsearch/temporal_kg_tool.py`)
- [x] Temporal constraint extraction
- [x] Cypher query generation
- [x] Result formatting
- [x] ODS agent integration
- [x] Evaluation framework
- [x] Dataset generation

### Next Steps
1. Enhance temporal constraint parsing with more patterns
2. Improve Cypher query generation with LLM
3. Add more sophisticated result formatting
4. Expand evaluation dataset
5. Add more domain-specific temporal patterns
6. Implement real-time temporal updates

---

*This README serves as the comprehensive technical specification and context document for the Temporal Knowledge Graph enhancement to OpenDeepSearch.*

## Development & Deployment

### Using Nix

#### Prerequisites
- [Nix](https://nixos.org/download.html) installed on your system
- [Nix Flakes](https://nixos.wiki/wiki/Flakes) enabled

#### Development Environment
1. Enter the development shell:
```bash
# Using flakes (recommended)
nix develop

# Using legacy shell.nix
nix-shell
```

The shell will automatically:
- Set up the required environment variables
- Create Neo4j data and log directories
- Start Neo4j if it's not already running

2. Run the application:
```bash
python -m opendeepsearch.main
```

To stop Neo4j when you're done:
```bash
neo4j stop
```

#### Building Docker Image with Nix
1. Build the Docker image:
```bash
# Using flakes
nix build .#dockerImage

# The image will be available at ./result
```

2. Load the image into Docker:
```bash
docker load < result
```

### Using Docker

#### Quick Start
1. Build and start the containers:
```bash
docker-compose up --build
```

2. Access the services:
- Neo4j Browser: http://localhost:7474
- Neo4j Bolt: localhost:7687
- Application: http://localhost:8000

3. Stop the services:
```bash
docker-compose down
```

#### Environment Variables
The following environment variables can be configured:
- `NEO4J_AUTH`: Neo4j authentication (default: neo4j/password)
- `NEO4J_URI`: Neo4j connection URI (default: bolt://localhost:7687)
- `NEO4J_USERNAME`: Neo4j username (default: neo4j)
- `NEO4J_PASSWORD`: Neo4j password (default: password)
- `TEMPORAL_KG_ENABLED`: Enable temporal knowledge graph (default: true)

#### Data Persistence
The Docker setup includes two volumes:
- `neo4j_data`: Stores Neo4j database files
- `neo4j_logs`: Stores Neo4j logs

To remove all data:
```bash
docker-compose down -v
```

## Evaluation stretigies

temporal_evaluation/
├── datasets/
│   ├── financial_data.json
│   ├── sec_filings.json
│   ├── clinical_trials.json
│   └── supply_chain.json
├── financial_data/
│   ├── collect_data.py          # Creates datasets/financial_data.json
│   ├── load_dataset.py          # Loads from datasets/financial_data.json to Neo4j
│   ├── generate_queries.py
│   ├── run_evaluation.py
│   └── analyze_results.py
├── shared/
│   ├── dataset_schema.py        # Standard dataset format
│   ├── neo4j_loader.py         # Generic Neo4j loader
│   └── base_evaluator.py
└── setup_evaluation.py         # One-click setup from datasets