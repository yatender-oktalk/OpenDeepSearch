from smolagents import Tool
from opendeepsearch import OpenDeepSearch

class OpenDeepSearchTool(Tool):
    name = "OpenDeepSearch"
    description = """
    This is a tool that answers user questions, using a web-search, on any topic."""
    inputs = {
        "question": {
            "type": "string",
            "description": "the user question to answer",
        }
    }
    output_type = "string"

    def forward(self, task: str):
        from huggingface_hub import list_models

        model = next(iter(list_models(filter=task, sort="downloads", direction=-1)))
        return model.id

    def setup(self):
        self.search_tool = OpenDeepSearch()