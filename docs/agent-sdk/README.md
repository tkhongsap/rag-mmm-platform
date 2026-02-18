# Claude Agent SDK — Reference Docs

Local reference for the Claude Agent SDK (formerly Claude Code SDK). These files were extracted from `platform.claude.com/docs/en/agent-sdk/` for offline use when building agentic features in the rag-mmm-platform.

## Files

| File | Topic | Key content |
|------|-------|-------------|
| [`00_overview.md`](00_overview.md) | Overview | Capabilities, built-in tools table, SDK vs Client SDK vs CLI comparison |
| [`01_quickstart.md`](01_quickstart.md) | Quickstart | Bug-fixing agent walkthrough, `query()` loop, permission modes primer |
| [`02_python-reference.md`](02_python-reference.md) | Python API | `query()`, `ClaudeSDKClient`, `ClaudeAgentOptions` full table, all types, errors, hooks, tool schemas |
| [`03_hooks.md`](03_hooks.md) | Hooks | `PreToolUse`/`PostToolUse` patterns, `HookMatcher`, block/allow/modify/redirect, security patterns |
| [`04_subagents.md`](04_subagents.md) | Subagents | `AgentDefinition`, parallel delegation, tool restrictions, dynamic factory pattern |
| [`05_sessions.md`](05_sessions.md) | Sessions | Session IDs, `resume`, `fork_session`, multi-turn workflows |

## Quick Reference

### Install

```bash
pip install claude-agent-sdk
```

### Minimal query

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Bash"],
            permission_mode="acceptEdits",
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

### Key `ClaudeAgentOptions` fields

| Field | Type | Notes |
|-------|------|-------|
| `allowed_tools` | `list[str]` | `["Read","Edit","Bash","Glob","Grep","Task",...]` |
| `permission_mode` | `str` | `"acceptEdits"` / `"bypassPermissions"` / `"default"` |
| `system_prompt` | `str` | Custom system instructions |
| `agents` | `dict[str, AgentDefinition]` | Subagent definitions |
| `hooks` | `dict[HookEvent, list[HookMatcher]]` | Lifecycle hooks |
| `resume` | `str` | Session ID to resume |
| `fork_session` | `bool` | Fork on resume (creates new session ID) |
| `max_turns` | `int` | Turn limit |
| `model` | `str` | Model override (e.g. `"claude-opus-4-6"`) |
| `cwd` | `str \| Path` | Working directory |
| `mcp_servers` | `dict` | MCP server configs |
| `setting_sources` | `list` | `["project"]` to load CLAUDE.md |

### Built-in tools

`Read` · `Write` · `Edit` · `Bash` · `Glob` · `Grep` · `WebSearch` · `WebFetch` · `Task` · `AskUserQuestion` · `NotebookEdit` · `TodoWrite` · `BashOutput` · `KillBash` · `ExitPlanMode` · `ListMcpResources` · `ReadMcpResource`

### Hook events (Python SDK)

`PreToolUse` · `PostToolUse` · `UserPromptSubmit` · `Stop` · `SubagentStop` · `PreCompact`

## Not yet fetched

- `/docs/en/agent-sdk/mcp` — MCP server integration
- `/docs/en/agent-sdk/permissions` — Permission modes in depth
- `/docs/en/agent-sdk/typescript` — TypeScript API reference
- `/docs/en/agent-sdk/user-input` — `AskUserQuestion` / approval flows
- `/docs/en/agent-sdk/migration-guide` — Claude Code SDK → Agent SDK migration
