# Documents and Nodes

> Reference: [developers.llamaindex.ai](https://developers.llamaindex.ai) — Documents and Nodes

Documents and Nodes are the core data abstractions in LlamaIndex. Understanding how they work is essential for controlling how data flows through the indexing and retrieval pipeline.

---

## Overview

- A **Document** is a generic container for any data source -- a PDF, an API response, a database row, or any text content.
- A **Node** represents a "chunk" of a source Document. Nodes carry metadata, track relationships to other nodes, and are the atomic unit used for indexing and retrieval.

Documents are the input to the pipeline. Nodes are what the index actually stores and searches over.

---

## The Document Class

A Document is a subclass of Node. It includes:

- `text`: The content string
- `metadata`: A dictionary of key-value pairs (filterable during retrieval)
- `id_`: A unique identifier

### Creating documents manually

```python
from llama_index.core import Document

doc = Document(text="This is the document text.")
```

### Creating from data sources

```python
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
```

Each file produces one or more Document objects depending on the reader and file format.

---

## Metadata

Every Document (and Node) has a `metadata` dictionary for storing arbitrary key-value pairs:

```python
document = Document(
    text="This is the document text.",
    metadata={
        "filename": "example.pdf",
        "category": "research",
        "author": "John Doe",
    },
)
```

Metadata is inherited by Nodes when a Document is parsed into chunks. You can control what metadata is visible to the LLM versus the embedding model:

```python
document.excluded_llm_metadata_keys = ["internal_id"]
document.excluded_embed_metadata_keys = ["internal_id"]
```

- Keys in `excluded_llm_metadata_keys` are hidden from the LLM during response synthesis.
- Keys in `excluded_embed_metadata_keys` are excluded when generating embeddings.

This is useful for keeping internal tracking fields out of the semantic search and generation steps while still using them for metadata filtering.

---

## The Node Class (TextNode)

Nodes are chunks of documents. The primary node type is `TextNode`:

```python
from llama_index.core.schema import TextNode

node = TextNode(text="This is a chunk of text.", id_="node-1")
```

Nodes inherit all metadata from their source Document and maintain a relationship back to it.

---

## Node Relationships

Nodes track relationships to other nodes, enabling traversal and context expansion during retrieval:

```python
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo

node1 = TextNode(text="First chunk", id_="node-1")
node2 = TextNode(text="Second chunk", id_="node-2")

# Set relationships
node1.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
    node_id=node2.node_id
)
node2.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
    node_id=node1.node_id
)
```

### Relationship types

| Type | Description |
|------|-------------|
| `SOURCE` | The parent Document this node was derived from |
| `PREVIOUS` | The preceding node in sequence |
| `NEXT` | The following node in sequence |
| `PARENT` | A parent node in a hierarchical structure |
| `CHILD` | A child node in a hierarchical structure |

These relationships are used by retrieval strategies like recursive retrieval to navigate between chunks and expand context.

---

## Parsing Documents into Nodes

Use a node parser (splitter) to break Documents into Nodes. `SentenceSplitter` is the most common:

```python
from llama_index.core.node_parser import SentenceSplitter

parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
nodes = parser.get_nodes_from_documents(documents)
```

The parser:
- Splits text at sentence boundaries to preserve readability
- Respects `chunk_size` (in tokens) and `chunk_overlap` for context continuity
- Automatically assigns PREVIOUS/NEXT relationships between sequential nodes
- Copies metadata from the source Document to each Node
- Sets a SOURCE relationship from each Node back to its parent Document

---

## Relevance to This Project

The `src/rag/data_processing/` module handles Document creation from raw data sources. Chunking is configured via `CHUNK_SIZE` (default: 1024) and `CHUNK_OVERLAP` (default: 50) environment variables. Metadata is used extensively for filtering in the metadata retriever (`src/rag/retrieval/retrievers/metadata.py`).
