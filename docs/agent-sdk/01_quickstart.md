# Claude Agent SDK — Quickstart

> Source: `platform.claude.com/docs/en/agent-sdk/quickstart`

Build an AI agent that reads code, finds bugs, and fixes them without manual intervention.

**What you'll do:**
1. Set up a project with the Agent SDK
2. Create a file with some buggy code
3. Run an agent that finds and fixes the bugs automatically

## Prerequisites

- Python 3.10+ (or Node.js 18+ for TypeScript)
- An Anthropic account and API key

## Setup

### 1. Create a project folder

```bash
mkdir my-agent && cd my-agent
```

### 2. Install the SDK

```bash
# Python (uv)
uv init && uv add claude-agent-sdk

# Python (pip)
python3 -m venv .venv && source .venv/bin/activate
pip3 install claude-agent-sdk
```

### 3. Set your API key

Create a `.env` file:

```
ANTHROPIC_API_KEY=your-api-key
```

## Create a buggy file

Create `utils.py` with intentional bugs for the agent to fix:

```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: crashes on empty list


def get_user_name(user):
    return user["name"].upper()  # Bug: crashes if user is None
```

Bugs:
1. `calculate_average([])` → division by zero
2. `get_user_name(None)` → TypeError

## Build the agent

Create `agent.py`:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],  # Tools Claude can use
            permission_mode="acceptEdits",            # Auto-approve file edits
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)          # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # Final result


asyncio.run(main())
```

### Run the agent

```bash
python3 agent.py
```

After running, check `utils.py`. The agent will have:
1. **Read** `utils.py` to understand the code
2. **Analyzed** the logic and identified edge cases
3. **Edited** the file to add proper error handling

## Key concepts

### The `query()` agentic loop

`query()` is the main entry point. It returns an async iterator — use `async for` to stream messages as Claude works. The loop runs until Claude finishes or hits an error. The SDK handles orchestration (tool execution, context management, retries) so you just consume the stream.

Three main parts:
1. **`prompt`**: what you want Claude to do
2. **`options`**: configuration (`allowedTools`, `permissionMode`, `systemPrompt`, etc.)
3. **Message loop**: stream messages — reasoning, tool calls, tool results, final outcome

### Tools

| Tools | What the agent can do |
|-------|----------------------|
| `Read`, `Glob`, `Grep` | Read-only analysis |
| `Read`, `Edit`, `Glob` | Analyze and modify code |
| `Read`, `Edit`, `Bash`, `Glob`, `Grep` | Full automation |

### Permission modes

| Mode | Behavior | Use case |
|------|----------|----------|
| `acceptEdits` | Auto-approves file edits, asks for other actions | Trusted development workflows |
| `bypassPermissions` | Runs without prompts | CI/CD pipelines, automation |
| `default` | Requires a `canUseTool` callback | Custom approval flows |

## Customize your agent

**Add web search:**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "WebSearch"],
    permission_mode="acceptEdits",
)
```

**Custom system prompt:**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob"],
    permission_mode="acceptEdits",
    system_prompt="You are a senior Python developer. Always follow PEP 8 style guidelines.",
)
```

**Enable Bash (terminal commands):**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "Bash"],
    permission_mode="acceptEdits",
)
```

With `Bash` enabled: `"Write unit tests for utils.py, run them, and fix any failures"`

## Next steps

- **[Permissions](https://platform.claude.com/docs/en/agent-sdk/permissions)**: control what your agent can do
- **[Hooks](03_hooks.md)**: run custom code before or after tool calls
- **[Sessions](05_sessions.md)**: build multi-turn agents that maintain context
- **[Subagents](04_subagents.md)**: delegate subtasks to specialized agents
- **[Python reference](02_python-reference.md)**: full API reference
