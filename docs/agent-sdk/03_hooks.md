# Claude Agent SDK — Hooks

> Source: `platform.claude.com/docs/en/agent-sdk/hooks`

Hooks intercept agent execution at key points to add validation, logging, security controls, or custom logic.

Use hooks to:
- **Block dangerous operations** before they execute (destructive shell commands, unauthorized file access)
- **Log and audit** every tool call for compliance, debugging, or analytics
- **Transform inputs and outputs** to sanitize data, inject credentials, or redirect file paths
- **Require human approval** for sensitive actions (database writes, API calls)
- **Track session lifecycle** to manage state, clean up resources, or send notifications

## Anatomy of a hook

A hook has two parts:
1. **The callback function**: logic that runs when the hook fires
2. **The hook configuration**: specifies which event and which tools to match

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


# 1. Define the callback
async def protect_env_files(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")
    if file_path.split("/")[-1] == ".env":
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }
    return {}


async def main():
    # 2. Register the hook in options
    async for message in query(
        prompt="Update the database configuration",
        options=ClaudeAgentOptions(
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])
                ]
            }
        ),
    ):
        print(message)


asyncio.run(main())
```

## Available hooks

| Hook Event | Python SDK | TypeScript SDK | Trigger | Example use case |
|------------|:----------:|:--------------:|---------|------------------|
| `PreToolUse` | ✅ | ✅ | Tool call request | Block dangerous shell commands |
| `PostToolUse` | ✅ | ✅ | Tool execution result | Log all file changes to audit trail |
| `PostToolUseFailure` | ❌ | ✅ | Tool execution failure | Handle or log tool errors |
| `UserPromptSubmit` | ✅ | ✅ | User prompt submission | Inject additional context |
| `Stop` | ✅ | ✅ | Agent execution stop | Save session state before exit |
| `SubagentStart` | ❌ | ✅ | Subagent initialization | Track parallel task spawning |
| `SubagentStop` | ✅ | ✅ | Subagent completion | Aggregate results |
| `PreCompact` | ✅ | ✅ | Conversation compaction | Archive full transcript |
| `PermissionRequest` | ❌ | ✅ | Permission dialog | Custom permission handling |
| `SessionStart` | ❌ | ✅ | Session initialization | Initialize logging |
| `SessionEnd` | ❌ | ✅ | Session termination | Clean up resources |
| `Notification` | ❌ | ✅ | Agent status messages | Forward to Slack/PagerDuty |

## Configure hooks

Pass hooks in `options.hooks` when calling `query()`:

```python
options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_callback])]}
)
```

The `hooks` dict:
- **Keys**: hook event names (`"PreToolUse"`, `"PostToolUse"`, `"Stop"`, etc.)
- **Values**: arrays of `HookMatcher` objects

## Matchers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `matcher` | `str` | `None` | Regex pattern to match tool names |
| `hooks` | `list[HookCallback]` | — | Required. Callback functions |
| `timeout` | `float` | `60` | Timeout in seconds |

Built-in tool names: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebFetch`, `Task`, etc.
MCP tools follow pattern: `mcp__<server>__<action>`

Matchers only filter by **tool name**, not by file paths or other arguments. To filter by file path, check `tool_input.file_path` inside your callback.

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Write|Edit|Delete", hooks=[file_security_hook]),
            HookMatcher(matcher="^mcp__", hooks=[mcp_audit_hook]),
            HookMatcher(hooks=[global_logger]),  # No matcher → all tools
        ]
    }
)
```

## Callback function inputs

Every hook callback receives:
1. **`input_data`** (`dict`): event details
2. **`tool_use_id`** (`str | None`): correlate `PreToolUse` and `PostToolUse` events
3. **`context`** (`HookContext`): reserved for future use in Python

### Common fields (all hook types)

| Field | Type | Description |
|-------|------|-------------|
| `hook_event_name` | `str` | `"PreToolUse"`, `"PostToolUse"`, etc. |
| `session_id` | `str` | Current session identifier |
| `transcript_path` | `str` | Path to conversation transcript |
| `cwd` | `str` | Current working directory |

### Hook-specific fields

| Field | Type | Description | Hooks |
|-------|------|-------------|-------|
| `tool_name` | `str` | Name of the tool | PreToolUse, PostToolUse |
| `tool_input` | `dict` | Arguments passed to the tool | PreToolUse, PostToolUse |
| `tool_response` | `any` | Result from tool execution | PostToolUse |
| `prompt` | `str` | The user's prompt text | UserPromptSubmit |
| `stop_hook_active` | `bool` | Whether a stop hook is active | Stop, SubagentStop |
| `trigger` | `str` | `"manual"` or `"auto"` | PreCompact |
| `custom_instructions` | `str` | Instructions for compaction | PreCompact |

## Callback outputs

Return an empty `{}` to allow the operation. To block, modify, or add context, return an object:

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `continue` | `bool` | Whether agent should continue (default: `True`) |
| `stopReason` | `str` | Message when `continue` is `False` |
| `suppressOutput` | `bool` | Hide stdout from transcript |
| `systemMessage` | `str` | Message injected into conversation for Claude to see |

### Fields inside `hookSpecificOutput`

| Field | Type | Hooks | Description |
|-------|------|-------|-------------|
| `hookEventName` | `str` | All | Required. Use `input_data["hook_event_name"]` |
| `permissionDecision` | `"allow"` \| `"deny"` \| `"ask"` | PreToolUse | Controls whether tool executes |
| `permissionDecisionReason` | `str` | PreToolUse | Explanation shown to Claude |
| `updatedInput` | `dict` | PreToolUse | Modified tool input (requires `permissionDecision: "allow"`) |
| `additionalContext` | `str` | PreToolUse, PostToolUse, UserPromptSubmit | Context added to conversation |

### Permission decision flow

1. **Deny** rules checked first — any match → immediate denial
2. **Ask** rules checked second
3. **Allow** rules checked third
4. **Default to Ask** if nothing matches

## Common patterns

### Block dangerous commands

```python
async def block_dangerous_commands(input_data, tool_use_id, context):
    command = input_data["tool_input"].get("command", "")
    if "rm -rf /" in command:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Dangerous command blocked: rm -rf /",
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_dangerous_commands])]}
)
```

### Redirect file operations to sandbox

```python
async def redirect_to_sandbox(input_data, tool_use_id, context):
    if input_data["tool_name"] == "Write":
        original_path = input_data["tool_input"].get("file_path", "")
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "updatedInput": {
                    **input_data["tool_input"],
                    "file_path": f"/sandbox{original_path}",
                },
            }
        }
    return {}
