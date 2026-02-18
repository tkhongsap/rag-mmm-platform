"""Agent SDK integration for RAG chat — reads project data files to answer marketing questions."""

from __future__ import annotations

import os
from pathlib import Path

# Allow the Agent SDK to launch even when running inside a Claude Code session.
os.environ.pop("CLAUDECODE", None)

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

PROJECT_ROOT = Path(__file__).resolve()
for _parent in PROJECT_ROOT.parents:
    if (_parent / "requirements.txt").is_file() and (_parent / "data").is_dir():
        PROJECT_ROOT = _parent
        break

SYSTEM_PROMPT = """You are a marketing data analyst for the DEEPAL/AVATR UK automotive launch.

You have access to the following project data (read-only):

- data/raw/ — ~19 CSVs covering digital media (Meta, Google, DV360, TikTok, YouTube, LinkedIn),
  traditional media (TV, OOH, print, radio), and sales pipeline (vehicle sales, website sessions,
  configurator usage, leads, test drives)
- data/raw/contracts/ — 7 markdown vendor contracts (ITV, Sky, JCDecaux, etc.)
- data/mmm/ — 3 MMM-ready weekly datasets (weekly_channel_spend, weekly_sales, model_ready)
- data/generators/config.py — master config with channel benchmarks (CPM/CTR/CPC), budgets,
  seasonal multipliers, campaign naming templates

INSTRUCTIONS:
- Answer questions using the ACTUAL data in these files. Read the files before answering.
- Cite specific file names and numbers from the data.
- If a question cannot be answered from the available data, say so clearly.
- Format responses in clean markdown with tables where appropriate.
- Keep answers concise but thorough."""


async def ask_marketing_question(question: str):
    """Stream an answer to a marketing question using the Agent SDK.

    Yields text chunks as the agent reads data files and formulates a response.
    """
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        max_turns=10,
        cwd=str(PROJECT_ROOT),
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="bypassPermissions",
    )

    full_response = []
    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    full_response.append(block.text)

    return "\n".join(full_response)
