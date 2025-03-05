from smolagents import Tool
from opendeepsearch.ods_agent import OpenDeepSearchAgent

class OpenDeepSearchTool(Tool):
    name = "OpenDeepSearch"
    description = """
    This is a tool that answers user questions, using a web-search, on any topic."""
    inputs = {
        "question": {
            "type": "string",
            "description": "the user question to answer",
        },
        "max_sources": {
            "type": "integer",
            "nullable": True,
            "description": "the maximum number of sources to retrieve from the web",
        },
        "pro_mode": {
            "type": "boolean",
            "nullable": True,
            "description": "whether to use in-depth search mode",
        }
    }
    output_type = "string"

    def __init__(self, model_name: str):
        super().__init__()
        self.search_model_name = model_name #LiteLLM model name

    def forward(self, question: str, max_sources: int = 2, pro_mode: bool = False):
        answer = self.search_tool.ask_sync(question, max_sources, pro_mode)
        return answer

    def setup(self):
        self.search_tool = OpenDeepSearchAgent(self.search_model_name)