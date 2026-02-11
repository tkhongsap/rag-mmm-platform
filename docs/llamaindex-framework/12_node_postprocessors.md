# Node Postprocessors

> Source: [LlamaIndex Documentation — Node Postprocessors](https://developers.llamaindex.ai)

## Overview

Node postprocessors are applied after retrieval and before response synthesis. They transform, filter, or rerank the retrieved nodes. This is a critical step for improving retrieval quality — raw retrieval results often benefit from additional processing.

The postprocessing pipeline sits between the retriever and the response synthesizer:

```
Query → Retriever → [Node Postprocessors] → Response Synthesizer → Response
```

LlamaIndex provides several built-in postprocessors, and you can create custom ones by extending `BaseNodePostprocessor`.

---

## SimilarityPostprocessor

Filter nodes by similarity score. Nodes with a score below the cutoff are removed, eliminating low-relevance results.

```python
from llama_index.core.postprocessor import SimilarityPostprocessor

postprocessor = SimilarityPostprocessor(similarity_cutoff=0.7)
```

This is one of the simplest and most effective postprocessors. Set the cutoff based on your embedding model and quality requirements — higher values produce more precise but fewer results.

---

## KeywordNodePostprocessor

Filter nodes by the presence or absence of specific keywords:

```python
from llama_index.core.postprocessor import KeywordNodePostprocessor

postprocessor = KeywordNodePostprocessor(
    required_keywords=["machine learning", "neural network"],
    exclude_keywords=["deprecated", "outdated"],
)
```

Nodes must contain at least one of the `required_keywords` and none of the `exclude_keywords`. This is useful for enforcing topic relevance or excluding stale content.

---

## TimeWeightedPostprocessor

Boost recent documents by applying exponential time decay to scores:

```python
from llama_index.core.postprocessor import TimeWeightedPostprocessor

postprocessor = TimeWeightedPostprocessor(
    time_decay=0.99,
    time_access_refresh=False,
    top_k=5,
)
```

The `time_decay` parameter controls how aggressively older documents are penalized. A value close to 1.0 applies mild decay, while lower values strongly favor recent content. Set `time_access_refresh=True` to update access timestamps when nodes are retrieved.

---

## CohereRerank

Neural reranking using Cohere's rerank API. This provides high-quality relevance scoring using a cross-encoder model:

```python
from llama_index.postprocessor.cohere_rerank import CohereRerank

reranker = CohereRerank(
    api_key="your-cohere-api-key",
    top_n=5,
)
```

**Installation:**

```bash
pip install llama-index-postprocessor-cohere-rerank
```

Cohere reranking is particularly effective for improving precision — it re-scores each node against the query using a dedicated relevance model, which is more accurate than initial retrieval scores alone.

---

## SentenceTransformerRerank

Local neural reranking using a cross-encoder model from the Sentence Transformers library. No external API required:

```python
from llama_index.core.postprocessor import SentenceTransformerRerank

reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    top_n=5,
)
```

This runs the reranking model locally, which avoids API costs and latency but requires GPU/CPU resources. The `ms-marco-MiniLM-L-2-v2` model is a good balance of speed and accuracy for general-purpose reranking.

---

## PrevNextNodePostprocessor

Include adjacent nodes to provide surrounding context. This is useful when a single chunk doesn't contain enough context on its own:

```python
from llama_index.core.postprocessor import PrevNextNodePostprocessor

postprocessor = PrevNextNodePostprocessor(
    docstore=index.docstore,
    num_nodes=1,
    mode="both",  # "previous", "next", or "both"
)
```

The `mode` parameter controls which direction to expand:
- `"previous"` — include nodes that come before the matched node
- `"next"` — include nodes that come after
- `"both"` — include nodes in both directions

The `num_nodes` parameter controls how many adjacent nodes to fetch in each direction. This requires access to the index's document store.

---

## Using Postprocessors

### With a Query Engine

The most common usage is passing postprocessors to a `RetrieverQueryEngine`. Multiple postprocessors are applied in sequence:

```python
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[
        SimilarityPostprocessor(similarity_cutoff=0.7),
        reranker,
    ],
)
```

Postprocessors are applied in order — in this example, low-similarity nodes are filtered first, then the remaining nodes are reranked. Order matters: filtering before reranking reduces the reranker's workload.

### Standalone Usage

You can also use postprocessors independently outside a query engine:

```python
from llama_index.core.schema import QueryBundle

query = QueryBundle(query_str="What is machine learning?")
filtered_nodes = postprocessor.postprocess_nodes(
    nodes, query_bundle=query
)
```

This is useful for debugging, custom pipelines, or when you need fine-grained control over the postprocessing step.

---

## Custom Postprocessor

Create your own postprocessor by extending `BaseNodePostprocessor` and implementing the `_postprocess_nodes` method:

```python
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from typing import List, Optional


class CustomPostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        # Custom logic here
        filtered = []
        for node in nodes:
            if len(node.node.text) > 100:  # Example: min length filter
                filtered.append(node)
        return filtered
```

Custom postprocessors can implement any filtering, scoring, or transformation logic. Common use cases include:

- Deduplication of near-identical chunks
- Domain-specific relevance scoring
- Metadata-based filtering (e.g., access control, date ranges)
- Content quality checks (minimum length, language detection)

---

## Relevance to This Project

Node postprocessing is integrated into the retrieval strategies in `src/rag/retrieval/`. Different strategies apply different postprocessors — for example, the hybrid retriever uses reciprocal rank fusion for reranking, while other strategies may apply similarity cutoffs. See `references/rag-llamaindex/` for benchmarks on different postprocessing approaches.
