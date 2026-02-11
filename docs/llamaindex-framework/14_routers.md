# Routers

> Source: [LlamaIndex Documentation — Routers](https://developers.llamaindex.ai)

## Overview

Routers direct incoming queries to the most appropriate query engine or retriever. They are essential when you have multiple data sources, index types, or retrieval strategies and need to dynamically select the best one for each query. Routers use either LLM-based reasoning or structured (Pydantic) classification to make routing decisions.

```
Query → [Router] → Selected Query Engine / Retriever → Response
```

A router consists of two parts:
1. **Selector** — the decision-making component that chooses which tool to use
2. **Tools** — the query engines or retrievers wrapped with descriptive metadata

---

## Selectors

Selectors are the decision-making component of a router. They analyze the query and choose the most appropriate tool based on tool descriptions.

### LLM Selectors

Use natural language reasoning to select the best tool:

```python
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector

# Select one best option
selector = LLMSingleSelector.from_defaults()

# Select multiple relevant options
selector = LLMMultiSelector.from_defaults()
```

LLM selectors work with any LLM and provide flexible, natural language reasoning about which tool to use.

### Pydantic Selectors

Use structured output for more reliable routing (requires OpenAI function calling):

```python
from llama_index.core.selectors import PydanticSingleSelector, PydanticMultiSelector

# Structured single selection
selector = PydanticSingleSelector.from_defaults()

# Structured multi selection
selector = PydanticMultiSelector.from_defaults()
```

Pydantic selectors are more reliable for deterministic routing because they use structured function calling rather than free-form text parsing.

---

## RouterQueryEngine

Route queries to different query engines based on the query content:

```python
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import PydanticSingleSelector

# Define tools with descriptions
tool1 = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description="Useful for answering specific factual questions about the documents.",
)

tool2 = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description="Useful for summarizing the content of the documents.",
)

# Create router
router_query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[tool1, tool2],
)

# Use it
response = router_query_engine.query("Summarize the main themes.")
```

The router examines the query, reads the tool descriptions, and selects the most appropriate query engine before executing the query.

---

## RouterRetriever

Route at the retriever level for finer-grained control over which retrieval strategy to use:

```python
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.tools import RetrieverTool

tool1 = RetrieverTool.from_defaults(
    retriever=vector_retriever,
    description="Retrieves specific passages using semantic similarity.",
)

tool2 = RetrieverTool.from_defaults(
    retriever=keyword_retriever,
    description="Retrieves passages matching specific keywords.",
)

router_retriever = RouterRetriever(
    selector=PydanticSingleSelector.from_defaults(),
    retriever_tools=[tool1, tool2],
)

nodes = router_retriever.retrieve("What is machine learning?")
```

`RouterRetriever` is useful when you want to share the same response synthesizer across all routes but vary the retrieval strategy.

---

## ToolMetadata

Define descriptive metadata for each tool. The description is what the selector uses to make routing decisions:

```python
from llama_index.core.tools import ToolMetadata

metadata = ToolMetadata(
    name="vector_search",
    description="Best for specific factual questions. Uses semantic similarity to find relevant passages.",
)
```

Good descriptions are critical — they are what the LLM or selector uses to make routing decisions. Write descriptions that clearly distinguish each tool's strengths and intended use cases.

**Tips for writing tool descriptions:**
- Be specific about what types of queries the tool handles well
- Mention the retrieval method (semantic, keyword, filtering, etc.)
- Include the type of content the tool is designed for
- Avoid generic descriptions that could apply to multiple tools

---

## Standalone Selector Usage

Selectors can be used independently, outside of a router, for general-purpose classification:

```python
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import ToolMetadata

selector = LLMSingleSelector.from_defaults()

choices = [
    ToolMetadata(description="Handles factual Q&A about documents"),
    ToolMetadata(description="Handles document summarization"),
    ToolMetadata(description="Handles comparative analysis"),
]

result = selector.select(choices, query="Summarize the key findings")
print(f"Selected index: {result.selections[0].index}")
print(f"Reason: {result.selections[0].reason}")
```

This is useful for building custom routing logic, query classification systems, or intent detection pipelines.

---

## Multi-Selection

When a query spans multiple domains or requires answers from multiple sources, use a multi-selector to route to several targets simultaneously:

```python
from llama_index.core.selectors import LLMMultiSelector

selector = LLMMultiSelector.from_defaults()

result = selector.select(choices, query="Compare and summarize all findings")
for selection in result.selections:
    print(f"Selected: {selection.index}, Reason: {selection.reason}")
```

Multi-selection is useful for complex queries that benefit from combining results from different retrieval strategies or data sources.

---

## Relevance to This Project

The planner retrieval strategy (`src/rag/retrieval/retrievers/planner.py`) implements query routing concepts, directing complex queries through multi-step planning. The project's 7 retrieval strategies could be composed behind a router to automatically select the best strategy based on query type — vector for factual questions, summary for overviews, metadata for filtered queries, etc.
