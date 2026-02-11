# Querying

> Source: [developers.llamaindex.ai](https://developers.llamaindex.ai)

## Overview

Querying is the most critical part of any RAG pipeline. After your data has been ingested, indexed, and stored, querying is how you retrieve relevant context and generate answers from it.

In LlamaIndex, the query stage has 3 sub-stages:

1. **Retrieval**: Find and return the most relevant nodes from the index based on the query. The retriever takes a query string and returns a list of `NodeWithScore` objects.
2. **Postprocessing**: Apply transformations, filtering, or reranking to the retrieved nodes. This can include filtering by similarity score, required keywords, or adding adjacent nodes for more context.
3. **Response Synthesis**: Generate a natural language answer by combining the original query with the retrieved context. The synthesizer sends the query plus relevant chunks to the LLM and produces a final response.

## Basic Query Engine

The simplest way to query an index is through the high-level `as_query_engine()` API:

```python
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic?")
print(response)
```

You can customize the query engine with common parameters:

```python
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact",
    streaming=True,
)
```

- `similarity_top_k`: Number of top similar nodes to retrieve.
- `response_mode`: How the response is synthesized from the retrieved chunks.
- `streaming`: Whether to stream the response token by token.

## Low-Level Composition

For full control, build a custom query pipeline from individual components:

```python
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine

# Step 1: Configure retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)

# Step 2: Configure postprocessor
postprocessor = SimilarityPostprocessor(similarity_cutoff=0.7)

# Step 3: Configure response synthesizer
response_synthesizer = get_response_synthesizer(response_mode="compact")

# Step 4: Assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[postprocessor],
    response_synthesizer=response_synthesizer,
)

response = query_engine.query("What is the main topic?")
```

This approach lets you swap out any component independently. You can use a different retriever, add multiple postprocessors, or change how the response is synthesized without affecting the rest of the pipeline.

## Node Postprocessors in Queries

Postprocessors transform or filter the list of retrieved nodes before they are passed to the response synthesizer. Common postprocessors include:

```python
from llama_index.core.postprocessor import (
    SimilarityPostprocessor,
    KeywordNodePostprocessor,
    PrevNextNodePostprocessor,
)

# Filter by similarity score
similarity_pp = SimilarityPostprocessor(similarity_cutoff=0.7)

# Filter by required/excluded keywords
keyword_pp = KeywordNodePostprocessor(
    required_keywords=["machine learning"],
    exclude_keywords=["outdated"],
)

# Include adjacent nodes for more context
prev_next_pp = PrevNextNodePostprocessor(
    docstore=index.docstore,
    num_nodes=1,
    mode="both",  # "previous", "next", or "both"
)
```

Multiple postprocessors can be chained together and are applied in order:

```python
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[similarity_pp, keyword_pp],
    response_synthesizer=response_synthesizer,
)
```

## Response Modes

The response mode determines how retrieved context is combined and sent to the LLM. A brief overview (see `13_response_synthesizers.md` for details):

| Mode | Description |
|------|-------------|
| `refine` | Sequentially refine the answer through each retrieved chunk |
| `compact` (default) | Compact chunks to fit more context per LLM call, then refine |
| `tree_summarize` | Build a summary tree bottom-up from chunks |
| `simple_summarize` | Truncate all chunks to fit in one LLM call and summarize |
| `no_text` | Return retrieved nodes without LLM synthesis |
| `accumulate` | Generate a separate response per chunk, then combine |

## Structured Outputs

You can get structured data from query engines using Pydantic models:

```python
from pydantic import BaseModel

class Response(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

query_engine = index.as_query_engine(
    response_mode="compact",
    output_cls=Response,
)
```

The LLM output will be parsed into the specified Pydantic model, giving you typed access to structured fields rather than raw text.

## Chat Engine

For conversational interactions that maintain context across multiple turns, use the chat engine:

```python
chat_engine = index.as_chat_engine()
response = chat_engine.chat("What is the main topic?")
follow_up = chat_engine.chat("Tell me more about that.")
```

The chat engine automatically manages conversation history, allowing follow-up questions that reference prior context. It combines retrieval with conversational memory so the LLM can understand references like "that" or "it" from previous turns.

## Relevance to This Project

The `src/rag/retrieval/` module implements the full query pipeline with 7 retrieval strategies. Each strategy in `src/rag/retrieval/retrievers/` configures different combinations of retrievers, postprocessors, and synthesizers. The `src/rag/retrieval/cli` provides an interactive query interface.
