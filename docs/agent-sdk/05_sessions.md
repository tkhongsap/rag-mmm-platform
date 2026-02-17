# Claude Agent SDK — Sessions

> Source: `platform.claude.com/docs/en/agent-sdk/sessions`

Sessions allow you to continue conversations across multiple interactions while maintaining full context — files read, analysis done, conversation history.

## How Sessions Work

When you start a new query, the SDK creates a session and returns a session ID in the initial system message. Capture this ID to resume later.

### Getting the Session ID

```python
from claude_agent_sdk import query, ClaudeAgentOptions

session_id = None

async for message in query(
    prompt="Help me build a web application",
    options=ClaudeAgentOptions(model="claude-opus-4-6"),
):
    # The first message is a system init message with the session ID
    if hasattr(message, "subtype") and message.subtype == "init":
        session_id = message.data.get("session_id")
        print(f"Session started with ID: {session_id}")

    print(message)

# Later, resume with the saved session_id
if session_id:
    async for message in query(
        prompt="Continue where we left off",
        options=ClaudeAgentOptions(resume=session_id),
    ):
        print(message)
```

## Resuming Sessions

Use `resume` with a session ID to continue a previous conversation with full context:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Resume a previous session using its ID
async for message in query(
    prompt="Continue implementing the authentication system from where we left off",
    options=ClaudeAgentOptions(
        resume="session-xyz",          # Session ID from previous conversation
        model="claude-opus-4-6",
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep", "Bash"],
    ),
):
    print(message)
```

The SDK automatically loads conversation history and context when you resume, allowing Claude to continue exactly where it left off.

## Forking Sessions

When resuming, you can continue the original session or fork it into a new branch. Use `fork_session=True` to create a new session ID that starts from the resumed state.

### When to Fork

- Explore different approaches from the same starting point
- Create multiple conversation branches without modifying the original
- Test changes without affecting the original session history
- Maintain separate paths for different experiments

### Forking vs Continuing

| Behavior | `fork_session=False` (default) | `fork_session=True` |
|----------|-------------------------------|---------------------|
| **Session ID** | Same as original | New session ID generated |
| **History** | Appends to original session | Creates new branch from resume point |
| **Original Session** | Modified | Preserved unchanged |
| **Use Case** | Continue linear conversation | Branch to explore alternatives |

### Example: Forking a Session

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Step 1: Run first query and capture session ID
session_id = None

async for message in query(
    prompt="Help me design a REST API",
    options=ClaudeAgentOptions(model="claude-opus-4-6"),
):
    if hasattr(message, "subtype") and message.subtype == "init":
        session_id = message.data.get("session_id")
        print(f"Original session: {session_id}")

# Step 2: Fork the session to try a different approach
forked_id = None

async for message in query(
    prompt="Now let's redesign this as a GraphQL API instead",
    options=ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,       # Creates a new session ID
        model="claude-opus-4-6",
    ),
):
    if hasattr(message, "subtype") and message.subtype == "init":
        forked_id = message.data.get("session_id")
        print(f"Forked session: {forked_id}")  # Different ID from original

# Step 3: Original session is still intact
async for message in query(
    prompt="Add authentication to the REST API",
    options=ClaudeAgentOptions(
        resume=session_id,
        fork_session=False,      # Continue original session (default)
        model="claude-opus-4-6",
    ),
):
    print(message)
```

## Multi-Turn Workflow Pattern

Practical pattern for building multi-step workflows where each step builds on the previous:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def multi_turn_analysis():
    session_id = None

    # Turn 1: Read and understand the codebase
    async for message in query(
        prompt="Read the authentication module and understand its structure",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
        ),
    ):
        if hasattr(message, "session_id"):
            session_id = message.session_id
        if hasattr(message, "result"):
            print("Turn 1 complete:", message.result[:200])

    # Turn 2: Use context from Turn 1 — "it" refers to the auth module
    async for message in query(
        prompt="Now find all places in the codebase that call it",
        options=ClaudeAgentOptions(
            resume=session_id,
            allowed_tools=["Read", "Glob", "Grep"],
        ),
    ):
        if hasattr(message, "result"):
            print("Turn 2 complete:", message.result[:200])

    # Turn 3: Build on accumulated context
    async for message in query(
        prompt="Which of those callers are missing error handling?",
        options=ClaudeAgentOptions(resume=session_id),
    ):
        if hasattr(message, "result"):
            print("Turn 3 complete:", message.result[:200])


asyncio.run(multi_turn_analysis())
```

## Session Persistence

- Sessions persist until cleanup (default: 30 days based on `cleanupPeriodDays` setting)
- Subagent transcripts are stored separately and persist within their session
- When the main conversation compacts, subagent transcripts are unaffected
- To track and revert file changes across sessions, see File Checkpointing

## ClaudeSDKClient for Continuous Conversations

For interactive, multi-turn applications where you need to maintain an open connection, use `ClaudeSDKClient` instead of `query()`. See [`02_python-reference.md`](02_python-reference.md) for full details.

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
import asyncio


async def main():
    async with ClaudeSDKClient() as client:
        # First question
        await client.query("What's the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up — Claude remembers the previous context
        await client.query("What's the population of that city?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


asyncio.run(main())
```

`ClaudeSDKClient` vs `query()`:

| Feature | `query()` | `ClaudeSDKClient` |
|---------|-----------|-------------------|
| Session | New each time | Reuses same session |
| Conversation | Single exchange | Multiple exchanges |
| Continue chat | New session | Maintains context |
| Interrupts | Not supported | Supported |
| Hooks | Not supported | Supported |
| Use case | One-off tasks | Continuous conversations |
