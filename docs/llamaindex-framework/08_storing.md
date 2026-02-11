# Storing and Persistence

> Source: [LlamaIndex Documentation — Storing](https://docs.llamaindex.ai/en/stable/understanding/storing/storing/)

## Overview

After building an index, you'll want to persist it to avoid re-processing and re-embedding data every time. Re-embedding is both slow and costly (due to API calls to the embedding model), so persistence is essential for production use. LlamaIndex supports both simple file-based persistence and integration with external vector stores.

## Simple Persistence

Save an index to disk using the built-in persistence mechanism:

```python
# Build index
index = VectorStoreIndex.from_documents(documents)

# Save to disk
index.storage_context.persist(persist_dir="./storage")
```

This creates several JSON files in the specified directory:
- `docstore.json` — Stores the original node content and metadata
- `index_store.json` — Stores index structure and configuration
- `vector_store.json` — Stores embedding vectors
- `graph_store.json` — Stores graph relationships (if applicable)

## Loading from Storage

Reload a persisted index without re-processing or re-embedding:

```python
from llama_index.core import StorageContext, load_index_from_storage

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

This reconstructs the index from the saved files, making it ready for querying immediately.

## Important: Custom Settings When Reloading

If you used custom embed models or transformations when building the index, you must set them again before loading. The settings are not stored in the persisted files:

```python
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding

# Must set same settings used during indexing
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

Failing to do this can cause dimension mismatches or incorrect retrieval results. For example, if you built the index with `text-embedding-3-small` (1536 dimensions) but load it with a different model that produces 768-dimensional vectors, queries will fail or return meaningless results.

## Vector Store Integration: Chroma

For production deployments, external vector stores provide better scalability, persistence, and query performance. Chroma is a popular open-source option:

```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# Create Chroma client with persistence
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_collection")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Build index with Chroma backend
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)
```

Loading from an existing Chroma store (no re-embedding needed):

```python
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_collection")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(vector_store)
```

When using an external vector store, embeddings are stored in the vector store itself rather than in `vector_store.json`. The docstore and index store can still be persisted separately if needed.

## Inserting into Existing Indices

Add new documents to an existing index without rebuilding from scratch:

```python
# Load existing index
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

# Insert new documents
new_documents = SimpleDirectoryReader("./new_data").load_data()
for doc in new_documents:
    index.insert(doc)

# Persist updated index
index.storage_context.persist(persist_dir="./storage")
```

Each inserted document is automatically split into nodes, embedded, and added to the index. This is useful for incrementally growing your knowledge base as new data becomes available.

## Other Vector Store Integrations

LlamaIndex supports 40+ vector stores including:

- **Pinecone** — Fully managed, serverless vector database
- **Weaviate** — Open-source vector search engine with built-in ML models
- **Qdrant** — High-performance vector similarity search engine
- **Milvus** — Scalable open-source vector database for AI applications
- **FAISS** — Facebook's library for efficient similarity search (in-memory)
- **PGVector** — PostgreSQL extension for vector similarity search

Each follows a similar pattern: create a vector store object, wrap it in a `StorageContext`, and pass it to the index constructor. The choice of vector store depends on your deployment requirements around scalability, managed vs. self-hosted, and existing infrastructure.

## Relevance to This Project

The `src/rag/embeddings/` module handles embedding persistence. The project uses batch embedding generation and stores results for reuse across retrieval strategies. Storage configuration is managed through the platform config layer in `src/platform/config/`.
