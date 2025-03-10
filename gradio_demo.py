from smolagents import CodeAgent, GradioUI, LiteLLMModel
from opendeepsearch import OpenDeepSearchTool
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Add command line argument parsing
parser = argparse.ArgumentParser(description='Run the Gradio demo with custom models')
parser.add_argument('--model-name', 
                   default="openrouter/google/gemini-2.0-flash-001",
                   help='Model name for search')
parser.add_argument('--orchestrator-model', 
                   default="openrouter/google/gemini-2.0-flash-001",
                   help='Model name for orchestration')
parser.add_argument('--reranker',
                   choices=['jina', 'infinity'],
                   default='jina',
                   help='Reranker to use (jina or infinity)')

args = parser.parse_args()

# Use the command line arguments
search_tool = OpenDeepSearchTool(model_name=args.model_name, reranker=args.reranker)
model = LiteLLMModel(
    model_id=args.orchestrator_model,
    temperature=0.2,
)

# Initialize the agent with the search tool
agent = CodeAgent(tools=[search_tool], model=model)

# Add a name when initializing GradioUI
GradioUI(agent).launch()