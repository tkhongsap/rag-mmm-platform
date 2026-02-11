# Retrievers

> Source: [developers.llamaindex.ai](https://developers.llamaindex.ai)

## Overview

A Retriever is responsible for fetching the most relevant nodes (context) from an index given a query. Retrievers are the core of the "R" in RAG — they determine what information the LLM sees when generating an answer.

LlamaIndex provides built-in retrievers for each index type and supports custom retriever composition. The choice of retriever strategy has a significant impact on the quality, speed, and flexibility of your RAG pipeline.

## Basic Usage

The simplest way to get a retriever is from an existing index:

```python
# High-level
retriever = index.as_retriever()
nodes = retriever.retrieve("What is the main topic?")

for node in nodes:
    print(f"Score: {node.score:.4f}")
    print(f"Text: {node.text[:200]}")
    print("---")
```

The `retrieve()` method returns a list of `NodeWithScore` objects, each containing the matched node and its relevance score.

## Retriever Modes

Each index type supports different retrieval modes that control how nodes are selected.

**VectorStoreIndex**:

```python
retriever = index.as_retriever(
    retriever_mode="default",  # vector similarity (default)
)
```

**SummaryIndex** supports multiple selection strategies:

```python
# Default: use LLM to pick relevant nodes
retriever = index.as_retriever(retriever_mode="default")

# Embedding-based selection
retriever = index.as_retriever(retriever_mode="embedding")

# LLM-based selection
retriever = index.as_retriever(retriever_mode="llm")
```

The `embedding` mode uses cosine similarity to select nodes, while the `llm` mode asks the language model to judge relevance. The default mode varies by index type.

## VectorIndexRetriever

The most commonly used retriever for semantic similarity search:

```python
from llama_index.core.retrievers import VectorIndexRetriever

retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)

nodes = retriever.retrieve("What is machine learning?")
```

Key parameters:

- `similarity_top_k`: Number of top similar nodes to retrieve. Higher values provide more context but may include less relevant results.
- `filters`: `MetadataFilters` object for pre-filtering nodes by metadata attributes before similarity search.

## SummaryIndexRetriever

Uses the LLM to select relevant nodes from a summary index:

```python
from llama_index.core.retrievers import SummaryIndexLLMRetriever

retriever = SummaryIndexLLMRetriever(
    index=summary_index,
    choice_batch_size=10,
)

nodes = retriever.retrieve("Summarize the key findings.")
```

The `choice_batch_size` parameter controls how many nodes are presented to the LLM at once for selection. This retriever is useful when you need the LLM to make nuanced relevance judgments rather than relying solely on embedding similarity.

## Composing Retrievers

Combine multiple retrievers to leverage different retrieval strategies:

```python
from llama_index.core.retrievers import QueryFusionRetriever

retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, keyword_retriever],
    similarity_top_k=10,
    num_queries=4,  # Generate 4 query variations
    mode="reciprocal_rerank",
)

nodes = retriever.retrieve("What is the main topic?")
```

`QueryFusionRetriever` generates multiple query variations from the original query, runs each through all retrievers, and fuses the results using reciprocal rank fusion or other ranking strategies. This improves recall by capturing different aspects of the query.

## Retrieved Node Structure

Each retrieved node is a `NodeWithScore` object that contains the node and its relevance score:

```python
for node_with_score in nodes:
    print(f"Node ID: {node_with_score.node.node_id}")
    print(f"Score: {node_with_score.score}")
    print(f"Text: {node_with_score.node.text}")
    print(f"Metadata: {node_with_score.node.metadata}")
```

- `node_id`: Unique identifier for the node.
- `score`: Relevance score (higher is more relevant; scale depends on the retriever).
- `text`: The text content of the node.
- `metadata`: Dictionary of metadata attributes attached to the node during ingestion.

## Relevance to This Project

The `src/rag/retrieval/retrievers/` directory implements 7 retrieval strategies, each wrapping or composing LlamaIndex retrievers:

- `vector.py`: VectorIndexRetriever for semantic similarity search.
- `summary.py`: SummaryIndex-based retrieval for document-level understanding.
- `recursive.py`: Hierarchical multi-level retrieval for structured documents.
- `metadata.py`: Metadata filtering for fast attribute-based queries.
- `chunk_decoupling.py`: Separates embedding vectors from content storage for flexibility.
- `hybrid.py`: Combines vector similarity with BM25 keyword search using fusion.
- `planner.py`: Multi-step query planning agent for complex questions.
