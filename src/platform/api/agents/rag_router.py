"""RAG query router with Claude Agent SDK session handling and graceful fallback."""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Any

# Allow the Agent SDK to launch inside a Claude Code session.
os.environ.pop("CLAUDECODE", None)

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)

from .prompts import ORCHESTRATOR_PROMPT, RAG_AGENT_PROMPT
from .tools import rag_mcp_server

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project root (matches rag_agent.py pattern)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve()
for _p in _PROJECT_ROOT.parents:
    if (_p / "requirements.txt").is_file() and (_p / "data").is_dir():
        _PROJECT_ROOT = _p
        break

# ---------------------------------------------------------------------------
# Session store — maps session_id → ClaudeSDKClient
# ---------------------------------------------------------------------------

_sessions: dict[str, ClaudeSDKClient] = {}


async def _extract_reply(client: ClaudeSDKClient) -> tuple[str, list[str]]:
    """Collect text reply and source file references from the agent response."""
    text_parts: list[str] = []
    sources: list[str] = []

    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)

    reply = "\n".join(text_parts)

    # Extract source references from the reply (filenames ending in .csv or .md)
    for word in reply.split():
        cleaned = word.strip("(),;:\"'`[]")
        if cleaned.endswith((".csv", ".md")) and "/" not in cleaned:
            if cleaned not in sources:
                sources.append(cleaned)

    return reply, sources


async def _create_client() -> ClaudeSDKClient:
    """Create a new ClaudeSDKClient configured for RAG routing."""
    options = ClaudeAgentOptions(
        system_prompt=ORCHESTRATOR_PROMPT,
        agents={
            "rag-analyst": AgentDefinition(
                description=(
                    "Marketing data analyst for DEEPAL/AVATR UK launch. "
                    "Use for data queries, media performance, sales pipeline, "
                    "campaign assets, contracts, and channel comparisons."
                ),
                prompt=RAG_AGENT_PROMPT,
                tools=[
                    "Read",
                    "Grep",
                    "Glob",
                    "mcp__rag-tools__search_data",
                    "mcp__rag-tools__search_assets",
                ],
                model="sonnet",
            ),
        },
        mcp_servers={"rag-tools": rag_mcp_server},
        allowed_tools=[
            "Task",
            "Read",
            "Grep",
            "Glob",
            "mcp__rag-tools__search_data",
            "mcp__rag-tools__search_assets",
        ],
        permission_mode="bypassPermissions",
        max_turns=15,
        cwd=str(_PROJECT_ROOT),
    )

    client = ClaudeSDKClient(options=options)
    await client.connect()
    return client


async def ask_with_routing(
    question: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Route a question through the Claude Agent SDK orchestrator.

    Returns a dict with keys: reply, sources, session_id, agent_used.
    Falls back to rag_agent.ask_marketing_question when the SDK is unavailable.
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    try:
        # Reuse or create client for this session
        client = _sessions.get(session_id)
        if client is None:
            client = await _create_client()
            _sessions[session_id] = client

        await client.query(question)
        reply, sources = await _extract_reply(client)

        return {
            "reply": reply,
            "sources": sources,
            "session_id": session_id,
            "agent_used": "rag-analyst",
        }

    except Exception:
        logger.exception("Agent SDK routing failed — falling back to file reader")
        # Remove broken session
        _sessions.pop(session_id, None)

        try:
            from ..rag_agent import ask_marketing_question

            fallback_reply = await ask_marketing_question(question)
            return {
                "reply": fallback_reply,
                "sources": [],
                "session_id": session_id,
                "agent_used": "file-reader-fallback",
            }
        except Exception:
            logger.exception("Fallback also failed")
            return {
                "reply": "I'm sorry, I wasn't able to process your question right now. Please try again.",
                "sources": [],
                "session_id": session_id,
                "agent_used": "file-reader-fallback",
            }
