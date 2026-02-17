# Claude Agent SDK — Python API Reference

> Source: `platform.claude.com/docs/en/agent-sdk/python`

Complete API reference for the Python Agent SDK.

```bash
pip install claude-agent-sdk
```

## `query()` vs `ClaudeSDKClient`

| Feature | `query()` | `ClaudeSDKClient` |
|:--------|:----------|:------------------|
| Session | New each time | Reuses same session |
| Conversation | Single exchange | Multiple exchanges |
| Continue chat | New session | Maintains context |
| Interrupts | ❌ | ✅ |
| Hooks | ❌ | ✅ |
| Custom Tools | ❌ | ✅ |
| Use case | One-off tasks | Continuous conversations |

**Use `query()` for**: one-off questions, independent tasks, simple automation scripts, fresh-start each time.

**Use `ClaudeSDKClient` for**: continuing conversations, follow-up questions, interactive chat applications, response-driven logic, session lifecycle control.

---

## Functions

### `query()`

Creates a new session for each interaction. Returns an async iterator that yields messages as they arrive.

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None
) -> AsyncIterator[Message]
```

#### Parameters

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `prompt` | `str \| AsyncIterable[dict]` | Input prompt or async iterable for streaming mode |
| `options` | `ClaudeAgentOptions \| None` | Optional config (defaults to `ClaudeAgentOptions()` if None) |

#### Example

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",
        cwd="/home/user/project",
    )
    async for message in query(prompt="Create a Python web server", options=options):
        print(message)

asyncio.run(main())
```

---

### `tool()`

Decorator for defining MCP tools with type safety.

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any]
) -> Callable[..., SdkMcpTool[Any]]
```

#### Parameters

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `name` | `str` | Unique identifier for the tool |
| `description` | `str` | Human-readable description |
| `input_schema` | `type \| dict` | Input schema (simple type mapping or JSON Schema) |

**Simple type mapping** (recommended):
```python
{"text": str, "count": int, "enabled": bool}
```

**JSON Schema format** (for complex validation):
```python
{"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
```

#### Example

```python
from claude_agent_sdk import tool
from typing import Any

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

---

### `create_sdk_mcp_server()`

Create an in-process MCP server that runs within your Python application.

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

#### Example

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, query, ClaudeAgentOptions

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}

calculator = create_sdk_mcp_server(name="calculator", version="2.0.0", tools=[add])

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add"],
)
```

---

## Classes

### `ClaudeSDKClient`

Maintains a conversation session across multiple exchanges.

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def rewind_files(self, user_message_uuid: str) -> None
    async def disconnect(self) -> None
```

#### Methods

| Method | Description |
|:-------|:------------|
| `connect(prompt)` | Connect to Claude with optional initial prompt |
| `query(prompt)` | Send a new request in streaming mode |
| `receive_messages()` | Receive all messages as async iterator |
| `receive_response()` | Receive messages until and including a ResultMessage |
| `interrupt()` | Send interrupt signal (streaming mode only) |
| `rewind_files(uuid)` | Restore files to state at specified user message (requires `enable_file_checkpointing=True`) |
| `disconnect()` | Disconnect from Claude |

> **Important:** When iterating messages, avoid `break` to exit early — use flags to track when you've found what you need.

