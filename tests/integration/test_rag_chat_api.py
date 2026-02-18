"""Tests for POST /api/rag/chat — Agent SDK RAG endpoint."""

from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.platform.api.main import app

client = TestClient(app)

MOCK_TARGET = "src.platform.api.rag_agent.ask_marketing_question"


@patch(MOCK_TARGET, new_callable=AsyncMock, return_value="Total budget is £20M across 11 channels.")
def test_rag_chat_valid_message(mock_ask):
    resp = client.post("/api/rag/chat", json={"message": "What are our channel budgets?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "reply" in body
    assert body["reply"] == "Total budget is £20M across 11 channels."
    mock_ask.assert_awaited_once_with("What are our channel budgets?")


def test_rag_chat_empty_message():
    resp = client.post("/api/rag/chat", json={"message": "   "})
    assert resp.status_code == 400
    assert "message is required" in resp.json()["detail"]


def test_rag_chat_missing_message():
    resp = client.post("/api/rag/chat", json={})
    assert resp.status_code == 422


@patch(MOCK_TARGET, new_callable=AsyncMock, side_effect=RuntimeError("API key missing"))
def test_rag_chat_agent_error(mock_ask):
    resp = client.post("/api/rag/chat", json={"message": "Hello"})
    assert resp.status_code == 500
    assert "API key missing" in resp.json()["detail"]


@patch(MOCK_TARGET, new_callable=AsyncMock, return_value="Follow-up answer.")
def test_rag_chat_includes_history(mock_ask):
    resp = client.post(
        "/api/rag/chat",
        json={
            "message": "Follow up",
            "history": [{"role": "user", "text": "prior"}],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["reply"] == "Follow-up answer."