```

> When using `updatedInput`, you must also include `permissionDecision: "allow"`. Always return a new dict rather than mutating the original.

### Inject context (system message)

```python
async def add_security_reminder(input_data, tool_use_id, context):
    return {"systemMessage": "Remember to follow security best practices."}
```

### Auto-approve read-only tools

```python
async def auto_approve_read_only(input_data, tool_use_id, context):
    read_only_tools = ["Read", "Glob", "Grep"]
    if input_data["tool_name"] in read_only_tools:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "permissionDecisionReason": "Read-only tool auto-approved",
            }
        }
    return {}
```

### Audit log (PostToolUse)

```python
from datetime import datetime

async def audit_logger(input_data, tool_use_id, context):
    with open("audit.log", "a") as f:
        f.write(
            f"{datetime.now().isoformat()} | {input_data['tool_name']} | "
            f"input={input_data['tool_input']}\n"
        )
    return {}

options = ClaudeAgentOptions(
    hooks={"PostToolUse": [HookMatcher(hooks=[audit_logger])]}
)
```

### Chaining multiple hooks

Hooks execute in array order. Keep each hook focused on a single responsibility:

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[rate_limiter]),         # First: check rate limits
            HookMatcher(hooks=[authorization_check]),  # Second: verify permissions
            HookMatcher(hooks=[input_sanitizer]),      # Third: sanitize inputs
            HookMatcher(hooks=[audit_logger]),         # Last: log the action
        ]
    }
)
```

### Async hook with external request

```python
import aiohttp
from datetime import datetime

async def webhook_notifier(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "PostToolUse":
        return {}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "https://api.example.com/webhook",
                json={
                    "tool": input_data["tool_name"],
                    "timestamp": datetime.now().isoformat(),
                },
            )
    except Exception as e:
        print(f"Webhook failed: {e}")
    return {}
```

### Track subagent activity

```python
async def subagent_tracker(input_data, tool_use_id, context):
    print(f"[SUBAGENT] Completed — tool_use_id={tool_use_id}")
    return {}

options = ClaudeAgentOptions(
    hooks={"SubagentStop": [HookMatcher(hooks=[subagent_tracker])]}
)
```

## Full example: security + audit

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, HookContext
from typing import Any


async def validate_bash_command(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    if input_data["tool_name"] == "Bash":
        command = input_data["tool_input"].get("command", "")
        if "rm -rf /" in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Dangerous command blocked",
                }
            }
    return {}


async def log_tool_use(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    print(f"Tool used: {input_data.get('tool_name')}")
    return {}


options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[validate_bash_command], timeout=120),
            HookMatcher(hooks=[log_tool_use]),  # All tools
        ],
        "PostToolUse": [HookMatcher(hooks=[log_tool_use])],
    }
)
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Hook not firing | Check event name is case-correct (`PreToolUse`, not `preToolUse`); verify matcher pattern |
| Matcher not filtering | Matchers only match tool names, not arguments — check `tool_input.file_path` inside the callback |
| Hook timeout | Increase `timeout` in `HookMatcher` |
| Tool blocked unexpectedly | Check all `PreToolUse` hooks for `"deny"` returns; add logging to see `permissionDecisionReason` |
| `updatedInput` not applied | Must be inside `hookSpecificOutput` with `permissionDecision: "allow"` |
| Session hooks not available | `SessionStart`, `SessionEnd`, `Notification` are TypeScript-only |
| Recursive loop with subagents | `UserPromptSubmit` hook spawning subagents can loop — check `parent_tool_use_id` to detect subagent context |
