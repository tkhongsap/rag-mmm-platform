# Claude Agent SDK — Reference Docs

Local reference for the Claude Agent SDK (formerly Claude Code SDK). These files were extracted from `platform.claude.com/docs/en/agent-sdk/` for offline use when building agentic features in the rag-mmm-platform.

## Files

| # | File | Topic | Key content |
|---|------|-------|-------------|
| 00 | [`00_overview.md`](00_overview.md) | Overview | Capabilities, built-in tools table, SDK vs Client SDK vs CLI comparison |
| 01 | [`01_quickstart.md`](01_quickstart.md) | Quickstart | Bug-fixing agent walkthrough, `query()` loop, permission modes primer |
| 02 | [`02_typescript-reference.md`](02_typescript-reference.md) | TypeScript API | Full TypeScript API reference, types, interfaces, options |
| 03 | [`03_python-reference.md`](03_python-reference.md) | Python API | `query()`, `ClaudeSDKClient`, `ClaudeAgentOptions` full table, all types, errors, hooks, tool schemas |
| 04 | [`04_hooks.md`](04_hooks.md) | Hooks | `PreToolUse`/`PostToolUse` patterns, `HookMatcher`, block/allow/modify/redirect, security patterns |
| 05 | [`05_subagents.md`](05_subagents.md) | Subagents | `AgentDefinition`, parallel delegation, tool restrictions, dynamic factory pattern |
| 06 | [`06_sessions.md`](06_sessions.md) | Sessions | Session IDs, `resume`, `fork_session`, multi-turn workflows |
| 07 | [`07_mcp.md`](07_mcp.md) | MCP | MCP server integration, transport types, tool naming, authentication, examples |
| 08 | [`08_permissions.md`](08_permissions.md) | Permissions | Permission modes (`default`, `acceptEdits`, `bypassPermissions`, `plan`), evaluation order |
| 09 | [`09_skills.md`](09_skills.md) | Skills | SKILL.md format, auto-discovery, model-invoked skills, tool restrictions |
| 10 | [`10_slash-commands.md`](10_slash-commands.md) | Slash Commands | Built-in commands, custom commands, frontmatter, arguments, subdirectory namespacing |
| 11 | [`11_system-prompts.md`](11_system-prompts.md) | System Prompts | CLAUDE.md files, output styles, `systemPrompt` append, custom system prompts |
| 12 | [`12_plugins.md`](12_plugins.md) | Plugins | Loading plugins, plugin structure, commands/agents/skills/hooks via plugins |
| 13 | [`13_user-input.md`](13_user-input.md) | User Input | `AskUserQuestion`, tool approval flows, approve/reject/modify responses |
| 14 | [`14_migration-guide.md`](14_migration-guide.md) | Migration | Claude Code SDK → Agent SDK rename, breaking changes, step-by-step migration |

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