#### Example — Continuing a conversation

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    async with ClaudeSDKClient() as client:
        # First question
        await client.query("What's the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up — Claude remembers previous context
        await client.query("What's the population of that city?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(main())
```

#### Example — Advanced permission control

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny

async def custom_permission_handler(tool_name, input_data, context):
    # Block writes to system directories
    if tool_name == "Write" and input_data.get("file_path", "").startswith("/system/"):
        return PermissionResultDeny(
            message="System directory write not allowed", interrupt=True
        )
    # Redirect config file operations to sandbox
    if tool_name in ["Write", "Edit"] and "config" in input_data.get("file_path", ""):
        safe_path = f"./sandbox/{input_data['file_path']}"
        return PermissionResultAllow(
            updated_input={**input_data, "file_path": safe_path}
        )
    return PermissionResultAllow(updated_input=input_data)

async def main():
    options = ClaudeAgentOptions(
        can_use_tool=custom_permission_handler,
        allowed_tools=["Read", "Write", "Edit"],
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Update the system config file")
        async for message in client.receive_response():
            print(message)
```

---

## Types

### `ClaudeAgentOptions`

Configuration dataclass for Claude Code queries.

```python
@dataclass
class ClaudeAgentOptions:
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str | SystemPromptPreset | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)
    permission_mode: PermissionMode | None = None
    continue_conversation: bool = False
    resume: str | None = None
    fork_session: bool = False
    max_turns: int | None = None
    max_budget_usd: float | None = None
    disallowed_tools: list[str] = field(default_factory=list)
    enable_file_checkpointing: bool = False
    model: str | None = None
    fallback_model: str | None = None
    betas: list[SdkBeta] = field(default_factory=list)
    output_format: OutputFormat | None = None
    permission_prompt_tool_name: str | None = None
    cwd: str | Path | None = None
    cli_path: str | Path | None = None
    settings: str | None = None
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    stderr: Callable[[str], None] | None = None
    can_use_tool: CanUseTool | None = None
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    user: str | None = None
    include_partial_messages: bool = False
    agents: dict[str, AgentDefinition] | None = None
    setting_sources: list[SettingSource] | None = None
    max_thinking_tokens: int | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)
    sandbox: SandboxSettings | None = None
```

#### Full parameter table

| Property | Type | Default | Description |
|:---------|:-----|:--------|:------------|
| `tools` | `list[str] \| ToolsPreset \| None` | `None` | Tools config. Use `{"type":"preset","preset":"claude_code"}` for Claude Code defaults |
| `allowed_tools` | `list[str]` | `[]` | List of allowed tool names |
| `system_prompt` | `str \| SystemPromptPreset \| None` | `None` | System prompt. String for custom, or preset dict |
| `mcp_servers` | `dict[str, McpServerConfig] \| str \| Path` | `{}` | MCP server configs or path to config file |
| `permission_mode` | `PermissionMode \| None` | `None` | Permission mode for tool usage |
| `continue_conversation` | `bool` | `False` | Continue the most recent conversation |
| `resume` | `str \| None` | `None` | Session ID to resume |
| `fork_session` | `bool` | `False` | Fork to new session ID when resuming |
| `max_turns` | `int \| None` | `None` | Maximum conversation turns |
| `max_budget_usd` | `float \| None` | `None` | Maximum budget in USD |
| `disallowed_tools` | `list[str]` | `[]` | Tools to block |
| `enable_file_checkpointing` | `bool` | `False` | Track file changes for `rewind_files()` |
| `model` | `str \| None` | `None` | Claude model (e.g. `"claude-opus-4-6"`) |
| `fallback_model` | `str \| None` | `None` | Fallback if primary model fails |
| `betas` | `list[SdkBeta]` | `[]` | Beta features (e.g. `["context-1m-2025-08-07"]`) |
| `output_format` | `OutputFormat \| None` | `None` | Structured output config |
| `cwd` | `str \| Path \| None` | `None` | Working directory |
| `cli_path` | `str \| Path \| None` | `None` | Custom Claude Code CLI path |
| `add_dirs` | `list[str \| Path]` | `[]` | Additional accessible directories |
| `env` | `dict[str, str]` | `{}` | Environment variables |
| `extra_args` | `dict[str, str \| None]` | `{}` | Additional CLI arguments |
| `max_buffer_size` | `int \| None` | `None` | Max bytes when buffering CLI stdout |
| `stderr` | `Callable[[str], None] \| None` | `None` | Callback for stderr output |
| `can_use_tool` | `CanUseTool \| None` | `None` | Tool permission callback |
| `hooks` | `dict[HookEvent, list[HookMatcher]] \| None` | `None` | Hook configurations |
| `user` | `str \| None` | `None` | User identifier |
| `include_partial_messages` | `bool` | `False` | Include `StreamEvent` messages |
| `agents` | `dict[str, AgentDefinition] \| None` | `None` | Subagent definitions |
| `setting_sources` | `list[SettingSource] \| None` | `None` | Filesystem settings to load. **Omit** = no settings loaded |
| `max_thinking_tokens` | `int \| None` | `None` | Max tokens for thinking blocks |
| `plugins` | `list[SdkPluginConfig]` | `[]` | Local plugin configs |
| `sandbox` | `SandboxSettings \| None` | `None` | Sandbox behavior config |

---

### `AgentDefinition`

Configuration for a subagent defined programmatically.

```python
@dataclass
class AgentDefinition:
    description: str                # When to use this agent
    prompt: str                     # System prompt
    tools: list[str] | None = None  # Allowed tools (None = inherit all)
    model: Literal["sonnet", "opus", "haiku", "inherit"] | None = None
```

---

### `PermissionMode`

```python
PermissionMode = Literal[
    "default",            # Standard permission behavior
    "acceptEdits",        # Auto-accept file edits
    "plan",               # Planning mode — no execution
    "bypassPermissions",  # Bypass all checks (use with caution)
]
```

---

### `CanUseTool`

Type alias for tool permission callback functions.

```python
CanUseTool = Callable[
    [str, dict[str, Any], ToolPermissionContext], Awaitable[PermissionResult]
]
# (tool_name, input_data, context) -> PermissionResultAllow | PermissionResultDeny
```

---

### `PermissionResultAllow`

```python
@dataclass
class PermissionResultAllow:
    behavior: Literal["allow"] = "allow"
    updated_input: dict[str, Any] | None = None      # Modified input
    updated_permissions: list[PermissionUpdate] | None = None
```

### `PermissionResultDeny`

```python
@dataclass
class PermissionResultDeny:
    behavior: Literal["deny"] = "deny"
    message: str = ""          # Why the tool was denied
    interrupt: bool = False    # Whether to interrupt execution
```

---

### `SettingSource`

Controls which filesystem-based configuration sources to load.

```python
SettingSource = Literal["user", "project", "local"]
# "user"    → ~/.claude/settings.json
# "project" → .claude/settings.json (also loads CLAUDE.md)
# "local"   → .claude/settings.local.json
```

When `setting_sources` is **omitted or `None`**, no filesystem settings are loaded (isolation mode for SDK apps).

**Load CLAUDE.md project instructions:**
```python
options = ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"},
    setting_sources=["project"],  # Required to load CLAUDE.md
    allowed_tools=["Read", "Write", "Edit"],
)
```

**Settings precedence** (highest to lowest): local → project → user. Programmatic options always override filesystem settings.

---

### `SystemPromptPreset`

Use Claude Code's preset system prompt with optional additions.

```python
class SystemPromptPreset(TypedDict):
    type: Literal["preset"]
    preset: Literal["claude_code"]
    append: NotRequired[str]  # Additional instructions to append
```

---

### `OutputFormat`

Configuration for structured output validation.

```python
class OutputFormat(TypedDict):
    type: Literal["json_schema"]
    schema: dict[str, Any]  # JSON Schema definition
```

---

### `HookEvent`

Supported hook event types (Python SDK).

```python
HookEvent = Literal[
    "PreToolUse",       # Before tool execution (can block/modify)
    "PostToolUse",      # After tool execution
    "UserPromptSubmit", # When user submits a prompt
    "Stop",             # When stopping execution
    "SubagentStop",     # When a subagent stops
    "PreCompact",       # Before message compaction
]
```

> `SessionStart`, `SessionEnd`, and `Notification` are TypeScript-only.

### `HookMatcher`

```python
@dataclass
class HookMatcher:
    matcher: str | None = None         # Tool name pattern (e.g. "Bash", "Write|Edit")
    hooks: list[HookCallback] = field(default_factory=list)
    timeout: float | None = None       # Timeout in seconds (default: 60)
```

### `HookCallback`

```python
HookCallback = Callable[
    [dict[str, Any], str | None, HookContext], Awaitable[dict[str, Any]]
]
# (input_data, tool_use_id, context) -> response dict
```

### Hook Input Types

**`PreToolUseHookInput`**:
```python
class PreToolUseHookInput(BaseHookInput):
    hook_event_name: Literal["PreToolUse"]
    tool_name: str
    tool_input: dict[str, Any]
```

**`PostToolUseHookInput`**:
```python
class PostToolUseHookInput(BaseHookInput):
    hook_event_name: Literal["PostToolUse"]
    tool_name: str
    tool_input: dict[str, Any]
    tool_response: Any
```

**`UserPromptSubmitHookInput`**:
```python
class UserPromptSubmitHookInput(BaseHookInput):
    hook_event_name: Literal["UserPromptSubmit"]
    prompt: str
```

**`StopHookInput`**:
```python
class StopHookInput(BaseHookInput):
    hook_event_name: Literal["Stop"]
    stop_hook_active: bool
```

**`PreCompactHookInput`**:
```python
class PreCompactHookInput(BaseHookInput):
    hook_event_name: Literal["PreCompact"]
    trigger: Literal["manual", "auto"]
    custom_instructions: str | None
```

### `SyncHookJSONOutput`

Return value from hook callbacks:

```python
class SyncHookJSONOutput(TypedDict):
    continue_: NotRequired[bool]          # Proceed (default: True). Sent as "continue"
    suppressOutput: NotRequired[bool]     # Hide stdout from transcript
    stopReason: NotRequired[str]          # Message when continue is False
    decision: NotRequired[Literal["block"]]
    systemMessage: NotRequired[str]       # Warning message for user
    reason: NotRequired[str]              # Feedback for Claude
    hookSpecificOutput: NotRequired[dict[str, Any]]
```

> Use `continue_` (with underscore) in Python — it's converted to `continue` automatically.

---

## Message Types

### `Message` (union)

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent
```

### `AssistantMessage`

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
```

### `SystemMessage`

```python
@dataclass
class SystemMessage:
    subtype: str    # "init" for session start
    data: dict[str, Any]
```

### `ResultMessage`

```python
@dataclass
class ResultMessage:
    subtype: str           # "success" or "error"
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
    structured_output: Any = None
```

### `StreamEvent`

Only received when `include_partial_messages=True`.

```python
@dataclass
class StreamEvent:
    uuid: str
    session_id: str
    event: dict[str, Any]            # Raw Anthropic API stream event
    parent_tool_use_id: str | None = None  # Set if from within a subagent
```

---

## Content Block Types

```python
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

```python
@dataclass
class TextBlock:
    text: str

@dataclass
class ThinkingBlock:
    thinking: str
    signature: str

@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]

@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None
```

---

## Error Types

```python
class ClaudeSDKError(Exception): ...          # Base exception
class CLIConnectionError(ClaudeSDKError): ... # Connection failed

class CLINotFoundError(CLIConnectionError):
    def __init__(self, message="Claude Code not found", cli_path=None): ...

class ProcessError(ClaudeSDKError):
    exit_code: int | None
    stderr: str | None

class CLIJSONDecodeError(ClaudeSDKError):
    line: str            # The line that failed to parse
    original_error: Exception
```

### Error handling example

```python
from claude_agent_sdk import query, CLINotFoundError, ProcessError, CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print("Please install Claude Code: npm install -g @anthropic-ai/claude-code")
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except CLIJSONDecodeError as e:
    print(f"Failed to parse response: {e}")
```

---

## Tool Input/Output Schemas

Schemas for built-in Claude Code tools (structure of `tool_input` / `tool_response` in messages).

### Task

**Input:**
```python
{"description": str, "prompt": str, "subagent_type": str}
```

**Output:**
```python
{"result": str, "usage": dict | None, "total_cost_usd": float | None, "duration_ms": int | None}
```

### Bash

**Input:**
```python
{
    "command": str,
    "timeout": int | None,          # Max 600000 ms
    "description": str | None,
    "run_in_background": bool | None,
}
```

**Output:**
```python
{"output": str, "exitCode": int, "killed": bool | None, "shellId": str | None}
```

### Edit

**Input:**
```python
{"file_path": str, "old_string": str, "new_string": str, "replace_all": bool | None}
```

**Output:**
```python
{"message": str, "replacements": int, "file_path": str}
```

### Read

**Input:**
```python
{"file_path": str, "offset": int | None, "limit": int | None}
```

**Output (text):**
```python
{"content": str, "total_lines": int, "lines_returned": int}
```

**Output (image):**
```python
{"image": str, "mime_type": str, "file_size": int}
```

### Write

**Input:**
```python
{"file_path": str, "content": str}
```

**Output:**
```python
{"message": str, "bytes_written": int, "file_path": str}
```

### Glob

**Input:**
```python
{"pattern": str, "path": str | None}
```

**Output:**
```python
{"matches": list[str], "count": int, "search_path": str}
```

### Grep

**Input:**
```python
{
    "pattern": str,
    "path": str | None,
    "glob": str | None,
    "type": str | None,
    "output_mode": str | None,  # "content" | "files_with_matches" | "count"
    "-i": bool | None,
    "-n": bool | None,
    "-B": int | None,
    "-A": int | None,
    "-C": int | None,
    "head_limit": int | None,
    "multiline": bool | None,
}
```

### WebSearch

**Input:**
```python
{
    "query": str,
    "allowed_domains": list[str] | None,
    "blocked_domains": list[str] | None,
}
```

**Output:**
```python
{
    "results": [{"title": str, "url": str, "snippet": str, "metadata": dict | None}],
    "total_results": int,
    "query": str,
}
```

### WebFetch

**Input:**
```python
{"url": str, "prompt": str}
```

**Output:**
```python
{"response": str, "url": str, "final_url": str | None, "status_code": int | None}
```

### AskUserQuestion

**Input:**
```python
{
    "questions": [
        {
            "question": str,
            "header": str,           # Max 12 chars
            "options": [{"label": str, "description": str}],  # 2-4 options
            "multiSelect": bool,
        }
    ],
    "answers": dict | None,
}
```

**Output:**
```python
{"questions": [...], "answers": dict[str, str]}
# Multi-select answers are comma-separated
```

### NotebookEdit

**Input:**
```python
{
    "notebook_path": str,
    "cell_id": str | None,
    "new_source": str,
    "cell_type": "code" | "markdown" | None,
    "edit_mode": "replace" | "insert" | "delete" | None,
}
```

---

## MCP Server Configs

```python
# Stdio (most common)
class McpStdioServerConfig(TypedDict):
    command: str
    args: NotRequired[list[str]]
    env: NotRequired[dict[str, str]]

# SSE
class McpSSEServerConfig(TypedDict):
    type: Literal["sse"]
    url: str
    headers: NotRequired[dict[str, str]]

# HTTP
class McpHttpServerConfig(TypedDict):
    type: Literal["http"]
    url: str
    headers: NotRequired[dict[str, str]]
```

### SDK MCP server (in-process)

```python
class McpSdkServerConfig(TypedDict):
    type: Literal["sdk"]
    name: str
    instance: Any  # MCP Server instance from create_sdk_mcp_server()
```

---

## Sandbox Settings

Configure command execution sandboxing:

```python
class SandboxSettings(TypedDict, total=False):
    enabled: bool                             # Enable sandbox mode
    autoAllowBashIfSandboxed: bool            # Auto-approve bash in sandboxed mode
    excludedCommands: list[str]               # Commands that always bypass sandbox
    allowUnsandboxedCommands: bool            # Allow model to request sandbox bypass
    network: SandboxNetworkConfig
    ignoreViolations: SandboxIgnoreViolations
    enableWeakerNestedSandbox: bool
```

```python
class SandboxNetworkConfig(TypedDict, total=False):
    allowLocalBinding: bool        # Allow binding to local ports
    allowUnixSockets: list[str]    # Allowed Unix socket paths
    allowAllUnixSockets: bool
    httpProxyPort: int
    socksProxyPort: int
```

> **Note:** Filesystem and network access restrictions are NOT in sandbox settings — use permission rules instead.

---

## Advanced Examples

### Continuous conversation interface

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
import asyncio


async def chat_session():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits",
    )
    async with ClaudeSDKClient(options=options) as client:
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            await client.query(user_input)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Claude: {block.text}")

asyncio.run(chat_session())
```

### Hooks with ClaudeSDKClient

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher
import asyncio


async def pre_tool_logger(input_data, tool_use_id, context):
    print(f"[PRE-TOOL] {input_data.get('tool_name')}")
    if "rm -rf" in str(input_data.get("tool_input", {})):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Dangerous command blocked",
            }
        }
    return {}


async def main():
    options = ClaudeAgentOptions(
        hooks={"PreToolUse": [HookMatcher(hooks=[pre_tool_logger])]},
        allowed_tools=["Read", "Write", "Bash"],
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query("List files in current directory")
        async for message in client.receive_response():
            pass

asyncio.run(main())
```
