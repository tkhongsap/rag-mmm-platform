# Starter Tutorial

> Reference: [developers.llamaindex.ai](https://developers.llamaindex.ai) — Starter Tutorial

This tutorial walks through the core LlamaIndex workflow: creating agents, adding chat history, building a RAG pipeline, and persisting indexes.

---

## Prerequisites

- **Python 3.9+**
- **OpenAI API key** set as an environment variable (`OPENAI_API_KEY`)
- **llama-index** installed:
  ```bash
  pip install llama-index
  ```

---

## Building a Basic Agent

LlamaIndex provides `FunctionAgent`, which wraps Python functions as callable tools for an LLM. Define a function, pass it to the agent, and run a query:

```python
from llama_index.core.agent import FunctionAgent
from llama_index.llms.openai import OpenAI

async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is sunny."

agent = FunctionAgent(
    tools=[get_weather],
    llm=OpenAI(model="gpt-4o-mini"),
    system_prompt="You are a helpful assistant.",
)

response = await agent.run("What is the weather in San Francisco?")
print(response)
```

The agent inspects the function signature and docstring to decide when and how to call it.

---

## Adding Chat History

Use a `Context` object to maintain state across multiple turns. Pass the same `ctx` to each `agent.run()` call so the agent remembers prior exchanges:

```python
from llama_index.core.agent import FunctionAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(
    tools=[get_weather],
    llm=OpenAI(model="gpt-4o-mini"),
    system_prompt="You are a helpful assistant.",
)

ctx = agent.create_context()
response = await agent.run("What is the weather in San Francisco?", ctx=ctx)
print(response)
response = await agent.run("What about New York?", ctx=ctx)
print(response)
```

The second call automatically has access to the first question and answer, enabling follow-up questions without repeating context.

---

## Adding RAG

The standard RAG pipeline in LlamaIndex follows three steps: load documents, build an index, and query.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load documents from a directory
documents = SimpleDirectoryReader("data").load_data()

# Build index
index = VectorStoreIndex.from_documents(documents)

# Create query engine
query_engine = index.as_query_engine()

# Query
response = query_engine.query("What did the author do growing up?")
print(response)
```

`SimpleDirectoryReader` handles file parsing, `VectorStoreIndex` chunks and embeds the documents, and `as_query_engine()` creates a retrieval + synthesis pipeline.

---

## Using RAG as an Agent Tool

A query engine can be passed directly as a tool to a `FunctionAgent`, combining agentic reasoning with document retrieval:

```python
from llama_index.core.agent import FunctionAgent
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

agent = FunctionAgent(
    tools=[query_engine],
    llm=OpenAI(model="gpt-4o-mini"),
    system_prompt="You are a helpful assistant that can answer questions about documents.",
)

response = await agent.run("What did the author do growing up?")
print(response)
```

The agent decides when to use the query engine based on the user's question. You can combine multiple tools (RAG + custom functions) in a single agent.

---

## Persisting the Index

Avoid rebuilding the index every time by saving it to disk and reloading later:

```python
# Save
index.storage_context.persist(persist_dir="./storage")

# Reload
from llama_index.core import StorageContext, load_index_from_storage

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

The persisted storage includes the document store, index store, and vector store. Once loaded, the index is ready for querying without re-embedding.

---

## Relevance to This Project

The RAG pipeline in `src/rag/` follows this same pattern: `src/rag/data_processing/` handles document loading, `src/rag/embeddings/` handles embedding generation, and `src/rag/retrieval/` handles index creation and querying with 7 different retrieval strategies.
