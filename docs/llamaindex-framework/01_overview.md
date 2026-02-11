# RAG Overview

> Source: [developers.llamaindex.ai](https://developers.llamaindex.ai) -- LlamaIndex official documentation.

## What Is RAG?

Retrieval-Augmented Generation (RAG) is a technique that augments Large Language Models (LLMs) with private or domain-specific data. Rather than relying solely on the knowledge baked into model weights during pre-training, RAG retrieves relevant information from an external knowledge base and feeds it to the LLM as additional context when generating a response.

RAG operates in two key stages:

1. **Indexing stage** -- Prepare a knowledge base by ingesting data from various sources, splitting it into manageable chunks, generating vector embeddings, and storing everything in a searchable index.
2. **Querying stage** -- Given a user query, retrieve the most relevant context from the index and pass it to the LLM alongside the query to generate a grounded, accurate answer.

### Why RAG?

- **Private data access**: LLMs are trained on publicly available data. Organizations need to augment them with proprietary documents, internal databases, and domain-specific knowledge that was never part of the training set.
- **Context window limits**: Even though context windows are growing, they cannot hold an entire knowledge base. RAG selectively retrieves only the most relevant pieces of information for each query.
- **Cost-effectiveness**: RAG is significantly more cost-effective than fine-tuning a model on private data. Fine-tuning requires retraining (expensive, slow, and must be repeated when data changes), while RAG works with any base model and updates instantly when the knowledge base changes.

## The 5 Stages of RAG

LlamaIndex structures the RAG workflow into five distinct stages:

### 1. Loading

Getting data from its source -- PDFs, Word documents, APIs, databases, web pages, Slack, Notion -- into the pipeline. LlamaIndex provides **data connectors** (also called Readers) that load raw data and convert it into `Document` objects. The `SimpleDirectoryReader` handles common file formats out of the box, while LlamaHub offers hundreds of connectors for third-party data sources.

### 2. Indexing

Creating a searchable data structure from the loaded documents. This typically involves:

- **Parsing and chunking**: Splitting documents into smaller, semantically meaningful pieces called `Nodes`.
- **Embedding**: Converting each chunk into a numerical vector representation that captures its semantic meaning.
- **Index construction**: Organizing embeddings into a data structure optimized for fast retrieval, usually backed by a vector store.

The most common index type is `VectorStoreIndex`, which stores embeddings and enables similarity-based retrieval.

### 3. Storing

Persisting the indexed data so you do not have to re-ingest and re-embed every time you run the pipeline. LlamaIndex supports persisting indices to disk or to external vector stores (Chroma, Pinecone, Weaviate, Qdrant, and many others). Once stored, an index can be loaded directly without reprocessing the source data.

### 4. Querying

Utilizing LLMs and LlamaIndex data structures to answer questions. The querying stage involves multiple sub-components working together:

- **Retrievers** fetch the most relevant nodes from the index given a query.
- **Node postprocessors** optionally filter, rerank, or transform the retrieved nodes.
- **Response synthesizers** take the retrieved context and the original query, then prompt the LLM to generate a final answer.

Query strategies range from simple semantic search (embed the query, find nearest neighbors) to complex multi-step approaches involving query decomposition, routing across multiple indices, and iterative refinement.

### 5. Evaluation

Measuring how well the pipeline performs. Key evaluation dimensions include:

- **Accuracy**: Are the retrieved documents relevant to the query?
- **Faithfulness**: Is the generated response grounded in the retrieved context (not hallucinated)?
- **Speed**: How fast is end-to-end query latency?
- **Cost**: How many LLM tokens and API calls does a query consume?

LlamaIndex provides evaluation modules that assess retrieval quality and response faithfulness, enabling systematic pipeline optimization.

## Key Concepts and Terminology

| Concept | Description |
|---------|-------------|
| **Documents** | Core data containers that hold raw data from a source (a PDF, a web page, a database row). Each Document has text content and metadata. |
| **Nodes** | Chunks derived from Documents. A Node is the atomic unit of data in LlamaIndex -- it carries text, metadata, and relationships to other Nodes (parent, child, sibling). |
| **Connectors (Readers)** | Components that load data from various sources and convert them into Documents. Examples: `SimpleDirectoryReader`, database readers, API readers. |
| **Indices** | Data structures built from Nodes for efficient retrieval. `VectorStoreIndex` is the most common; `SummaryIndex` stores all nodes sequentially for summarization tasks. |
| **Embeddings** | Numerical vector representations of text. Similar texts produce vectors that are close together in vector space, enabling semantic similarity search. |
| **Retrievers** | Components that fetch relevant Nodes from an Index given a query. Different retriever types implement different search strategies (vector similarity, keyword matching, metadata filtering). |
| **Routers** | Components that direct a query to the most appropriate sub-pipeline or index. Useful when you have multiple indices or retrieval strategies and need to select the right one per query. |
| **Node Postprocessors** | Components that transform, filter, or rerank Nodes after retrieval but before response synthesis. Examples: similarity score thresholding, metadata filtering, reranking with a cross-encoder. |
| **Response Synthesizers** | Components that take retrieved Nodes and the original query, then generate a natural language answer using an LLM. Multiple modes are available: refine, compact, tree_summarize, and others. |

## Relevance to This Project

Our RAG pipeline in `src/rag/` implements all 5 stages of the RAG workflow:

- **Loading** -- `src/rag/data_processing/` handles document loading and chunking from CSV and other file formats.
- **Indexing** -- `src/rag/embeddings/` generates vector embeddings using OpenAI's `text-embedding-3-small` model.
- **Storing** -- Embedding persistence is managed through the embeddings module and local storage.
- **Querying** -- `src/rag/retrieval/` implements 7 retrieval strategies (vector, summary, recursive, metadata, chunk decoupling, hybrid, planner) with response synthesis.

See the project's `references/rag-llamaindex/` for optimization benchmarks and performance tuning guidance.
