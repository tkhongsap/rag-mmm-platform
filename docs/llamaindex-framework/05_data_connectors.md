# Data Connectors (Readers)

> Reference: [developers.llamaindex.ai](https://developers.llamaindex.ai) — Data Connectors

Data connectors (also called Readers) load data from various sources into LlamaIndex Document objects. They abstract away source-specific parsing so you get a uniform list of Documents regardless of origin.

---

## Overview

Every data connector implements the same interface: call `.load_data()` and get back a list of `Document` objects. This uniformity means the rest of the pipeline (chunking, embedding, indexing, retrieval) works identically regardless of where the data came from.

---

## SimpleDirectoryReader

The most common reader. It reads all supported files from a directory, automatically detecting file types and applying the appropriate parser.

```python
from llama_index.core import SimpleDirectoryReader

# Read all supported files from a directory
documents = SimpleDirectoryReader("./data").load_data()

# Read specific file types
documents = SimpleDirectoryReader(
    input_dir="./data",
    required_exts=[".pdf", ".md", ".txt"],
).load_data()

# Read specific files
documents = SimpleDirectoryReader(
    input_files=["./data/file1.pdf", "./data/file2.txt"]
).load_data()
```

### Supported formats

| Category | Formats |
|----------|---------|
| Text | `.txt`, `.md`, `.csv` |
| Documents | `.pdf`, `.docx`, `.pptx` |
| Images | `.jpg`, `.png` (with image parsing) |
| Media | `.mp3`, `.mp4` (with transcription) |

Each file is converted into one or more Document objects with metadata automatically populated (filename, file path, creation date, etc.).

---

## LlamaHub

LlamaHub is the community-maintained connector ecosystem at [llamahub.ai](https://llamahub.ai). It provides hundreds of integrations installable as separate packages:

```bash
pip install llama-index-readers-database
pip install llama-index-readers-google
pip install llama-index-readers-notion
```

Each connector follows the same `.load_data()` interface, making it straightforward to swap data sources without changing downstream code.

---

## Common Third-Party Connectors

### Database

```python
from llama_index.readers.database import DatabaseReader

reader = DatabaseReader(uri="sqlite:///my_database.db")
documents = reader.load_data(query="SELECT text, metadata FROM documents")
```

### Google Docs

```python
from llama_index.readers.google import GoogleDocsReader

reader = GoogleDocsReader()
documents = reader.load_data(document_ids=["doc_id_1", "doc_id_2"])
```

### Notion

```python
from llama_index.readers.notion import NotionPageReader

reader = NotionPageReader(integration_token="secret_...")
documents = reader.load_data(page_ids=["page_id_1"])
```

### Slack

```python
from llama_index.readers.slack import SlackReader

reader = SlackReader(slack_token="xoxb-...")
documents = reader.load_data(channel_ids=["C01234567"])
```

All connectors return standard `Document` objects with source-specific metadata populated automatically.

---

## Creating Documents Directly

When you already have data in memory (from an API call, database query, or any other source), create Document objects directly:

```python
from llama_index.core import Document

documents = [
    Document(text="First document content", metadata={"source": "api"}),
    Document(text="Second document content", metadata={"source": "manual"}),
]
```

This is useful when integrating with existing data pipelines or when no pre-built connector exists for your data source.

---

## Relevance to This Project

The `src/rag/data_processing/` module handles document loading and preparation. The project primarily uses file-based loading for CSV and document formats, configured through the data processing pipeline.
