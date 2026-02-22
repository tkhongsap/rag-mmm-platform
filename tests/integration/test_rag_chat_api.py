"""Tests for POST /api/rag/chat — Agent SDK RAG endpoint with routing."""

from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.platform.api.main import app

client = TestClient(app)

MOCK_TARGET = "src.platform.api.agents.rag_router.ask_with_routing"


@patch(
    MOCK_TARGET,
    new_callable=AsyncMock,
    return_value={
        "reply": "Total budget is £20M across 11 channels.",
        "sources": ["meta_ads.csv"],
        "session_id": "test-session-1",
        "agent_used": "rag-analyst",
    },
)
def test_rag_chat_valid_message(mock_route):
    resp = client.post("/api/rag/chat", json={"message": "What are our channel budgets?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "Total budget is £20M across 11 channels."
    assert body["sources"] == ["meta_ads.csv"]
    assert body["session_id"] == "test-session-1"
    assert body["agent_used"] == "rag-analyst"
    mock_route.assert_awaited_once_with("What are our channel budgets?", None)


def test_rag_chat_empty_message():
    resp = client.post("/api/rag/chat", json={"message": "   "})
    assert resp.status_code == 400
    assert "message is required" in resp.json()["detail"]


def test_rag_chat_missing_message():
    resp = client.post("/api/rag/chat", json={})
    assert resp.status_code == 422


@patch(
    MOCK_TARGET,
    new_callable=AsyncMock,
    return_value={
        "reply": "I'm sorry, I wasn't able to process your question right now. Please try again.",
        "sources": [],
        "session_id": "fallback-session",
        "agent_used": "file-reader-fallback",
    },
)
def test_rag_chat_agent_error_returns_fallback(mock_route):
    """Agent errors produce a valid fallback response, not HTTP 500."""
    resp = client.post("/api/rag/chat", json={"message": "Hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["agent_used"] == "file-reader-fallback"
    assert body["session_id"] == "fallback-session"


@patch(
    MOCK_TARGET,
    new_callable=AsyncMock,
    return_value={
        "reply": "Follow-up answer.",
        "sources": [],
        "session_id": "existing-session",
        "agent_used": "rag-analyst",
    },
)
def test_rag_chat_with_session_id(mock_route):
    resp = client.post(
        "/api/rag/chat",
        json={"message": "Follow up", "session_id": "existing-session"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "Follow-up answer."
    assert body["session_id"] == "existing-session"
    mock_route.assert_awaited_once_with("Follow up", "existing-session")


@patch(
    MOCK_TARGET,
    new_callable=AsyncMock,
    return_value={
        "reply": "History still accepted.",
        "sources": [],
        "session_id": "new-session",
        "agent_used": "rag-analyst",
    },
)
def test_rag_chat_includes_history(mock_route):
    """History field is accepted for backward compatibility."""
    resp = client.post(
        "/api/rag/chat",
        json={
            "message": "Follow up",
            "history": [{"role": "user", "text": "prior"}],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["reply"] == "History still accepted."
