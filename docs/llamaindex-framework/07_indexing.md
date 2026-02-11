# Indexing

> Source: [LlamaIndex Documentation — Indexing](https://docs.llamaindex.ai/en/stable/understanding/indexing/indexing/)

## What Is an Index?

In LlamaIndex, an Index is a data structure built from Documents that enables fast retrieval. It stores processed nodes along with their embeddings (for vector indices) or summaries (for summary indices). The index is the bridge between your raw data and the query engine.

Different index types organize and access data in different ways, each optimized for specific retrieval patterns. Choosing the right index type is one of the most important decisions in building a RAG pipeline.

## VectorStoreIndex

The most common index type. `VectorStoreIndex` stores embedding vectors for each node and retrieves them using semantic similarity search.

From documents:

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
```

From pre-processed nodes:

```python
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex(nodes)
```

With a progress bar for large datasets:

```python
index = VectorStoreIndex.from_documents(documents, show_progress=True)
```

## How VectorStoreIndex Works

**During index construction:**

1. Documents are split into Nodes using the configured text splitter
2. Each Node's text is converted into an embedding vector via the embedding model
3. Embeddings and node data are stored in the vector store

**At query time:**

1. The query text is converted into an embedding using the same embedding model
2. The vector store finds the top-k most similar node embeddings (using cosine similarity or another distance metric)
3. The corresponding nodes are returned for response synthesis

This two-phase process means that the embedding model used at query time must match the one used during index construction. Mismatched models will produce incompatible embedding spaces and poor retrieval results.

## Top-K Similarity Retrieval

Top-k similarity retrieval is the fundamental retrieval mechanism for vector indices. Given a query embedding, the vector store finds the k most similar stored embeddings using cosine similarity (or other distance metrics such as dot product or Euclidean distance).

The default k value is typically 2-10, depending on the use case:

```python
query_engine = index.as_query_engine(similarity_top_k=5)
response = query_engine.query("What is the main topic?")
```

Lower values of k return fewer but more relevant results, while higher values provide more context at the cost of potentially including less relevant nodes. Tuning this parameter is important for balancing precision and recall.

## SummaryIndex

`SummaryIndex` stores all nodes sequentially and uses the LLM to determine relevance at query time. It is well suited for summarization tasks where you need to consider all available content:

```python
from llama_index.core import SummaryIndex

index = SummaryIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Summarize the main themes.")
```

Unlike `VectorStoreIndex`, `SummaryIndex` does not use embeddings. Instead, it iterates through all nodes and uses the LLM to determine which ones are relevant to the query. This makes it more expensive at query time (more LLM calls) but ensures no relevant content is missed due to embedding similarity thresholds.

## Other Index Types

LlamaIndex provides several additional index types for specialized use cases:

- **TreeIndex**: Builds a hierarchical tree of summaries from leaf nodes up to a root summary. Useful for multi-level summarization where you want different granularities of information.

- **KeywordTableIndex**: Extracts keywords from each node and builds a keyword-to-node mapping. Retrieval is based on keyword matching rather than semantic similarity. Fast but less flexible than vector search.

- **KnowledgeGraphIndex**: Builds a knowledge graph from extracted triplets (subject, predicate, object). Useful for structured reasoning over relationships between entities.

Each index type can be used independently or combined through composable indices for more sophisticated retrieval strategies.

## Relevance to This Project

The `src/rag/retrieval/` module builds indices from processed documents. `VectorStoreIndex` is the primary index type used, supporting the vector, hybrid, and chunk decoupling retrieval strategies. `SummaryIndex` powers the summary retrieval strategy. Index construction is separated from embedding generation, which is handled in `src/rag/embeddings/`.
