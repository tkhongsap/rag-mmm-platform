"""MCP tool wrappers around LlamaIndex retrieval functions for Claude Agent SDK."""

from __future__ import annotations

import json
from typing import Any

from claude_agent_sdk import tool, create_sdk_mcp_server


@tool(
    "search_data",
    "Search text data (CSVs, contracts, config) using hybrid retrieval (vector + BM25). "
    "Use category filter to narrow results: digital_media, traditional_media, sales_pipeline, external.",
    {"query": str, "top_k": int, "category": str},
)
async def search_data(args: dict[str, Any]) -> dict[str, Any]:
    """Invoke query_engine.search_text with hybrid retrieval."""
    try:
        from src.rag.retrieval.query_engine import search_text

        results = search_text(
            query=args["query"],
            top_k=args.get("top_k", 5),
            category=args.get("category") or None,
        )
        return {"content": [{"type": "text", "text": json.dumps(results, default=str)}]}
    except Exception as exc:
        return {"content": [{"type": "text", "text": f"search_data error: {exc}"}], "isError": True}


@tool(
    "search_assets",
    "Search campaign creative assets (images, ads) using dense vector retrieval. "
    "Use channel filter to narrow by source: meta, google, tv, ooh, youtube, tiktok, etc.",
    {"query": str, "top_k": int, "channel": str},
)
async def search_assets(args: dict[str, Any]) -> dict[str, Any]:
    """Invoke query_engine.search_assets with optional channel filtering."""
    try:
        from src.rag.retrieval.query_engine import search_assets as _search_assets

        results = _search_assets(
            query=args["query"],
            top_k=args.get("top_k", 5),
            channel=args.get("channel") or None,
        )
        return {"content": [{"type": "text", "text": json.dumps(results, default=str)}]}
    except Exception as exc:
        return {"content": [{"type": "text", "text": f"search_assets error: {exc}"}], "isError": True}


@tool(
    "filter_by_channel",
    "Search text data filtered to a specific channel category. "
    "Shortcut for search_data with category pre-set to the channel name.",
    {"query": str, "channel": str},
)
async def filter_by_channel(args: dict[str, Any]) -> dict[str, Any]:
    """Invoke query_engine.search_text with category set to the given channel."""
    try:
        from src.rag.retrieval.query_engine import search_text

        results = search_text(
            query=args["query"],
            category=args.get("channel") or None,
        )
        return {"content": [{"type": "text", "text": json.dumps(results, default=str)}]}
    except Exception as exc:
        return {"content": [{"type": "text", "text": f"filter_by_channel error: {exc}"}], "isError": True}


rag_mcp_server = create_sdk_mcp_server(
    "rag-tools",
    tools=[search_data, search_assets, filter_by_channel],
)
