"""Stage 2: Batch embedding generation.

Produces three embedding types (IndexNode, Chunk, Summary) using OpenAI
text-embedding-3-small with rate-limited batch processing. Outputs JSON/PKL/NPY formats.
"""
