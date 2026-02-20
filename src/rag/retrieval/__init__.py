"""Stages 3-4: Index loading and retrieval orchestration.

Loads saved embeddings into LlamaIndex indices and routes queries to the appropriate
retrieval strategy via agentic classification.
"""

from .query_engine import search_text

__all__ = ["search_text"]
