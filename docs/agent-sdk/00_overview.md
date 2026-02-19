# Agent SDK Overview

> Source: `platform.claude.com/docs/en/agent-sdk/overview`

Build production AI agents with Claude Code as a library.

> **Note:** The Claude Code SDK has been renamed to the Claude Agent SDK. If you're migrating from the old SDK, see the [Migration Guide](./14_migration-guide.md).

Build AI agents that autonomously read files, run commands, search the web, edit code, and more. The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.

## Quick Example

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)  # Claude reads the file, finds the bug, edits it


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix the bug in auth.py",
  options: { allowedTools: ["Read", "Edit", "Bash"] }
})) {
  console.log(message);
}
```

The Agent SDK includes built-in tools for reading files, running commands, and editing code, so your agent can start working immediately without you implementing tool execution.

## Get Started

### 1. Install the SDK

```bash
# TypeScript
npm install @anthropic-ai/claude-agent-sdk

# Python
pip install claude-agent-sdk
```

### 2. Set your API key

Get an API key from the [Console](https://platform.claude.com/), then set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your-api-key
```

The SDK also supports authentication via third-party API providers:

- **Amazon Bedrock**: set `CLAUDE_CODE_USE_BEDROCK=1` and configure AWS credentials
- **Google Vertex AI**: set `CLAUDE_CODE_USE_VERTEX=1` and configure Google Cloud credentials
- **Microsoft Azure**: set `CLAUDE_CODE_USE_FOUNDRY=1` and configure Azure credentials

> Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Please use the API key authentication methods described in this document instead.

### 3. Run your first agent

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="What files are in this directory?",
        options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "What files are in this directory?",
  options: { allowedTools: ["Bash", "Glob"] }
})) {
  if ("result" in message) console.log(message.result);
}
```

## Capabilities

Everything that makes Claude Code powerful is available in the SDK:

### Built-in Tools

Your agent can read files, run commands, and search codebases out of the box:

| Tool | What it does |
|------|--------------|
| **Read** | Read any file in the working directory |
| **Write** | Create new files |
| **Edit** | Make precise edits to existing files |
| **Bash** | Run terminal commands, scripts, git operations |
| **Glob** | Find files by pattern (`**/*.ts`, `src/**/*.py`) |
| **Grep** | Search file contents with regex |
| **WebSearch** | Search the web for current information |
| **WebFetch** | Fetch and parse web page content |
| **AskUserQuestion** | Ask the user clarifying questions with multiple choice options |

### Hooks

Run custom code at key points in the agent lifecycle. SDK hooks use callback functions to validate, log, block, or transform agent behavior.

**Available hooks:** `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, and more.

```python
import asyncio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
    with open("./audit.log", "a") as f:
        f.write(f"{datetime.now()}: modified {file_path}\n")
    return {}


async def main():
    async for message in query(
        prompt="Refactor utils.py to improve readability",
        options=ClaudeAgentOptions(
            permission_mode="acceptEdits",
            hooks={
                "PostToolUse": [
                    HookMatcher(matcher="Edit|Write", hooks=[log_file_change])
                ]
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### Subagents

Spawn specialized agents to handle focused subtasks. Your main agent delegates work, and subagents report back with results.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Use the code-reviewer agent to review this codebase",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Task"],
            agents={
                "code-reviewer": AgentDefinition(
                    description="Expert code reviewer for quality and security reviews.",
                    prompt="Analyze code quality and suggest improvements.",
                    tools=["Read", "Glob", "Grep"],
                )
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

Messages from within a subagent's context include a `parent_tool_use_id` field, letting you track which messages belong to which subagent execution.

### MCP (Model Context Protocol)

Connect to external systems via the Model Context Protocol: databases, browsers, APIs, and more.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Open example.com and describe what you see",
        options=ClaudeAgentOptions(
            mcp_servers={
                "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
            }
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### Permissions

Control exactly which tools your agent can use. Allow safe operations, block dangerous ones, or require approval for sensitive actions.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Review this code for best practices",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"], permission_mode="bypassPermissions"
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### Sessions

Maintain context across multiple exchanges. Resume sessions later, or fork them to explore different approaches.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    session_id = None

    # First query: capture the session ID
    async for message in query(
        prompt="Read the authentication module",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
    ):
        if hasattr(message, "subtype") and message.subtype == "init":
            session_id = message.session_id

    # Resume with full context from the first query
    async for message in query(
        prompt="Now find all places that call it",
        options=ClaudeAgentOptions(resume=session_id),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### Claude Code Features

The SDK also supports Claude Code's filesystem-based configuration. Set `setting_sources=["project"]` (Python) or `settingSources: ['project']` (TypeScript) in your options.

| Feature | Description | Location |
|---------|-------------|----------|
| Skills | Specialized capabilities defined in Markdown | `.claude/skills/SKILL.md` |
| Slash commands | Custom commands for common tasks | `.claude/commands/*.md` |
| Memory | Project context and instructions | `CLAUDE.md` or `.claude/CLAUDE.md` |
| Plugins | Extend with custom commands, agents, and MCP servers | Programmatic via `plugins` option |

## Agent SDK vs Client SDK

The Anthropic Client SDK gives you direct API access: you send prompts and implement tool execution yourself. The Agent SDK gives you Claude with built-in tool execution.

```python
# Client SDK: You implement the tool loop
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude handles tools autonomously
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

## Agent SDK vs Claude Code CLI

| Use case | Best choice |
|----------|-------------|
| Interactive development | CLI |
| CI/CD pipelines | SDK |
| Custom applications | SDK |
| One-off tasks | CLI |
| Production automation | SDK |

## Changelog

- **TypeScript SDK**: [CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
- **Python SDK**: [CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)

## Reporting Bugs

- **TypeScript SDK**: [GitHub Issues](https://github.com/anthropics/claude-agent-sdk-typescript/issues)
- **Python SDK**: [GitHub Issues](https://github.com/anthropics/claude-agent-sdk-python/issues)

## License and Terms

Use of the Claude Agent SDK is governed by [Anthropic's Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).
