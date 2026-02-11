# Installation & Environment Setup

> Source: [developers.llamaindex.ai](https://developers.llamaindex.ai) -- LlamaIndex official documentation.

## Quick Install

Install LlamaIndex with a single command:

```bash
pip install llama-index
```

This installs the **starter bundle**, which includes the core framework and the most common integrations:

- `llama-index-core` -- Core framework (required)
- `llama-index-llms-openai` -- OpenAI LLM integration
- `llama-index-embeddings-openai` -- OpenAI embedding models
- `llama-index-program-openai` -- OpenAI function calling programs
- `llama-index-multi-modal-llms-openai` -- OpenAI multi-modal support
- `llama-index-readers-file` -- File readers (PDF, DOCX, CSV, etc.)

The starter bundle is the fastest way to get up and running with LlamaIndex using OpenAI as the default LLM and embedding provider.

## Namespaced Package System

LlamaIndex uses a **namespaced package architecture** to keep the ecosystem modular and lightweight. The design separates the core framework from all third-party integrations.

- **Core framework**: `llama-index-core` contains all fundamental abstractions (Documents, Nodes, Indices, Retrievers, etc.) with no external provider dependencies.
- **Integration packages**: Each integration is a standalone package following the naming convention `llama-index-{component}-{provider}`.

### Examples of Integration Packages

```
llama-index-llms-anthropic          # Anthropic Claude LLM
llama-index-llms-ollama             # Ollama local LLM
llama-index-embeddings-huggingface  # HuggingFace embedding models
llama-index-vector-stores-chroma    # Chroma vector store
llama-index-vector-stores-pinecone  # Pinecone vector store
llama-index-readers-database        # Database readers
llama-index-readers-web             # Web page readers
```

### Benefits of Namespaced Packages

- **Reduced dependency bloat**: You only install the integrations you actually use, keeping your environment lean.
- **Independent versioning**: Each integration package can release updates on its own schedule without waiting for a core framework release.
- **Clear ownership**: Each package maps to a specific provider, making it easy to find the right integration.

## Custom / Minimal Installation

For production deployments or custom setups where you want full control over installed packages, start with just the core and add only what you need:

```bash
# Core framework (always required)
pip install llama-index-core

# Add only the integrations you use
pip install llama-index-llms-openai
pip install llama-index-embeddings-openai
pip install llama-index-readers-file
```

This approach is recommended when:

- You want to minimize your dependency footprint in production.
- You are using a non-OpenAI LLM or embedding provider.
- You need to pin specific versions of individual integrations.
- You are building a Docker image and want to keep the image size small.

## Important Environment Setup

LlamaIndex defaults to OpenAI for both LLM and embedding calls. You need to set your OpenAI API key before using the framework.

### Setting the API Key in Code

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

### Setting the API Key via `.env` File

Create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-...
```

Then load it in your application:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Using a Non-OpenAI Provider

If you are not using OpenAI, you must explicitly configure your LLM and embedding model. LlamaIndex provides a `Settings` object for global configuration:

```python
from llama_index.core import Settings
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.llm = Anthropic(model="claude-sonnet-4-20250514")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```

## Source Installation

For development or contributing to LlamaIndex:

```bash
git clone https://github.com/run-llama/llama_index.git
cd llama_index
poetry install
```

This clones the full monorepo and installs all packages in development mode. Useful if you need to debug framework internals or contribute patches upstream.

## Relevance to This Project

This project's dependencies are managed through `requirements.txt` and `make install`. The RAG pipeline uses OpenAI embeddings (`text-embedding-3-small`) and LLM (`gpt-4o-mini`), configured via environment variables in `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
EMBED_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

See the root `CLAUDE.md` for the full list of environment variables and their defaults.
