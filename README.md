# OpenDeepSearch 🚀🔍

OpenDeepSearch is a lightweight yet powerful search tool designed for seamless integration with AI agents. It enables deep web search and retrieval, optimized for use with Hugging Face's **[SmolAgents](https://github.com/huggingface/smolagents)** ecosystem.

## Table of Contents 📑

- [OpenDeepSearch 🚀🔍](#opendeepsearch-)
  - [Table of Contents 📑](#table-of-contents-)
  - [Features ✨](#features-)
  - [Installation 📚](#installation-)
  - [Setup](#setup)
  - [Usage ️](#usage-️)
    - [Using OpenDeepSearch Standalone 🔍](#using-opendeepsearch-standalone-)
    - [Integrating with SmolAgents \& LiteLLM 🤖⚙️](#integrating-with-smolagents--litellm-️)
  - [Search Modes 🔄](#search-modes-)
    - [Default Mode ⚡](#default-mode-)
    - [Pro Mode 🔍](#pro-mode-)
  - [Acknowledgments 💡](#acknowledgments-)
  - [License 📝](#license-)
  - [Contributing 🤝](#contributing-)
  - [Contact 📩](#contact-)

## Features ✨

- **Semantic Search** 🧠: Leverages **[Crawl4AI](https://github.com/crawl4ai)** and semantic search rerankers (such as [Qwen2-7B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct/tree/main) and [Jina AI](https://jina.ai/)) to provide in-depth results
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
   - When initializing OpenDeepSearch, specify your chosen model using the provider's format:
   ```python
   search_agent = OpenDeepSearchTool(model_name="provider/model-name")  # e.g., "anthropic/claude-3-opus-20240229", 'huggingface/microsoft/codebert-base', 'openrouter/google/gemini-2.0-flash-001'
   ```

## Usage ️

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

## Search Modes 🔄

OpenDeepSearch offers two distinct search modes to balance between speed and depth:

### Default Mode ⚡
- Uses SERP-based interaction for quick results
- Minimal processing overhead
- Ideal for single-hop, straightforward queries
- Fast response times
- Perfect for basic information retrieval

### Pro Mode 🔍
- Involves comprehensive web scraping
- Implements semantic reranking of results
- Includes advanced post-processing of data
- Slightly longer processing time
- Excels at:
  - Multi-hop queries
  - Complex search requirements
  - Detailed information gathering
  - Questions requiring cross-reference verification

## Acknowledgments 💡

OpenDeepSearch is built on the shoulders of great open-source projects:

- **[SmolAgents](https://huggingface.co/docs/smolagents/index)** 🤗 – Powers the agent framework and reasoning capabilities.
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

