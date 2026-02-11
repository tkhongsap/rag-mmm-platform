# LlamaIndex Framework Documentation

Foundational reference for LlamaIndex RAG framework concepts, APIs, and patterns used in this project.

This documentation complements `references/rag-llamaindex/`, which covers optimization strategies and benchmarks, while this series covers core framework concepts, abstractions, and code patterns.

## Document Index

| File | Topic | Description |
|------|-------|-------------|
| [01_overview.md](01_overview.md) | RAG Overview | RAG concept and the 5-stage pipeline model |
| [02_installation.md](02_installation.md) | Installation | Package installation, namespaced packages, environment setup |
| [03_starter_tutorial.md](03_starter_tutorial.md) | Starter Tutorial | End-to-end working example with agent and RAG |
| [04_documents_and_nodes.md](04_documents_and_nodes.md) | Documents & Nodes | Core data abstractions -- Document, Node, metadata |
| [05_data_connectors.md](05_data_connectors.md) | Data Connectors | SimpleDirectoryReader, LlamaHub, third-party readers |
| [06_loading_and_ingestion.md](06_loading_and_ingestion.md) | Loading & Ingestion | Transformations, SentenceSplitter, IngestionPipeline |
| [07_indexing.md](07_indexing.md) | Indexing | VectorStoreIndex, SummaryIndex, top-k retrieval |
| [08_storing.md](08_storing.md) | Storing | Persistence, StorageContext, vector stores |
| [09_querying.md](09_querying.md) | Querying | 3-stage query architecture and customization API |
| [10_embeddings.md](10_embeddings.md) | Embeddings | Model configuration, OpenAI/HuggingFace/ONNX, batch size |
| [11_retrievers.md](11_retrievers.md) | Retrievers | Retriever types, modes, low-level composition |
| [12_node_postprocessors.md](12_node_postprocessors.md) | Node Postprocessors | Filtering, reranking, custom postprocessors |
| [13_response_synthesizers.md](13_response_synthesizers.md) | Response Synthesizers | 8 response modes (refine, compact, tree_summarize...) |
| [14_routers.md](14_routers.md) | Routers | LLM/Pydantic selectors, RouterQueryEngine |

## Document Organization

The 14 documents are organized into four logical groups:

### Foundation (01-03)

Core concepts, setup, and a hands-on starter tutorial. Start here if you are new to LlamaIndex or RAG.

### Data Layer (04-06)

How data enters the system -- from raw files to structured, chunked documents ready for indexing. Covers the Document and Node abstractions, data connectors for loading from various sources, and the ingestion pipeline that transforms raw data into processable units.

### Pipeline Core (07-09)

The backbone of the RAG pipeline -- building searchable indices, persisting them for reuse, and executing queries against them. These three stages form the core workflow that connects data loading to answer generation.

### Query Components (10-14)

The building blocks that power the query stage -- embeddings for similarity search, retrievers for fetching relevant content, postprocessors for filtering and reranking, response synthesizers for generating answers, and routers for directing queries to the right sub-pipeline.

## Cross-Reference: Documentation to Project Modules

| Documentation | Project Module | Connection |
|---|---|---|
| 04-06 (Data Layer) | `src/rag/data_processing/` | Document loading and chunking |
| 07 (Indexing) | `src/rag/retrieval/` | Index construction |
| 08 (Storing) | `src/rag/embeddings/` | Embedding persistence |
| 10 (Embeddings) | `src/rag/embeddings/` | Embedding model configuration |
| 11 (Retrievers) | `src/rag/retrieval/retrievers/` | 7 retrieval strategy implementations |
| 12 (Postprocessors) | `src/rag/retrieval/` | Result filtering and reranking |
| 13 (Synthesizers) | `src/rag/retrieval/` | Response generation |
| 14 (Routers) | `src/rag/retrieval/retrievers/planner.py` | Query routing |

## Comparison with `references/`

| | `docs/llamaindex-framework/` | `references/rag-llamaindex/` |
|---|---|---|
| Purpose | Core framework concepts & APIs | Optimization strategies & benchmarks |
| Content | Abstractions, tutorials, code patterns | Performance numbers, model comparisons |
| Use when | Learning LlamaIndex or looking up APIs | Tuning an existing implementation |

## Source Attribution

Content derived from the official LlamaIndex documentation at [developers.llamaindex.ai](https://developers.llamaindex.ai).
