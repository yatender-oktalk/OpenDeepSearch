# 🔍OpenDeepSearch: Democratizing Search with Open-source Reasoning Models and Reasoning Agents 🚀

<!-- markdownlint-disable first-line-h1 -->
<!-- markdownlint-disable html -->
<!-- markdownlint-disable no-duplicate-header -->

<div align="center">
    <img src="./assets/sentient-logo-narrow.png" alt="alt text" width="60%"/>
</div>

<hr>
<div align="center" style="line-height: 1;">
  <a href="https://sentient.xyz/" target="_blank" style="margin: 2px;">
    <img alt="Homepage" src="https://img.shields.io/badge/Sentient-Homepage-%23EAEAEA?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzNDEuMzMzIiBoZWlnaHQ9IjM0MS4zMzMiIHZlcnNpb249IjEuMCIgdmlld0JveD0iMCAwIDI1NiAyNTYiPjxwYXRoIGQ9Ik0xMzIuNSAyOC40Yy0xLjUgMi4yLTEuMiAzLjkgNC45IDI3LjIgMy41IDEzLjcgOC41IDMzIDExLjEgNDIuOSAyLjYgOS45IDUuMyAxOC42IDYgMTkuNCAzLjIgMy4zIDExLjctLjggMTMuMS02LjQuNS0xLjktMTcuMS03Mi0xOS43LTc4LjYtMS4yLTMtNy41LTYuOS0xMS4zLTYuOS0xLjYgMC0zLjEuOS00LjEgMi40ek0xMTAgMzBjLTEuMSAxLjEtMiAzLjEtMiA0LjVzLjkgMy40IDIgNC41IDMuMSAyIDQuNSAyIDMuNC0uOSA0LjUtMiAyLTMuMSAyLTQuNS0uOS0zLjQtMi00LjUtMy4xLTItNC41LTItMy40LjktNC41IDJ6TTgxLjUgNDYuMWMtMi4yIDEuMi00LjYgMi44LTUuMiAzLjctMS44IDIuMy0xLjYgNS42LjUgNy40IDEuMyAxLjIgMzIuMSAxMC4yIDQ1LjQgMTMuMyAzIC44IDYuOC0yLjIgNi44LTUuMyAwLTMuNi0yLjItOS4yLTMuOS0xMC4xQzEyMy41IDU0LjIgODcuMiA0NCA4NiA0NGMtLjMuMS0yLjMgMS00LjUgMi4xek0xNjUgNDZjLTEuMSAxLjEtMiAyLjUtMiAzLjIgMCAyLjggMTEuMyA0NC41IDEyLjYgNDYuNS45IDEuNSAyLjQgMi4zIDQuMiAyLjMgMy44IDAgOS4yLTUuNiA5LjItOS40IDAtMS41LTIuMS0xMC45LTQuNy0yMC44bC00LjctMTguMS00LjUtMi44Yy01LjMtMy40LTcuNC0zLjYtMTAuMS0uOXpNNDguNyA2NS4xYy03LjcgNC4xLTYuOSAxMC43IDEuNSAxMyAyLjQuNiAyMS40IDUuOCA0Mi4yIDExLjYgMjIuOCA2LjIgMzguOSAxMC4yIDQwLjMgOS44IDMuNS0uOCA0LjYtMy44IDMuMi04LjgtMS41LTUuNy0yLjMtNi41LTguMy04LjJDOTQuMiA3My4xIDU2LjYgNjMgNTQuOCA2M2MtMS4zLjEtNCAxLTYuMSAyLjF6TTE5OC4yIDY0LjdjLTMuMSAyLjgtMy41IDUuNi0xLjEgOC42IDQgNS4xIDEwLjkgMi41IDEwLjktNC4xIDAtNS4zLTUuOC03LjktOS44LTQuNXpNMTgxLjggMTEzLjFjLTI3IDI2LjQtMzEuOCAzMS41LTMxLjggMzMuOSAwIDEuNi43IDMuNSAxLjUgNC40IDEuNyAxLjcgNy4xIDMgMTAuMiAyLjQgMi4xLS4zIDU2LjktNTMuNCA1OS01Ny4xIDEuNy0zLjEgMS42LTkuOC0uMy0xMi41LTMuNi01LjEtNC45LTQuMi0zOC42IDI4Ljl6TTM2LjYgODguMWMtNSA0LTIuNCAxMC45IDQuMiAxMC45IDMuMyAwIDYuMi0yLjkgNi4yLTYuMyAwLTIuMS00LjMtNi43LTYuMy02LjctLjggMC0yLjYuOS00LjEgMi4xek02My40IDk0LjVjLTEuNi43LTguOSA3LjMtMTYuMSAxNC43TDM0IDEyMi43djUuNmMwIDYuMyAxLjYgOC43IDUuOSA4LjcgMi4xIDAgNi0zLjQgMTkuOS0xNy4zIDkuNS05LjUgMTcuMi0xOCAxNy4yLTE4LjkgMC00LjctOC40LTguNi0xMy42LTYuM3pNNjIuOSAxMzAuNiAzNCAxNTkuNXY1LjZjMCA2LjIgMS44IDguOSA2IDguOSAzLjIgMCA2Ni02Mi40IDY2LTY1LjYgMC0zLjMtMy41LTUuNi05LjEtNi4ybC01LS41LTI5IDI4Ljl6TTE5Ni4zIDEzNS4yYy05IDktMTYuNiAxNy4zLTE2LjkgMTguNS0xLjMgNS4xIDIuNiA4LjMgMTAgOC4zIDIuOCAwIDUuMi0yIDE3LjktMTQuOCAxNC41LTE0LjcgMTQuNy0xNC45IDE0LjkgMTQuNy0xOS4zIDAtNS44LTIuMi04LjktNi4yLTguOS0yLjYgMC01LjQgMi4zLTE5LjUgMTYuMnpNOTYgMTM2LjhjLTIuOS45LTggNi42LTggOSAwIDEuMyAyLjkgMTMuNCA2LjQgMjcgMy42IDEzLjYgNy45IDMwLjMgOS43IDM3LjIgMS43IDYuOSAzLjYgMTMuMyA0LjEgMTQuMi41IDEgMi42IDIuNyA0LjggMy44IDYuOCAzLjUgMTEgMi4zIDExLTMuMiAwLTMtMjAuNi04My4xLTIyLjEtODUuOS0uOS0xLjktMy42LTIuOC01LjktMi4xek0xMjAuNSAxNTguNGMtMS45IDIuOS0xLjIgOC41IDEuNCAxMS42IDEuMSAxLjQgMTIuMSA0LjkgMzkuNiAxMi41IDIwLjkgNS44IDM4LjggMTAuNSAzOS44IDEwLjVzMy42LTEgNS43LTIuMmM4LjEtNC43IDcuMS0xMC42LTIuMy0xMy4yLTI4LjItOC4xLTc4LjUtMjEuNi04MC4zLTIxLjYtMS40IDAtMyAxLTMuOSAyLjR6TTIxMC43IDE1OC44Yy0xLjggMS45LTIuMiA1LjktLjkgNy44IDEuNSAyLjMgNSAzLjQgNy42IDIuNCA2LjQtMi40IDUuMy0xMS4yLTEuNS0xMS44LTIuNC0uMi00IC4zLTUuMiAxLjZ6TTY5LjYgMTYyYy0yIDIuMi0zLjYgNC4zLTMuNiA0LjguMSAyLjYgMTAuMSAzOC42IDExLjEgMzkuOSAyLjIgMi42IDkgNS41IDExLjUgNC45IDUtMS4zIDQuOS0zLTEuNS0yNy43LTMuMy0xMi43LTYuNS0yMy43LTcuMi0yNC41LTIuMi0yLjctNi40LTEuNy0xMC4zIDIuNnpNNDkuNiAxODEuNWMtMi40IDIuNS0yLjkgNS40LTEuMiA4QzUyIDE5NSA2MCAxOTMgNjAgMTg2LjZjMC0xLjktLjgtNC0xLjgtNC45LTIuMy0yLjEtNi42LTIuMi04LjYtLjJ6TTEyOC41IDE4N2MtMi4zIDIuNS0xLjMgMTAuMyAxLjYgMTIuOCAyLjIgMS45IDM0LjggMTEuMiAzOS40IDExLjIgMy42IDAgMTAuMS00LjEgMTEtNyAuNi0xLjktMS43LTctMy4xLTctLjIgMC0xMC4zLTIuNy0yMi4zLTZzLTIyLjUtNi0yMy4zLTZjLS44IDAtMi4zLjktMy4zIDJ6TTEzNi43IDIxNi44Yy0zLjQgMy44LTEuNSA5LjUgMy41IDEwLjcgMy45IDEgOC4zLTMuNCA3LjMtNy4zLTEuMi01LjEtNy41LTcuMS0xMC44LTMuNHoiLz48L3N2Zz4%3D&link=https%3A%2F%2Fhuggingface.co%2FSentientagi" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://github.com/sentient-agi" target="_blank" style="margin: 2px;">
    <img alt="GitHub" src="https://img.shields.io/badge/Github-sentient_agi-181717?logo=github" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://huggingface.co/Sentientagi" target="_blank" style="margin: 2px;">
    <img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-SentientAGI-ffc107?color=ffc107&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

