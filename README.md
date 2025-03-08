# OpenDeepSearch 🚀🔍

OpenDeepSearch is a lightweight yet powerful search tool designed for seamless integration with AI agents. It enables deep web search and retrieval, optimized for use with Hugging Face's **[SmolAgents](https://github.com/huggingface/smolagents)** ecosystem.

## Features ✨

- **Semantic Search** 🧠: Leverages **[Infinity Embeddings API](https://github.com/michaelfeil/infinity)** for high-quality search results.
- **Two Modes of Operation** ⚡:
  - **Default Mode**: Quick and efficient search with minimal latency.
  - **Pro Mode (Deep Search)**: More in-depth and accurate results at the cost of additional processing time.
- **Optimized for AI Agents** 🤖: Works seamlessly with **SmolAgents** like `CodeAgent`.
- **Fast and Lightweight** ⚡: Designed for speed and efficiency with minimal setup.
- **Extensible** 🔌: Easily configurable to work with different models and APIs.

## Installation 📚

To install OpenDeepSearch, run:

```bash
pip install opendeepsearch
```

## Setup

1. **Sign up for Serper.dev**: Get **free 2500 credits** and add your API key.
   - Visit [serper.dev](https://serper.dev) to create an account.
   - Retrieve your API key and store it as an environment variable:
   
   ```bash
   export SERPER_API_KEY='your-api-key-here'
   ```

2. **Set up Infinity Embeddings server or implement a base reranker**:
   - Run the **[Infinity Embeddings](https://github.com/michaelfeil/infinity)** server for enhanced search capabilities.
   - Alternatively, integrate a **base_reranker** for custom ranking of search results.

## Usage 🏠️

You can use OpenDeepSearch independently or integrate it with **SmolAgents** for enhanced reasoning and code generation capabilities.

### Using OpenDeepSearch Standalone 🔍

```python
from opendeepsearch import OpenDeepSearchTool
import os

search_agent = OpenDeepSearchTool(model_name="openrouter/google/gemini-2.0-flash-001", pro_mode=True)  # Set pro_mode for deep search
query = "Fastest land animal?"
result = search_agent.search(query)
print(result)
```

### Integrating with SmolAgents & LiteLLM 🤖⚙️

```python
from opendeepsearch import OpenDeepSearchTool
from smolagents import CodeAgent, LiteLLMModel
import os

search_agent = OpenDeepSearchTool(model_name="openrouter/google/gemini-2.0-flash-001", pro_mode=True)
model = LiteLLMModel(
    "openrouter/google/gemini-2.0-flash-001",
    temperature=0.2,
    api_key=os.environ["OPENROUTER_API_KEY"]
)

code_agent = CodeAgent(tools=[search_agent], model=model)
query = "How long would a cheetah at full speed take to run the length of Pont Alexandre III?"
result = code_agent.run(query)

print(result)
```

## LiteLLM Setup & Usage 🔥

**[LiteLLM](https://www.litellm.ai/)** is a lightweight and efficient wrapper that enables seamless integration with multiple LLM APIs. OpenDeepSearch leverages LiteLLM, meaning you can use **any LLM from any provider** that LiteLLM supports. This includes OpenAI, Anthropic, Cohere, and others. **OpenRouter** is a great example of a provider that gives access to multiple models through a single API.

### Using LiteLLM with OpenDeepSearch

You need to set up your API key in your environment variables before using LiteLLM:

```bash
export OPENROUTER_API_KEY='your-api-key-here'
```

Then, you can use it as shown in the SmolAgents integration example above.

## Acknowledgments 💡

OpenDeepSearch is built on the shoulders of great open-source projects:

- **[Crawl4AI](https://github.com/crawl4ai)** 🕷️ – Provides data crawling support.
- **[Infinity Embedding API](https://github.com/michaelfeil/infinity)** 🌍 – Powers semantic search capabilities.
- **[LiteLLM](https://www.litellm.ai/)** 🔥 – Used for efficient AI model integration.
- **Various Open-Source Libraries** 📚 – Enhancing search and retrieval functionalities.

## License 📝

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing 🤝

We welcome contributions! If you'd like to improve OpenDeepSearch, please:

1. Fork the repository.
2. Create a new branch (`feature-xyz`).
3. Submit a pull request.

For major changes, open an issue to discuss your ideas first.

## Contact 📩

For questions or collaborations, open an issue or reach out to the maintainers.

