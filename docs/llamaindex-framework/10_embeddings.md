# Embeddings

> Source: [developers.llamaindex.ai](https://developers.llamaindex.ai)

## Overview

Embeddings are numerical vector representations of text that capture semantic meaning. Similar concepts produce vectors that are close together in the embedding space, enabling similarity-based search.

In LlamaIndex, embeddings are used to:

1. **Convert document chunks into vectors** for storage in a vector index during ingestion.
2. **Convert queries into vectors** for similarity search during retrieval.

The quality of your embeddings directly impacts retrieval quality. Better embeddings produce more accurate similarity matches, which means the LLM receives more relevant context and generates better answers.

## Default Configuration

LlamaIndex defaults to OpenAI's `text-embedding-ada-002`. You can set the embedding model globally using the `Settings` object:

```python
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
```

Or with the larger, higher-quality model:

```python
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")
```

The `text-embedding-3-small` model offers a good balance between quality and cost. The `text-embedding-3-large` model provides higher quality embeddings at increased cost and dimensionality.

## Batch Size

Control the embedding batch size to manage API rate limits and throughput:

```python
embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
    embed_batch_size=10,  # default is 10
)
```

- **Reduce batch size** if you are hitting API rate limits.
- **Increase batch size** for higher throughput when rate limits allow.

## HuggingFace Embeddings

For local embedding models that do not require API calls, use HuggingFace models:

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
```

Install the integration package:

```bash
pip install llama-index-embeddings-huggingface
```

Local models run entirely on your machine, avoiding API costs and latency. They are useful for development, testing, or environments where data cannot be sent to external APIs.

## ONNX / OpenVINO Backends

For faster local inference, use optimized backends:

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    backend="onnx",  # or "openvino"
)
```

The ONNX backend can provide up to ~7x speedup over default PyTorch inference, making local models more practical for production workloads.

## Per-Index Overrides

You can use different embedding models for different indices by passing the model directly:

```python
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(model="text-embedding-3-large"),
)
```

This overrides the global `Settings.embed_model` for that specific index. This is useful when different document collections benefit from different embedding models.

## Standalone Usage

Embeddings can be used directly outside of the index/retrieval pipeline:

```python
embed_model = OpenAIEmbedding()

# Single text
embedding = embed_model.get_text_embedding("Hello world")

# Batch
embeddings = embed_model.get_text_embedding_batch(
    ["Hello world", "How are you?"]
)

# Query embedding (may be different from text embedding for some models)
query_embedding = embed_model.get_query_embedding("What is the meaning?")
```

Some embedding models use different encoding for documents versus queries. The `get_query_embedding` method ensures the correct encoding is used for query-time similarity search.

## Integration Ecosystem

LlamaIndex supports 40+ embedding providers through integration packages:

| Provider | Package | Model Example |
|----------|---------|---------------|
| OpenAI | `llama-index-embeddings-openai` | text-embedding-3-small |
| HuggingFace | `llama-index-embeddings-huggingface` | BAAI/bge-small-en-v1.5 |
| Cohere | `llama-index-embeddings-cohere` | embed-english-v3.0 |
| Google | `llama-index-embeddings-gemini` | models/embedding-001 |
| Mistral | `llama-index-embeddings-mistralai` | mistral-embed |
| Voyage | `llama-index-embeddings-voyageai` | voyage-2 |
| Ollama | `llama-index-embeddings-ollama` | nomic-embed-text |

Each provider requires installing the corresponding integration package (e.g., `pip install llama-index-embeddings-cohere`).

## Relevance to This Project

The `src/rag/embeddings/` module handles all embedding operations. The project uses OpenAI's `text-embedding-3-small` model (configured via the `EMBED_MODEL` environment variable) with batch processing (`BATCH_SIZE=10`, `MAX_WORKERS=4`). Embedding generation is a separate pipeline stage from retrieval, allowing pre-computation and storage of embeddings before any queries are run.
