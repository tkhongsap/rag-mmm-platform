# Response Synthesizers

> Source: [LlamaIndex Documentation — Response Synthesizers](https://developers.llamaindex.ai)

## Overview

A response synthesizer takes a query and a set of retrieved text chunks (nodes) and generates a natural language response. It is the final stage of the RAG pipeline — where retrieved context becomes a coherent answer. The choice of response mode affects quality, latency, and cost.

```
Query → Retriever → Postprocessors → [Response Synthesizer] → Final Answer
```

LlamaIndex provides 8 built-in response modes, each with different tradeoffs.

---

## Getting a Response Synthesizer

Use the factory function to create a response synthesizer with a specific mode:

```python
from llama_index.core.response_synthesizers import get_response_synthesizer

response_synthesizer = get_response_synthesizer(response_mode="compact")
```

---

## The 8 Response Modes

### `refine`

Sequentially processes each chunk. Generates an initial answer from the first chunk, then refines it with each subsequent chunk:

```python
synth = get_response_synthesizer(response_mode="refine")
```

- **Pros:** Thorough, considers all chunks
- **Cons:** Slow (one LLM call per chunk), expensive
- **Best for:** Detailed answers requiring all context

### `compact` (default)

Concatenates chunks that fit within the context window, then applies the refine process on the concatenated groups:

```python
synth = get_response_synthesizer(response_mode="compact")
```

- **Pros:** Fewer LLM calls than refine, good quality
- **Cons:** May still need multiple calls for large result sets
- **Best for:** General-purpose use (default for good reason)

### `tree_summarize`

Recursively builds a tree of summaries. Chunks are summarized in groups, then those summaries are summarized, until a single root summary remains:

```python
synth = get_response_synthesizer(response_mode="tree_summarize")
```

- **Pros:** Handles very large result sets efficiently
- **Cons:** Multiple LLM calls, may lose detail
- **Best for:** Summarization tasks, large document sets

### `simple_summarize`

Truncates all chunks to fit in a single prompt:

```python
synth = get_response_synthesizer(response_mode="simple_summarize")
```

- **Pros:** Fastest (single LLM call)
- **Cons:** May lose context from truncation
- **Best for:** Quick answers when speed matters most

### `no_text`

Returns the retrieved nodes without generating a response:

```python
synth = get_response_synthesizer(response_mode="no_text")
```

- **Use when:** You only need the retrieved chunks, not an LLM-generated answer

### `context_only`

Returns the raw context string that would be used for synthesis, without making the LLM call:

```python
synth = get_response_synthesizer(response_mode="context_only")
```

### `accumulate`

Generates a separate response for each chunk, then accumulates all responses:

```python
synth = get_response_synthesizer(response_mode="accumulate")
```

- **Pros:** Each chunk gets individual attention
- **Cons:** Expensive (one call per chunk), responses may be redundant
- **Best for:** When you want per-source answers

### `compact_accumulate`

Compacts chunks first (combining those that fit together), then accumulates responses:

```python
synth = get_response_synthesizer(response_mode="compact_accumulate")
```

---

## Using with a Query Engine

Pass the response synthesizer to a `RetrieverQueryEngine`:

```python
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=get_response_synthesizer(response_mode="tree_summarize"),
)
```

Or use the high-level API on an index:

```python
query_engine = index.as_query_engine(response_mode="tree_summarize")
```

---

## Streaming Responses

Enable streaming for real-time token output. This is useful for interactive applications where you want to display the response as it is generated:

```python
synth = get_response_synthesizer(response_mode="compact", streaming=True)
query_engine = index.as_query_engine(streaming=True)

streaming_response = query_engine.query("What is the main topic?")
for text in streaming_response.response_gen:
    print(text, end="")
```

Streaming works with `refine`, `compact`, `tree_summarize`, and `simple_summarize` modes.

---

## Structured Output Filtering

Use Pydantic models to enforce structured output from the response synthesizer:

```python
from pydantic import BaseModel


class Answer(BaseModel):
    response: str
    confidence: float


synth = get_response_synthesizer(
    response_mode="compact",
    output_cls=Answer,
)
```

The LLM output will be parsed into the specified Pydantic model, giving you typed, validated responses.

---

## Custom Response Synthesizer

Create your own response synthesizer by extending `BaseSynthesizer`:

```python
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core.schema import NodeWithScore, QueryBundle


class CustomSynthesizer(BaseSynthesizer):
    def get_response(
        self,
        query_str: str,
        text_chunks: list[str],
        **kwargs,
    ) -> str:
        # Custom synthesis logic
        context = "\n".join(text_chunks)
        # Use self._llm to generate response
        return f"Based on {len(text_chunks)} sources: ..."
```

Custom synthesizers are useful for:

- Domain-specific response formatting
- Multi-language response generation
- Custom prompting strategies
- Integration with non-LLM response generation (e.g., template-based answers)

---

## Relevance to This Project

Response synthesis is configured within each retrieval strategy in `src/rag/retrieval/`. The choice of response mode affects both answer quality and API costs. The project's retrieval strategies may use different synthesis modes depending on the use case — see `references/rag-llamaindex/` for benchmarks comparing response modes.
