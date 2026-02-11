# Loading and Ingestion Pipeline

> Source: [LlamaIndex Documentation — Loading and Ingestion](https://docs.llamaindex.ai/en/stable/understanding/loading/loading/)

## Overview

Loading and ingestion is the process of transforming raw data into indexed, searchable nodes. LlamaIndex provides both a high-level one-liner API and a granular pipeline approach for full control. The ingestion process typically involves: loading documents from a source, splitting them into manageable chunks (nodes), optionally enriching them with metadata, generating embeddings, and storing everything in an index.

## High-Level API

The simplest approach loads documents and builds an index in just two lines:

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
```

This automatically:
- Splits documents into nodes using the default text splitter
- Generates embeddings for each node
- Stores nodes and embeddings in the index

This is convenient for getting started, but for production workloads you will typically want more control over each stage.

## Global Settings

Configure default behavior for chunking and other parameters using the `Settings` object:

```python
from llama_index.core import Settings

Settings.chunk_size = 1024
Settings.chunk_overlap = 50
```

You can also set the text splitter directly for finer control:

```python
from llama_index.core.node_parser import SentenceSplitter

Settings.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
```

These global settings apply to all subsequent index-building operations unless overridden at the call site.

## Transformations

Transformations convert raw documents into processed nodes. LlamaIndex provides several built-in text splitters.

### SentenceSplitter

Splits text by sentences, respecting sentence boundaries to produce more coherent chunks:

```python
from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
nodes = splitter.get_nodes_from_documents(documents)
```

`SentenceSplitter` is the recommended default for most use cases because it preserves semantic coherence within each chunk.

### TokenTextSplitter

Splits text by token count, useful when you need precise control over token budgets:

```python
from llama_index.core.node_parser import TokenTextSplitter

splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=20)
nodes = splitter.get_nodes_from_documents(documents)
```

## IngestionPipeline

Chain multiple transformations together using `IngestionPipeline`. Each transformation runs in sequence on the output of the previous one:

```python
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024, chunk_overlap=20),
        OpenAIEmbedding(),
    ]
)

nodes = pipeline.run(documents=documents)
```

The pipeline runs each transformation in sequence on the output of the previous one. In this example, documents are first split into nodes, then each node receives an embedding vector. The resulting nodes are ready to be inserted into an index.

## Adding Metadata

Metadata enriches nodes with structured information that can be used for filtering and context during retrieval.

### Manual Metadata

Set metadata directly on documents before ingestion:

```python
for document in documents:
    document.metadata["category"] = "research"
```

### Metadata Extractors

Use LLM-powered extractors in the pipeline to automatically generate metadata:

```python
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024, chunk_overlap=20),
        TitleExtractor(nodes=5),
        QuestionsAnsweredExtractor(questions=3),
    ]
)

nodes = pipeline.run(documents=documents)
```

`TitleExtractor` infers a title from the first few nodes of each document. `QuestionsAnsweredExtractor` generates questions that each node can answer, which improves retrieval accuracy for question-style queries.

## Direct Node Creation

For full control, you can create nodes manually and build an index from them:

```python
from llama_index.core.schema import TextNode

nodes = [
    TextNode(text="First chunk of text", id_="node-1"),
    TextNode(text="Second chunk of text", id_="node-2"),
]

# Build index directly from nodes
from llama_index.core import VectorStoreIndex
index = VectorStoreIndex(nodes)
```

This approach is useful when you have a custom preprocessing pipeline outside of LlamaIndex or when migrating data from another system.

## Relevance to This Project

The `src/rag/data_processing/` module implements the loading and transformation pipeline. Chunk size (default: 1024) and overlap (default: 50) are configured via `CHUNK_SIZE` and `CHUNK_OVERLAP` environment variables. The `src/rag/embeddings/` module handles the embedding stage of ingestion using batch processing.