<div align="center" style="line-height: 1;">
  <a href="https://discord.gg/sentientfoundation" target="_blank" style="margin: 2px;">
    <img alt="Discord" src="https://img.shields.io/badge/Discord-SentientAGI-7289da?logo=discord&logoColor=white&color=7289da" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://x.com/SentientAGI" target="_blank" style="margin: 2px;">
    <img alt="Twitter Follow" src="https://img.shields.io/badge/-SentientAGI-grey?logo=x&link=https%3A%2F%2Fx.com%2FSentientAGI%2F" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

<h4 align="center">
        <a href="https://arxiv.org/pdf/2503.20201"> Paper  </a>
</h4>

## Description 📝

OpenDeepSearch is a lightweight yet powerful search tool designed for seamless integration with AI agents. It enables deep web search and retrieval, optimized for use with Hugging Face's **[SmolAgents](https://github.com/huggingface/smolagents)** ecosystem.

**🆕 NEW: Temporal Knowledge Graph Integration** - OpenDeepSearch now supports time-aware reasoning through integrated Temporal Knowledge Graphs, enabling agents to answer chronological questions with precise historical context.

<div align="center">
    <img src="./assets/evals.png" alt="Evaluation Results" width="80%"/>
</div>

- **Performance**: ODS performs on par with closed source search alternatives on single-hop queries such as [SimpleQA](https://openai.com/index/introducing-simpleqa/) 🔍.
- **Advanced Capabilities**: ODS performs much better than closed source search alternatives on multi-hop queries such as [FRAMES bench](https://huggingface.co/datasets/google/frames-benchmark) 🚀.
- **Temporal Reasoning**: First open-source implementation of temporal graph integration in LLM agent systems, enabling accurate timeline-aware responses.

## Table of Contents 📑

- [🔍OpenDeepSearch: Democratizing Search with Open-source Reasoning Models and Reasoning Agents 🚀](#opendeepsearch-democratizing-search-with-open-source-reasoning-models-and-reasoning-agents-)
  - [Description 📝](#description-)
  - [Table of Contents 📑](#table-of-contents-)
  - [Features ✨](#features-)
  - [Installation 📚](#installation-)
  - [Setup](#setup)
    - [Core Setup](#core-setup)
    - [Temporal Knowledge Graph Setup (Optional)](#temporal-knowledge-graph-setup-optional)
  - [Usage ️](#usage-️)
    - [Using OpenDeepSearch Standalone 🔍](#using-opendeepsearch-standalone-)
    - [Running the Gradio Demo 🖥️](#running-the-gradio-demo-️)
    - [Enhanced Demo with Temporal Knowledge Graph 🕒](#enhanced-demo-with-temporal-knowledge-graph-)
    - [Integrating with SmolAgents \& LiteLLM 🤖⚙️](#integrating-with-smolagents--litellm-️)
    - [Multi-Tool Agent with Temporal Reasoning 🧠](#multi-tool-agent-with-temporal-reasoning-)
  - [Search Modes 🔄](#search-modes-)
    - [Default Mode ⚡](#default-mode-)
    - [Pro Mode 🔍](#pro-mode-)
  - [Temporal Knowledge Graph 🕒](#temporal-knowledge-graph-)
    - [Features](#features-1)
    - [Example Queries](#example-queries)
    - [Data Model](#data-model)
  - [Zep Temporal Knowledge Graph Evaluation 🧪](#zep-temporal-knowledge-graph-evaluation-)
    - [Overview](#overview)
    - [Quick Start](#quick-start)
    - [Evaluation Results](#evaluation-results)
  - [Acknowledgments 💡](#acknowledgments-)
  - [Citation](#citation)
  - [Contact 📩](#contact-)

## Features ✨

- **Semantic Search** 🧠: Leverages **[Crawl4AI](https://github.com/unclecode/crawl4ai)** and semantic search rerankers (such as [Qwen2-7B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct/tree/main) and [Jina AI](https://jina.ai/)) to provide in-depth results
- **Two Modes of Operation** ⚡:
  - **Default Mode**: Quick and efficient search with minimal latency.
  - **Pro Mode (Deep Search)**: More in-depth and accurate results at the cost of additional processing time.
- **Temporal Knowledge Graph Integration** 🕒: Revolutionary time-aware reasoning capabilities:
  - Customer journey analysis with precise timelines
  - Historical event tracking and chronological context
  - Temporal relationship understanding ("what happened before/after")
  - Enterprise-grade temporal data queries
- **Multi-Tool Architecture** 🔧: Intelligent tool selection between web search and temporal reasoning
- **Optimized for AI Agents** 🤖: Works seamlessly with **SmolAgents** like `CodeAgent`.
- **Fast and Lightweight** ⚡: Designed for speed and efficiency with minimal setup.
- **Extensible** 🔌: Easily configurable to work with different models and APIs.

## Installation 📚

To install OpenDeepSearch, run:

```bash
pip install -e . #you can also use: uv pip install -e .
pip install -r requirements.txt #you can also use: uv pip install -r requirements.txt
```

Note: you must have `torch` installed.
Note: using `uv` instead of regular `pip` makes life much easier!

### Using PDM (Alternative Package Manager) 📦

You can also use PDM as an alternative package manager for OpenDeepSearch. PDM is a modern Python package and dependency manager supporting the latest PEP standards.

```bash
# Install PDM if you haven't already
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -

# Initialize a new PDM project
pdm init

# Install OpenDeepSearch and its dependencies
pdm install

# Activate the virtual environment
eval "$(pdm venv activate)"
```

PDM offers several advantages:
- Lockfile support for reproducible installations
- PEP 582 support (no virtual environment needed)
- Fast dependency resolution
- Built-in virtual environment management

## Setup

### Core Setup

1. **Choose a Search Provider**:
   - **Option 1: Serper.dev**: Get **free 2500 credits** and add your API key.
     - Visit [serper.dev](https://serper.dev) to create an account.
     - Retrieve your API key and store it as an environment variable:

     ```bash
     export SERPER_API_KEY='your-api-key-here'
     ```

   - **Option 2: SearXNG**: Use a self-hosted or public SearXNG instance.
     - Specify the SearXNG instance URL when initializing OpenDeepSearch.
     - Optionally provide an API key if your instance requires authentication:

     ```bash
     export SEARXNG_INSTANCE_URL='https://your-searxng-instance.com'
     export SEARXNG_API_KEY='your-api-key-here'  # Optional
     ```

2. **Choose a Reranking Solution**:
   - **Quick Start with Jina**: Sign up at [Jina AI](https://jina.ai/) to get an API key for immediate use
   - **Self-hosted Option**: Set up [Infinity Embeddings](https://github.com/michaelfeil/infinity) server locally with open source models such as [Qwen2-7B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct/tree/main)
   - For more details on reranking options, see our [Rerankers Guide](src/opendeepsearch/ranking_models/README.md)

3. **Set up LiteLLM Provider**:
   - Choose a provider from the [supported list](https://docs.litellm.ai/docs/providers/), including:
     - OpenAI
     - Anthropic
     - Google (Gemini)
     - OpenRouter
     - HuggingFace
     - Fireworks
     - And many more!
   - Set your chosen provider's API key as an environment variable:
   ```bash
   export <PROVIDER>_API_KEY='your-api-key-here'  # e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY
   ```
   - For OpenAI, you can also set a custom base URL (useful for self-hosted endpoints or proxies):
   ```bash
   export OPENAI_BASE_URL='https://your-custom-openai-endpoint.com'
   ```
   - You can set default LiteLLM model IDs for different tasks:
   ```bash
   # General default model (fallback for all tasks)
   export LITELLM_MODEL_ID='openrouter/google/gemini-2.0-flash-001'

   # Task-specific models
   export LITELLM_SEARCH_MODEL_ID='openrouter/google/gemini-2.0-flash-001'  # For search tasks
   export LITELLM_ORCHESTRATOR_MODEL_ID='openrouter/google/gemini-2.0-flash-001'  # For agent orchestration
   export LITELLM_EVAL_MODEL_ID='gpt-4o-mini'  # For evaluation tasks
   ```
   - When initializing OpenDeepSearch, you can specify your chosen model using the provider's format (this will override the environment variables):
   ```python
   search_agent = OpenDeepSearchTool(model_name="provider/model-name")  # e.g., "anthropic/claude-3-opus-20240229", 'huggingface/microsoft/codebert-base', 'openrouter/google/gemini-2.0-flash-001'
   ```

### Temporal Knowledge Graph Setup (Optional)

For enhanced temporal reasoning capabilities, set up Neo4j:

1. **Install Neo4j Database**:
   ```bash
   # Using Docker (recommended)
   docker run --name neo4j-tkg \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your-password \
     neo4j:latest
   ```

2. **Set Environment Variables**:
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USERNAME="neo4j"
   export NEO4J_PASSWORD="your-password"
   ```

3. **Create Sample Data** (for testing):
   ```bash
   python scripts/create_test_data.py
   python scripts/add_strategic_test_data.py
   ```

## Usage ️

You can use OpenDeepSearch independently or integrate it with **SmolAgents** for enhanced reasoning and code generation capabilities.

### Using OpenDeepSearch Standalone 🔍

```python
from opendeepsearch import OpenDeepSearchTool
import os

# Set environment variables for API keys
os.environ["SERPER_API_KEY"] = "your-serper-api-key-here"
os.environ["OPENROUTER_API_KEY"] = "your-openrouter-api-key-here"
os.environ["JINA_API_KEY"] = "your-jina-api-key-here"

# Basic web search
search_agent = OpenDeepSearchTool(
    model_name="openrouter/google/gemini-2.0-flash-001",
    reranker="jina"
)

if not search_agent.is_initialized:
    search_agent.setup()
    
query = "Fastest land animal?"
result = search_agent.forward(query)
print(result)
```

### Running the Gradio Demo 🖥️

**Basic Demo (Web Search Only)**:
```bash
python gradio_demo.py
```

**With Custom Configuration**:
```bash
python gradio_demo.py --model-name "openrouter/google/gemini-2.0-flash-001" --reranker "jina"
```

### Enhanced Demo with Temporal Knowledge Graph 🕒

**Enable Temporal Reasoning**:
```bash
python gradio_demo.py --enable-temporal-kg --neo4j-password=your-password
```

**Full Configuration with Temporal KG**:
```bash
python gradio_demo.py \
  --enable-temporal-kg \
  --neo4j-password=your-password \
  --model-name="openrouter/google/gemini-2.0-flash-001" \
  --reranker=jina \
  --server-port=7860
```

Available Gradio demo options:
- `--model-name`: LLM model to use for search
- `--orchestrator-model`: LLM model for the agent orchestrator
- `--reranker`: Reranker to use (`jina` or `infinity`)
- `--search-provider`: Search provider to use (`serper` or `searxng`)
- `--enable-temporal-kg`: Enable temporal knowledge graph capabilities
- `--neo4j-uri`: Neo4j database URI (default: bolt://localhost:7687)
- `--neo4j-username`: Neo4j username (default: neo4j)
- `--neo4j-password`: Neo4j password (required if temporal KG enabled)
- `--server-port`: Port to run the Gradio server on (default: 7860)

### Integrating with SmolAgents & LiteLLM 🤖⚙️

```python
from smolagents import ReactAgent, LiteLLMModel
from opendeepsearch import OpenDeepSearchTool

# Initialize the search tool
search_tool = OpenDeepSearchTool(
    model_name="openrouter/google/gemini-2.0-flash-001",
    reranker="jina"
)

# Create a LiteLLM model for the agent
model = LiteLLMModel(
    model_id="openrouter/google/gemini-2.0-flash-001",
    temperature=0.2,
)

# Create and run the agent
agent = ReactAgent(tools=[search_tool], model=model)
result = agent.run("What are the latest developments in quantum computing?")
print(result)
```

### Multi-Tool Agent with Temporal Reasoning 🧠

```python
from smolagents import ReactAgent, LiteLLMModel
from opendeepsearch import OpenDeepSearchTool
from opendeepsearch.temporal_kg_tool import TemporalKGTool

# Create web search tool
search_tool = OpenDeepSearchTool(
    model_name="openrouter/google/gemini-2.0-flash-001",
    reranker="jina"
)

# Create temporal knowledge graph tool
temporal_tool = TemporalKGTool(
    neo4j_uri="bolt://localhost:7687",
    username="neo4j",
    password="your-password"
)

# Create multi-tool agent
model = LiteLLMModel(model_id="openrouter/google/gemini-2.0-flash-001")
agent = ReactAgent(tools=[search_tool, temporal_tool], model=model)

# The agent automatically chooses the right tool
print("🔍 Web Search Query:")
result1 = agent.run("What is machine learning?")
print(result1)

print("\n🕒 Temporal Query:")
result2 = agent.run("What happened to Customer CUST001?")
print(result2)
```

## Search Modes 🔄

### Default Mode ⚡
```python
result = search_agent.forward("query", pro_mode=False)
```
- Quick search with minimal processing time
- Suitable for simple factual queries
- Lower resource consumption

### Pro Mode 🔍
```python
result = search_agent.forward("query", pro_mode=True)
```
- Deep analysis with comprehensive source processing
- Better for complex, multi-step reasoning
- Higher accuracy at the cost of processing time

## Temporal Knowledge Graph 🕒

### Features
- **Time-Aware Reasoning**: Understand chronological relationships and temporal context
- **Customer Journey Analysis**: Track customer interactions over time
- **Historical Event Tracking**: Query past events with precise timestamps
- **Enterprise Integration**: Built for real-world business scenarios

### Example Queries
**Customer Timeline Analysis**:
- "What happened to Customer CUST001?"
- "Show me the timeline for Customer CUST003"
- "What events occurred after Customer CUST001's upgrade?"

**Temporal Relationships**:
- "What happened between Customer CUST002's signup and first support ticket?"
- "Which customers upgraded within 30 days of signup?"
- "Show me login activity for Customer CUST003 in February 2023"

**Business Intelligence**:
- "What was the sequence of events leading to Customer CUST003's cancellation?"
- "Compare Customer A and B's first-month activity timelines"
- "What patterns exist in support ticket creation times?"

### Data Model
The temporal knowledge graph uses Neo4j with the following structure:

**Entities**:
- `Customer`: Business customers with IDs and company names
- `Event`: Time-stamped activities (Signup, Login, Purchase, Support, etc.)

**Relationships**:
- `PERFORMED`: Links customers to their events with timestamps
- `FOLLOWED_BY`: Temporal sequences between events

**Sample Data**:
- **CUST001**: Success journey (signup → upgrade → purchase)
- **CUST002**: Support-driven journey (signup → support ticket → resolution)
- **CUST003**: Churn scenario (signup → usage → cancellation)

## Zep Temporal Knowledge Graph Evaluation 🧪

### Overview
OpenDeepSearch includes a comprehensive evaluation framework for testing temporal reasoning capabilities using **Zep Cloud's** advanced knowledge graph technology. This evaluation compares baseline web search + LLM against enhanced Zep Temporal Knowledge Graph capabilities.

### Quick Start

**One-Click Setup**:
```bash
# macOS/Linux
./setup_zep_evaluation.sh

# Windows
setup_zep_evaluation.bat
```

**Manual Setup** (5 steps):
```bash
# 1. Environment setup
git clone https://github.com/yatender-oktalk/OpenDeepSearch.git
cd OpenDeepSearch
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
pip install zep-cloud

# 2. Configure Zep
echo "ZEP_API_KEY=your_api_key_here" > .env
echo "ZEP_BASE_URL=https://api.getzep.com" >> .env

# 3. Load data
cd temporal_evaluation/zep
python load_sec_data_to_zep.py

# 4. Test setup
python test_basic_zep.py

# 5. Run evaluation
python run_zep_evaluation.py
```

**Get Zep API Key**: [Sign up at getzep.com](https://www.getzep.com/)

### Evaluation Results

The evaluation measures temporal intelligence improvements across multiple dimensions:

**Performance Metrics**:
- **Temporal Intelligence**: +40-60% improvement over baseline
- **Response Time**: 3-10x faster than web search
- **Zep Activation Rate**: 90-100% for temporal queries

**Sample Results**:
```
🎯 ZEP TEMPORAL KNOWLEDGE GRAPH EVALUATION SUMMARY
===============================================
📊 TEMPORAL INTELLIGENCE SCORES:
  Baseline (Web Search):     42.3%
  Enhanced (+ Zep TKG):      89.7%
  Average Improvement:       +47.4%
  Zep Activation Rate:       100.0%

📈 CAPABILITY IMPROVEMENTS:
  Pattern Detection........... +52.1%
  Temporal Correlation....... +48.3%
  Anomaly Detection.......... +45.7%
  Predictive Analysis........ +43.2%
  Temporal Reasoning......... +49.8%

✅ SUCCESS METRICS:
  Queries with Zep Usage:    5/5
  Success Rate:             100.0%
  🎉 Excellent Zep integration!
```

**Evaluation Queries**:
- "Which companies show irregular filing patterns compared to their historical schedule?"
- "Show me Apple's SEC filing timeline and patterns"
- "Compare filing frequencies between Microsoft and Apple over time"
- "Find companies with unusual gaps between quarterly filings"
- "Identify seasonal patterns in SEC filing submissions"

**Documentation**:
- **Complete Setup Guide**: `ZEP_SETUP_GUIDE.md`
- **Quick Reference**: `ZEP_QUICK_REFERENCE.md`
- **Troubleshooting**: See setup guides for common issues and solutions

## Acknowledgments 💡

- **[SmolAgents](https://github.com/huggingface/smolagents)** for providing the agent framework
- **[Crawl4AI](https://github.com/unclecode/crawl4ai)** for advanced web scraping capabilities
- **[LiteLLM](https://github.com/BerriAI/litellm)** for unified LLM API access
- **[Neo4j](https://neo4j.com/)** for temporal knowledge graph capabilities
- **[Jina AI](https://jina.ai/)** and **[Infinity Embeddings](https://github.com/michaelfeil/infinity)** for semantic reranking
- **[Zep Cloud](https://www.getzep.com/)** for advanced temporal knowledge graph evaluation capabilities

## Citation

```bibtex
@article{opendeepsearch2024,
  title={OpenDeepSearch: Democratizing Search with Open-source Reasoning Models and Reasoning Agents},
  author={SentientAGI Team},
  journal={arXiv preprint arXiv:2503.20201},
  year={2024}
}
```

## Contact 📩

- **Discord**: [SentientAGI Community](https://discord.gg/sentientfoundation)
- **Twitter**: [@SentientAGI](https://x.com/SentientAGI)
- **Homepage**: [sentient.xyz](https://sentient.xyz/)
- **GitHub**: [sentient-agi](https://github.com/sentient-agi)
