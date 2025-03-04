# OpenDeepSearch

## Core Components

### 1. Web Scraping
The WebScraper class supports multiple extraction strategies:
- LLM-based extraction
- CSS selectors
- XPath queries
- No-extraction (raw content)
- Cosine similarity-based extraction

Reference: 

### 2. Content Processing
Includes advanced content processing features:
- Chunk-based text splitting
- Quality content filtering
- Educational value assessment
- Smart paragraph processing

Reference:

### 3. Semantic Search
Implements semantic search capabilities:
- Document reranking
- Query-document similarity scoring
- Customizable normalization methods

Reference:

## Environment Variables

Required environment variables:
- `SERPER_API_KEY`: For web search functionality
- `OPENROUTER_API_KEY`: For LLM-based extraction

## Dependencies

Key dependencies include:

Full dependencies list can be found in the pyproject.toml file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Crawl4AI](https://github.com/crawl4ai)
- Uses [Infinity Embedding API](https://infinity.ai) for semantic search
- Powered by various open-source libraries and tools
