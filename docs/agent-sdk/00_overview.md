# Claude Agent SDK — Overview

> Source: `platform.claude.com/docs/en/agent-sdk/overview`

Build AI agents that autonomously read files, run commands, search the web, edit code, and more. The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.

> **Note:** The Claude Code SDK has been renamed to the Claude Agent SDK. If migrating from the old SDK, see the Migration Guide.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)

asyncio.run(main())
```

## Get started

### 1. Install

```bash
pip install claude-agent-sdk
# or TypeScript:
# npm install @anthropic-ai/claude-agent-sdk
```

### 2. Set API key

```bash
export ANTHROPIC_API_KEY=your-api-key
```

Third-party providers:
- **Amazon Bedrock**: set `CLAUDE_CODE_USE_BEDROCK=1` + configure AWS credentials
- **Google Vertex AI**: set `CLAUDE_CODE_USE_VERTEX=1` + configure GCP credentials
- **Microsoft Azure**: set `CLAUDE_CODE_USE_FOUNDRY=1` + configure Azure credentials

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

## Capabilities

### Built-in tools

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
| **AskUserQuestion** | Ask the user clarifying questions with multiple choice |

### Hooks

Run custom code at key points in the agent lifecycle. Available hooks: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, and more.

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher
from datetime import datetime

async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
    with open("./audit.log", "a") as f:
        f.write(f"{datetime.now()}: modified {file_path}\n")
    return {}

options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    hooks={
        "PostToolUse": [
            HookMatcher(matcher="Edit|Write", hooks=[log_file_change])
        ]
    },
)
```

### Subagents

Spawn specialized agents to handle focused subtasks. Include `Task` in `allowedTools` since subagents are invoked via the Task tool:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep", "Task"],
    agents={
        "code-reviewer": AgentDefinition(
            description="Expert code reviewer for quality and security reviews.",
            prompt="Analyze code quality and suggest improvements.",
            tools=["Read", "Glob", "Grep"],
        )
    },
)
```

Messages from within a subagent's context include a `parent_tool_use_id` field, letting you track which messages belong to which subagent execution.

### MCP

Connect to external systems via the Model Context Protocol: databases, browsers, APIs, and hundreds more.

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
    }
)
```

### Permissions

Control which tools your agent can use. Allow safe operations, block dangerous ones, or require approval for sensitive actions.

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"],
    permission_mode="bypassPermissions",
)
```

### Sessions

Maintain context across multiple exchanges. Resume sessions later, or fork them to explore different approaches.

```python
session_id = None

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
```

### Claude Code filesystem features

Set `setting_sources=["project"]` to use CLAUDE.md and `.claude/` filesystem config:

| Feature | Description | Location |
|---------|-------------|----------|
| **Skills** | Specialized capabilities defined in Markdown | `.claude/skills/SKILL.md` |
| **Slash commands** | Custom commands for common tasks | `.claude/commands/*.md` |
| **Memory** | Project context and instructions | `CLAUDE.md` |
| **Plugins** | Extend with custom commands, agents, MCP servers | Programmatic via `plugins` option |

## SDK vs Client SDK vs CLI

### Agent SDK vs Client SDK

With the Client SDK, you implement a tool loop. With the Agent SDK, Claude handles it:

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

### Agent SDK vs Claude Code CLI

| Use case | Best choice |
|----------|-------------|
| Interactive development | CLI |
| CI/CD pipelines | SDK |
| Custom applications | SDK |
| One-off tasks | CLI |
| Production automation | SDK |

## Branding guidelines

- **Allowed**: "Claude Agent", "Claude", "{YourAgentName} Powered by Claude"
- **Not permitted**: "Claude Code" or "Claude Code Agent"
