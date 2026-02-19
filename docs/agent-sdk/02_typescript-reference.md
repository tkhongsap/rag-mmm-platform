# Agent SDK Reference -- TypeScript

> Source: `platform.claude.com/docs/en/agent-sdk/typescript`

Complete API reference for the TypeScript Agent SDK, including all functions, types, and interfaces.

---

> **Try the new V2 interface (preview):** A simplified interface with `send()` and `receive()` patterns is now available, making multi-turn conversations easier. [Learn more about the TypeScript V2 preview](/docs/en/agent-sdk/typescript-v2-preview)

## Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

## Functions

### `query()`

The primary function for interacting with Claude Code. Creates an async generator that streams messages as they arrive.

```typescript
function query({
  prompt,
  options
}: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): Query
```

#### Parameters

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| `prompt` | `string \| AsyncIterable<SDKUserMessage>` | The input prompt as a string or async iterable for streaming mode |
| `options` | `Options` | Optional configuration object (see Options type below) |

#### Returns

Returns a `Query` object that extends `AsyncGenerator<SDKMessage, void>` with additional methods.

### `tool()`

Creates a type-safe MCP tool definition for use with SDK MCP servers.

```typescript
function tool<Schema extends ZodRawShape>(
  name: string,
  description: string,
  inputSchema: Schema,
  handler: (args: z.infer<ZodObject<Schema>>, extra: unknown) => Promise<CallToolResult>
): SdkMcpToolDefinition<Schema>
```

#### Parameters

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| `name` | `string` | The name of the tool |
| `description` | `string` | A description of what the tool does |
| `inputSchema` | `Schema extends ZodRawShape` | Zod schema defining the tool's input parameters |
| `handler` | `(args, extra) => Promise<CallToolResult>` | Async function that executes the tool logic |

### `createSdkMcpServer()`

Creates an MCP server instance that runs in the same process as your application.

```typescript
function createSdkMcpServer(options: {
  name: string;
  version?: string;
  tools?: Array<SdkMcpToolDefinition<any>>;
}): McpSdkServerConfigWithInstance
```

#### Parameters

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| `options.name` | `string` | The name of the MCP server |
| `options.version` | `string` | Optional version string |
| `options.tools` | `Array<SdkMcpToolDefinition>` | Array of tool definitions created with `tool()` |

## Types

### `Options`

Configuration object for the `query()` function.

| Property | Type | Default | Description |
| :------- | :--- | :------ | :---------- |
| `abortController` | `AbortController` | `new AbortController()` | Controller for cancelling operations |
| `additionalDirectories` | `string[]` | `[]` | Additional directories Claude can access |
| `agents` | `Record<string, AgentDefinition>` | `undefined` | Programmatically define subagents |
| `allowDangerouslySkipPermissions` | `boolean` | `false` | Enable bypassing permissions. Required when using `permissionMode: 'bypassPermissions'` |
| `allowedTools` | `string[]` | All tools | List of allowed tool names |
| `betas` | `SdkBeta[]` | `[]` | Enable beta features (e.g., `['context-1m-2025-08-07']`) |
| `canUseTool` | `CanUseTool` | `undefined` | Custom permission function for tool usage |
| `continue` | `boolean` | `false` | Continue the most recent conversation |
| `cwd` | `string` | `process.cwd()` | Current working directory |
| `disallowedTools` | `string[]` | `[]` | List of disallowed tool names |
| `enableFileCheckpointing` | `boolean` | `false` | Enable file change tracking for rewinding. See [File checkpointing](/docs/en/agent-sdk/file-checkpointing) |
| `env` | `Dict<string>` | `process.env` | Environment variables |
| `executable` | `'bun' \| 'deno' \| 'node'` | Auto-detected | JavaScript runtime to use |
| `executableArgs` | `string[]` | `[]` | Arguments to pass to the executable |
| `extraArgs` | `Record<string, string \| null>` | `{}` | Additional arguments |
| `fallbackModel` | `string` | `undefined` | Model to use if primary fails |
| `forkSession` | `boolean` | `false` | When resuming with `resume`, fork to a new session ID instead of continuing the original session |
| `hooks` | `Partial<Record<HookEvent, HookCallbackMatcher[]>>` | `{}` | Hook callbacks for events |
| `includePartialMessages` | `boolean` | `false` | Include partial message events |
| `maxBudgetUsd` | `number` | `undefined` | Maximum budget in USD for the query |
| `maxThinkingTokens` | `number` | `undefined` | Maximum tokens for thinking process |
| `maxTurns` | `number` | `undefined` | Maximum conversation turns |
| `mcpServers` | `Record<string, McpServerConfig>` | `{}` | MCP server configurations |
| `model` | `string` | Default from CLI | Claude model to use |
| `outputFormat` | `{ type: 'json_schema', schema: JSONSchema }` | `undefined` | Define output format for agent results. See [Structured outputs](/docs/en/agent-sdk/structured-outputs) for details |
| `pathToClaudeCodeExecutable` | `string` | Uses built-in executable | Path to Claude Code executable |
| `permissionMode` | `PermissionMode` | `'default'` | Permission mode for the session |
| `permissionPromptToolName` | `string` | `undefined` | MCP tool name for permission prompts |
| `plugins` | `SdkPluginConfig[]` | `[]` | Load custom plugins from local paths. See [Plugins](/docs/en/agent-sdk/plugins) for details |
| `resume` | `string` | `undefined` | Session ID to resume |
| `resumeSessionAt` | `string` | `undefined` | Resume session at a specific message UUID |
| `sandbox` | `SandboxSettings` | `undefined` | Configure sandbox behavior programmatically. See [Sandbox settings](#sandboxsettings) for details |
| `settingSources` | `SettingSource[]` | `[]` (no settings) | Control which filesystem settings to load. When omitted, no settings are loaded. **Note:** Must include `'project'` to load CLAUDE.md files |
| `stderr` | `(data: string) => void` | `undefined` | Callback for stderr output |
| `strictMcpConfig` | `boolean` | `false` | Enforce strict MCP validation |
| `systemPrompt` | `string \| { type: 'preset'; preset: 'claude_code'; append?: string }` | `undefined` (minimal prompt) | System prompt configuration. Pass a string for custom prompt, or `{ type: 'preset', preset: 'claude_code' }` to use Claude Code's system prompt. When using the preset object form, add `append` to extend the system prompt with additional instructions |
| `tools` | `string[] \| { type: 'preset'; preset: 'claude_code' }` | `undefined` | Tool configuration. Pass an array of tool names or use the preset to get Claude Code's default tools |

### `Query`

Interface returned by the `query()` function.

```typescript
interface Query extends AsyncGenerator<SDKMessage, void> {
  interrupt(): Promise<void>;
  rewindFiles(userMessageUuid: string): Promise<void>;
  setPermissionMode(mode: PermissionMode): Promise<void>;
  setModel(model?: string): Promise<void>;
  setMaxThinkingTokens(maxThinkingTokens: number | null): Promise<void>;
  supportedCommands(): Promise<SlashCommand[]>;
  supportedModels(): Promise<ModelInfo[]>;
  mcpServerStatus(): Promise<McpServerStatus[]>;
  accountInfo(): Promise<AccountInfo>;
}
```

#### Methods

| Method | Description |
| :----- | :---------- |
| `interrupt()` | Interrupts the query (only available in streaming input mode) |
| `rewindFiles(userMessageUuid)` | Restores files to their state at the specified user message. Requires `enableFileCheckpointing: true`. See [File checkpointing](/docs/en/agent-sdk/file-checkpointing) |
| `setPermissionMode()` | Changes the permission mode (only available in streaming input mode) |
| `setModel()` | Changes the model (only available in streaming input mode) |
| `setMaxThinkingTokens()` | Changes the maximum thinking tokens (only available in streaming input mode) |
| `supportedCommands()` | Returns available slash commands |
| `supportedModels()` | Returns available models with display info |
| `mcpServerStatus()` | Returns status of connected MCP servers |
| `accountInfo()` | Returns account information |

### `AgentDefinition`

Configuration for a subagent defined programmatically.

```typescript
type AgentDefinition = {
  description: string;
  tools?: string[];
  prompt: string;
  model?: "sonnet" | "opus" | "haiku" | "inherit";
}
```

| Field | Required | Description |
|:------|:---------|:------------|
| `description` | Yes | Natural language description of when to use this agent |
| `tools` | No | Array of allowed tool names. If omitted, inherits all tools |
| `prompt` | Yes | The agent's system prompt |
| `model` | No | Model override for this agent. If omitted, uses the main model |

### `SettingSource`

Controls which filesystem-based configuration sources the SDK loads settings from.

```typescript
type SettingSource = "user" | "project" | "local";
```

| Value | Description | Location |
|:------|:------------|:---------|
| `'user'` | Global user settings | `~/.claude/settings.json` |
| `'project'` | Shared project settings (version controlled) | `.claude/settings.json` |
| `'local'` | Local project settings (gitignored) | `.claude/settings.local.json` |

#### Default behavior

When `settingSources` is **omitted** or **undefined**, the SDK does **not** load any filesystem settings. This provides isolation for SDK applications.

#### Why use settingSources?

**Load all filesystem settings (legacy behavior):**

```typescript
// Load all settings like SDK v0.0.x did
const result = query({
  prompt: "Analyze this code",
  options: {
    settingSources: ["user", "project", "local"] // Load all settings
  }
});
```

**Load only specific setting sources:**

```typescript
// Load only project settings, ignore user and local
const result = query({
  prompt: "Run CI checks",
  options: {
    settingSources: ["project"] // Only .claude/settings.json
  }
});
```

**Testing and CI environments:**

```typescript
// Ensure consistent behavior in CI by excluding local settings
const result = query({
  prompt: "Run tests",
  options: {
    settingSources: ["project"], // Only team-shared settings
    permissionMode: "bypassPermissions"
  }
});
```

**SDK-only applications:**

```typescript
// Define everything programmatically (default behavior)
// No filesystem dependencies - settingSources defaults to []
const result = query({
  prompt: "Review this PR",
  options: {
    // settingSources: [] is the default, no need to specify
    agents: { /* ... */ },
    mcpServers: { /* ... */ },
    allowedTools: ["Read", "Grep", "Glob"]
  }
});
```

**Loading CLAUDE.md project instructions:**

```typescript
// Load project settings to include CLAUDE.md files
const result = query({
  prompt: "Add a new feature following project conventions",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code" // Required to use CLAUDE.md
    },
    settingSources: ["project"], // Loads CLAUDE.md from project directory
    allowedTools: ["Read", "Write", "Edit"]
  }
});
```

#### Settings precedence

When multiple sources are loaded, settings are merged with this precedence (highest to lowest):

1. Local settings (`.claude/settings.local.json`)
2. Project settings (`.claude/settings.json`)
3. User settings (`~/.claude/settings.json`)

Programmatic options (like `agents`, `allowedTools`) always override filesystem settings.

### `PermissionMode`

```typescript
type PermissionMode =
  | "default" // Standard permission behavior
  | "acceptEdits" // Auto-accept file edits
  | "bypassPermissions" // Bypass all permission checks
  | "plan" // Planning mode - no execution
```

### `CanUseTool`

Custom permission function type for controlling tool usage.

```typescript
type CanUseTool = (
  toolName: string,
  input: ToolInput,
  options: {
    signal: AbortSignal;
    suggestions?: PermissionUpdate[];
  }
) => Promise<PermissionResult>;
```

### `PermissionResult`

Result of a permission check.

```typescript
type PermissionResult =
  | {
      behavior: "allow";
      updatedInput: ToolInput;
      updatedPermissions?: PermissionUpdate[];
    }
  | {
      behavior: "deny";
      message: string;
      interrupt?: boolean;
    }
```

### `McpServerConfig`

Configuration for MCP servers.

```typescript
type McpServerConfig =
  | McpStdioServerConfig
  | McpSSEServerConfig
  | McpHttpServerConfig
  | McpSdkServerConfigWithInstance;
```

#### `McpStdioServerConfig`

```typescript
type McpStdioServerConfig = {
  type?: "stdio";
  command: string;
  args?: string[];
  env?: Record<string, string>;
}
```

#### `McpSSEServerConfig`

```typescript
type McpSSEServerConfig = {
  type: "sse";
  url: string;
  headers?: Record<string, string>;
}
```

#### `McpHttpServerConfig`

```typescript
type McpHttpServerConfig = {
  type: "http";
  url: string;
  headers?: Record<string, string>;
}
```

#### `McpSdkServerConfigWithInstance`

```typescript
type McpSdkServerConfigWithInstance = {
  type: "sdk";
  name: string;
  instance: McpServer;
}
```

### `SdkPluginConfig`

Configuration for loading plugins in the SDK.

```typescript
type SdkPluginConfig = {
  type: "local";
  path: string;
}
```

| Field | Type | Description |
|:------|:-----|:------------|
| `type` | `'local'` | Must be `'local'` (only local plugins currently supported) |
| `path` | `string` | Absolute or relative path to the plugin directory |

**Example:**

```typescript
plugins: [
  { type: "local", path: "./my-plugin" },
  { type: "local", path: "/absolute/path/to/plugin" }
];
```

For complete information on creating and using plugins, see [Plugins](/docs/en/agent-sdk/plugins).

## Message Types

### `SDKMessage`

Union type of all possible messages returned by the query.

```typescript
type SDKMessage =
  | SDKAssistantMessage
  | SDKUserMessage
  | SDKUserMessageReplay
  | SDKResultMessage
  | SDKSystemMessage
  | SDKPartialAssistantMessage
  | SDKCompactBoundaryMessage;
```

### `SDKAssistantMessage`

Assistant response message.

```typescript
type SDKAssistantMessage = {
  type: "assistant";
  uuid: UUID;
  session_id: string;
  message: APIAssistantMessage; // From Anthropic SDK
  parent_tool_use_id: string | null;
}
```

### `SDKUserMessage`

User input message.

```typescript
type SDKUserMessage = {
  type: "user";
  uuid?: UUID;
  session_id: string;
  message: APIUserMessage; // From Anthropic SDK
  parent_tool_use_id: string | null;
}
```

### `SDKUserMessageReplay`

Replayed user message with required UUID.

```typescript
type SDKUserMessageReplay = {
  type: "user";
  uuid: UUID;
  session_id: string;
  message: APIUserMessage;
  parent_tool_use_id: string | null;
}
```

### `SDKResultMessage`

Final result message.

```typescript
type SDKResultMessage =
  | {
      type: "result";
      subtype: "success";
      uuid: UUID;
      session_id: string;
      duration_ms: number;
      duration_api_ms: number;
      is_error: boolean;
      num_turns: number;
      result: string;
      total_cost_usd: number;
      usage: NonNullableUsage;
      modelUsage: { [modelName: string]: ModelUsage };
      permission_denials: SDKPermissionDenial[];
      structured_output?: unknown;
    }
  | {
      type: "result";
      subtype:
        | "error_max_turns"
        | "error_during_execution"
        | "error_max_budget_usd"
        | "error_max_structured_output_retries";
      uuid: UUID;
      session_id: string;
      duration_ms: number;
      duration_api_ms: number;
      is_error: boolean;
      num_turns: number;
      total_cost_usd: number;
      usage: NonNullableUsage;
      modelUsage: { [modelName: string]: ModelUsage };
      permission_denials: SDKPermissionDenial[];
      errors: string[];
    }
```

### `SDKSystemMessage`

System initialization message.

```typescript
type SDKSystemMessage = {
  type: "system";
  subtype: "init";
  uuid: UUID;
  session_id: string;
  apiKeySource: ApiKeySource;
  cwd: string;
  tools: string[];
  mcp_servers: {
    name: string;
    status: string;
  }[];
  model: string;
  permissionMode: PermissionMode;
  slash_commands: string[];
  output_style: string;
}
```

### `SDKPartialAssistantMessage`

Streaming partial message (only when `includePartialMessages` is true).

```typescript
type SDKPartialAssistantMessage = {
  type: "stream_event";
  event: RawMessageStreamEvent; // From Anthropic SDK
  parent_tool_use_id: string | null;
  uuid: UUID;
  session_id: string;
}
```

### `SDKCompactBoundaryMessage`

Message indicating a conversation compaction boundary.

```typescript
type SDKCompactBoundaryMessage = {
  type: "system";
  subtype: "compact_boundary";
  uuid: UUID;
  session_id: string;
  compact_metadata: {
    trigger: "manual" | "auto";
    pre_tokens: number;
  };
}
```

### `SDKPermissionDenial`

Information about a denied tool use.

```typescript
type SDKPermissionDenial = {
  tool_name: string;
  tool_use_id: string;
  tool_input: ToolInput;
}
```

## Hook Types

For a comprehensive guide on using hooks with examples and common patterns, see the [Hooks guide](/docs/en/agent-sdk/hooks).

### `HookEvent`

Available hook events.

```typescript
type HookEvent =
  | "PreToolUse"
  | "PostToolUse"
  | "PostToolUseFailure"
  | "Notification"
  | "UserPromptSubmit"
  | "SessionStart"
  | "SessionEnd"
  | "Stop"
  | "SubagentStart"
  | "SubagentStop"
  | "PreCompact"
  | "PermissionRequest";
```

### `HookCallback`

Hook callback function type.

```typescript
type HookCallback = (
  input: HookInput, // Union of all hook input types
  toolUseID: string | undefined,
  options: { signal: AbortSignal }
) => Promise<HookJSONOutput>;
```

### `HookCallbackMatcher`

Hook configuration with optional matcher.

```typescript
interface HookCallbackMatcher {
  matcher?: string;
  hooks: HookCallback[];
}
```

### `HookInput`

Union type of all hook input types.

```typescript
type HookInput =
  | PreToolUseHookInput
  | PostToolUseHookInput
  | PostToolUseFailureHookInput
  | NotificationHookInput
  | UserPromptSubmitHookInput
  | SessionStartHookInput
  | SessionEndHookInput
  | StopHookInput
  | SubagentStartHookInput
  | SubagentStopHookInput
  | PreCompactHookInput
  | PermissionRequestHookInput;
```

### `BaseHookInput`

Base interface that all hook input types extend.

```typescript
type BaseHookInput = {
  session_id: string;
  transcript_path: string;
  cwd: string;
  permission_mode?: string;
}
```

#### `PreToolUseHookInput`

```typescript
type PreToolUseHookInput = BaseHookInput & {
  hook_event_name: "PreToolUse";
  tool_name: string;
  tool_input: unknown;
}
```

#### `PostToolUseHookInput`

```typescript
type PostToolUseHookInput = BaseHookInput & {
  hook_event_name: "PostToolUse";
  tool_name: string;
  tool_input: unknown;
  tool_response: unknown;
}
```

#### `PostToolUseFailureHookInput`

```typescript
type PostToolUseFailureHookInput = BaseHookInput & {
  hook_event_name: "PostToolUseFailure";
  tool_name: string;
  tool_input: unknown;
  error: string;
  is_interrupt?: boolean;
}
```

#### `NotificationHookInput`

```typescript
type NotificationHookInput = BaseHookInput & {
  hook_event_name: "Notification";
  message: string;
  title?: string;
}
```

#### `UserPromptSubmitHookInput`

```typescript
type UserPromptSubmitHookInput = BaseHookInput & {
  hook_event_name: "UserPromptSubmit";
  prompt: string;
}
```

#### `SessionStartHookInput`

```typescript
type SessionStartHookInput = BaseHookInput & {
  hook_event_name: "SessionStart";
  source: "startup" | "resume" | "clear" | "compact";
}
```

#### `SessionEndHookInput`

```typescript
type SessionEndHookInput = BaseHookInput & {
  hook_event_name: "SessionEnd";
  reason: ExitReason; // String from EXIT_REASONS array
}
```

#### `StopHookInput`

```typescript
type StopHookInput = BaseHookInput & {
  hook_event_name: "Stop";
  stop_hook_active: boolean;
}
```

#### `SubagentStartHookInput`

```typescript
type SubagentStartHookInput = BaseHookInput & {
  hook_event_name: "SubagentStart";
  agent_id: string;
  agent_type: string;
}
```

#### `SubagentStopHookInput`

```typescript
type SubagentStopHookInput = BaseHookInput & {
  hook_event_name: "SubagentStop";
  stop_hook_active: boolean;
}
```

#### `PreCompactHookInput`

```typescript
type PreCompactHookInput = BaseHookInput & {
  hook_event_name: "PreCompact";
  trigger: "manual" | "auto";
  custom_instructions: string | null;
}
```

#### `PermissionRequestHookInput`

```typescript
type PermissionRequestHookInput = BaseHookInput & {
  hook_event_name: "PermissionRequest";
  tool_name: string;
  tool_input: unknown;
  permission_suggestions?: PermissionUpdate[];
}
```

### `HookJSONOutput`

Hook return value.

```typescript
type HookJSONOutput = AsyncHookJSONOutput | SyncHookJSONOutput;
```

#### `AsyncHookJSONOutput`

```typescript
type AsyncHookJSONOutput = {
  async: true;
  asyncTimeout?: number;
}
```

#### `SyncHookJSONOutput`

```typescript
type SyncHookJSONOutput = {
  continue?: boolean;
  suppressOutput?: boolean;
  stopReason?: string;
  decision?: "approve" | "block";
  systemMessage?: string;
  reason?: string;
  hookSpecificOutput?:
    | {
        hookEventName: "PreToolUse";
        permissionDecision?: "allow" | "deny" | "ask";
        permissionDecisionReason?: string;
        updatedInput?: Record<string, unknown>;
      }
    | {
        hookEventName: "UserPromptSubmit";
        additionalContext?: string;
      }
    | {
        hookEventName: "SessionStart";
        additionalContext?: string;
      }
    | {
        hookEventName: "PostToolUse";
        additionalContext?: string;
      };
}
```

## Tool Input Types

Documentation of input schemas for all built-in Claude Code tools. These types are exported from `@anthropic-ai/claude-agent-sdk` and can be used for type-safe tool interactions.

### `ToolInput`

**Note:** This is a documentation-only type for clarity. It represents the union of all tool input types.

```typescript
type ToolInput =
  | AgentInput
  | AskUserQuestionInput
  | BashInput
  | BashOutputInput
  | FileEditInput
  | FileReadInput
  | FileWriteInput
  | GlobInput
  | GrepInput
  | KillShellInput
  | NotebookEditInput
  | WebFetchInput
  | WebSearchInput
  | TodoWriteInput
  | ExitPlanModeInput
  | ListMcpResourcesInput
  | ReadMcpResourceInput;
```

### Task

**Tool name:** `Task`

```typescript
interface AgentInput {
  description: string;   // A short (3-5 word) description of the task
  prompt: string;        // The task for the agent to perform
  subagent_type: string; // The type of specialized agent to use for this task
}
```

Launches a new agent to handle complex, multi-step tasks autonomously.

### AskUserQuestion

**Tool name:** `AskUserQuestion`

```typescript
interface AskUserQuestionInput {
  questions: Array<{
    question: string;    // The complete question to ask the user
    header: string;      // Very short label displayed as a chip/tag (max 12 chars)
    options: Array<{
      label: string;       // Display text for this option (1-5 words)
      description: string; // Explanation of what this option means
    }>;
    multiSelect: boolean; // Set to true to allow multiple selections
  }>;
  answers?: Record<string, string>; // User answers populated by the permission system
}
```

Asks the user clarifying questions during execution. See [Handle approvals and user input](/docs/en/agent-sdk/user-input#handle-clarifying-questions) for usage details.

### Bash

**Tool name:** `Bash`

```typescript
interface BashInput {
  command: string;            // The command to execute
  timeout?: number;           // Optional timeout in milliseconds (max 600000)
  description?: string;       // Clear, concise description (5-10 words)
  run_in_background?: boolean; // Set to true to run in background
}
```

Executes bash commands in a persistent shell session with optional timeout and background execution.

### BashOutput

**Tool name:** `BashOutput`

```typescript
interface BashOutputInput {
  bash_id: string;   // The ID of the background shell to retrieve output from
  filter?: string;   // Optional regex to filter output lines
}
```

Retrieves output from a running or completed background bash shell.

### Edit

**Tool name:** `Edit`

```typescript
interface FileEditInput {
  file_path: string;      // The absolute path to the file to modify
  old_string: string;     // The text to replace
  new_string: string;     // The text to replace it with (must be different from old_string)
  replace_all?: boolean;  // Replace all occurrences of old_string (default false)
}
```

Performs exact string replacements in files.

### Read

**Tool name:** `Read`

```typescript
interface FileReadInput {
  file_path: string; // The absolute path to the file to read
  offset?: number;   // The line number to start reading from
  limit?: number;    // The number of lines to read
}
```

Reads files from the local filesystem, including text, images, PDFs, and Jupyter notebooks.

### Write

**Tool name:** `Write`

```typescript
interface FileWriteInput {
  file_path: string; // The absolute path to the file to write
  content: string;   // The content to write to the file
}
```

Writes a file to the local filesystem, overwriting if it exists.

### Glob

**Tool name:** `Glob`

```typescript
interface GlobInput {
  pattern: string; // The glob pattern to match files against
  path?: string;   // The directory to search in (defaults to cwd)
}
```

Fast file pattern matching that works with any codebase size.

### Grep

**Tool name:** `Grep`

```typescript
interface GrepInput {
  pattern: string;                                          // The regular expression pattern to search for
  path?: string;                                            // File or directory to search in (defaults to cwd)
  glob?: string;                                            // Glob pattern to filter files (e.g. "*.js")
  type?: string;                                            // File type to search (e.g. "js", "py", "rust")
  output_mode?: "content" | "files_with_matches" | "count"; // Output mode
  "-i"?: boolean;                                           // Case insensitive search
  "-n"?: boolean;                                           // Show line numbers (for content mode)
  "-B"?: number;                                            // Lines to show before each match
  "-A"?: number;                                            // Lines to show after each match
  "-C"?: number;                                            // Lines to show before and after each match
  head_limit?: number;                                      // Limit output to first N lines/entries
  multiline?: boolean;                                      // Enable multiline mode
}
```

Powerful search tool built on ripgrep with regex support.

### KillBash

**Tool name:** `KillBash`

```typescript
interface KillShellInput {
  shell_id: string; // The ID of the background shell to kill
}
```

Kills a running background bash shell by its ID.

### NotebookEdit

**Tool name:** `NotebookEdit`

```typescript
interface NotebookEditInput {
  notebook_path: string;                          // The absolute path to the Jupyter notebook file
  cell_id?: string;                               // The ID of the cell to edit
  new_source: string;                             // The new source for the cell
  cell_type?: "code" | "markdown";                // The type of the cell (code or markdown)
  edit_mode?: "replace" | "insert" | "delete";    // The type of edit (replace, insert, delete)
}
```

Edits cells in Jupyter notebook files.

### WebFetch

**Tool name:** `WebFetch`

```typescript
interface WebFetchInput {
  url: string;    // The URL to fetch content from
  prompt: string; // The prompt to run on the fetched content
}
```

Fetches content from a URL and processes it with an AI model.

### WebSearch

**Tool name:** `WebSearch`

```typescript
interface WebSearchInput {
  query: string;                  // The search query to use
  allowed_domains?: string[];     // Only include results from these domains
  blocked_domains?: string[];     // Never include results from these domains
}
```

Searches the web and returns formatted results.

### TodoWrite

**Tool name:** `TodoWrite`

```typescript
interface TodoWriteInput {
  todos: Array<{
    content: string;                                  // The task description
    status: "pending" | "in_progress" | "completed";  // The task status
    activeForm: string;                               // Active form of the task description
  }>;
}
```

Creates and manages a structured task list for tracking progress.

### ExitPlanMode

**Tool name:** `ExitPlanMode`

```typescript
interface ExitPlanModeInput {
  plan: string; // The plan to run by the user for approval
}
```

Exits planning mode and prompts the user to approve the plan.

### ListMcpResources

**Tool name:** `ListMcpResources`

```typescript
interface ListMcpResourcesInput {
  server?: string; // Optional server name to filter resources by
}
```

Lists available MCP resources from connected servers.

### ReadMcpResource

**Tool name:** `ReadMcpResource`

```typescript
interface ReadMcpResourceInput {
  server: string; // The MCP server name
  uri: string;    // The resource URI to read
}
```

Reads a specific MCP resource from a server.

## Tool Output Types

Documentation of output schemas for all built-in Claude Code tools. These types represent the actual response data returned by each tool.

### `ToolOutput`

**Note:** This is a documentation-only type for clarity. It represents the union of all tool output types.

```typescript
type ToolOutput =
  | TaskOutput
  | AskUserQuestionOutput
  | BashOutput
  | BashOutputToolOutput
  | EditOutput
  | ReadOutput
  | WriteOutput
  | GlobOutput
  | GrepOutput
  | KillBashOutput
  | NotebookEditOutput
  | WebFetchOutput
  | WebSearchOutput
  | TodoWriteOutput
  | ExitPlanModeOutput
  | ListMcpResourcesOutput
  | ReadMcpResourceOutput;
```

### Task Output

**Tool name:** `Task`

```typescript
interface TaskOutput {
  result: string;        // Final result message from the subagent
  usage?: {
    input_tokens: number;
    output_tokens: number;
    cache_creation_input_tokens?: number;
    cache_read_input_tokens?: number;
  };
  total_cost_usd?: number;  // Total cost in USD
  duration_ms?: number;      // Execution duration in milliseconds
}
```

### AskUserQuestion Output

**Tool name:** `AskUserQuestion`

```typescript
interface AskUserQuestionOutput {
  questions: Array<{
    question: string;
    header: string;
    options: Array<{ label: string; description: string }>;
    multiSelect: boolean;
  }>;
  answers: Record<string, string>; // Maps question text to answer string
}
```

### Bash Output

**Tool name:** `Bash`

```typescript
interface BashOutput {
  output: string;      // Combined stdout and stderr output
  exitCode: number;    // Exit code of the command
  killed?: boolean;    // Whether the command was killed due to timeout
  shellId?: string;    // Shell ID for background processes
}
```

### BashOutput Tool Output

**Tool name:** `BashOutput`

```typescript
interface BashOutputToolOutput {
  output: string;                              // New output since last check
  status: "running" | "completed" | "failed";  // Current shell status
  exitCode?: number;                           // Exit code (when completed)
}
```

### Edit Output

**Tool name:** `Edit`

```typescript
interface EditOutput {
  message: string;      // Confirmation message
  replacements: number; // Number of replacements made
  file_path: string;    // File path that was edited
}
```

### Read Output

**Tool name:** `Read`

```typescript
type ReadOutput = TextFileOutput | ImageFileOutput | PDFFileOutput | NotebookFileOutput;

interface TextFileOutput {
  content: string;       // File contents with line numbers
  total_lines: number;   // Total number of lines in file
  lines_returned: number; // Lines actually returned
}

interface ImageFileOutput {
  image: string;     // Base64 encoded image data
  mime_type: string; // Image MIME type
  file_size: number; // File size in bytes
}

interface PDFFileOutput {
  pages: Array<{
    page_number: number;
    text?: string;
    images?: Array<{ image: string; mime_type: string }>;
  }>;
  total_pages: number; // Total number of pages
}

interface NotebookFileOutput {
  cells: Array<{
    cell_type: "code" | "markdown";
    source: string;
    outputs?: any[];
    execution_count?: number;
  }>;
  metadata?: Record<string, any>; // Notebook metadata
}
```

### Write Output

**Tool name:** `Write`

```typescript
interface WriteOutput {
  message: string;       // Success message
  bytes_written: number; // Number of bytes written
  file_path: string;     // File path that was written
}
```

### Glob Output

**Tool name:** `Glob`

```typescript
interface GlobOutput {
  matches: string[];    // Array of matching file paths
  count: number;        // Number of matches found
  search_path: string;  // Search directory used
}
```

### Grep Output

**Tool name:** `Grep`

```typescript
type GrepOutput = GrepContentOutput | GrepFilesOutput | GrepCountOutput;

interface GrepContentOutput {
  matches: Array<{
    file: string;
    line_number?: number;
    line: string;
    before_context?: string[];
    after_context?: string[];
  }>;
  total_matches: number; // Total number of matches
}

interface GrepFilesOutput {
  files: string[]; // Files containing matches
  count: number;   // Number of files with matches
}

interface GrepCountOutput {
  counts: Array<{ file: string; count: number }>;
  total: number; // Total matches across all files
}
```

### KillBash Output

**Tool name:** `KillBash`

```typescript
interface KillBashOutput {
  message: string;  // Success message
  shell_id: string; // ID of the killed shell
}
```

### NotebookEdit Output

**Tool name:** `NotebookEdit`

```typescript
interface NotebookEditOutput {
  message: string;                                 // Success message
  edit_type: "replaced" | "inserted" | "deleted";  // Type of edit performed
  cell_id?: string;                                // Cell ID that was affected
  total_cells: number;                             // Total cells in notebook after edit
}
```

### WebFetch Output

**Tool name:** `WebFetch`

```typescript
interface WebFetchOutput {
  response: string;     // AI model's response to the prompt
  url: string;          // URL that was fetched
  final_url?: string;   // Final URL after redirects
  status_code?: number; // HTTP status code
}
```

### WebSearch Output

**Tool name:** `WebSearch`

```typescript
interface WebSearchOutput {
  results: Array<{
    title: string;
    url: string;
    snippet: string;
    metadata?: Record<string, any>;
  }>;
  total_results: number; // Total number of results
  query: string;         // The query that was searched
}
```

### TodoWrite Output

**Tool name:** `TodoWrite`

```typescript
interface TodoWriteOutput {
  message: string; // Success message
  stats: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
  };
}
```

### ExitPlanMode Output

**Tool name:** `ExitPlanMode`

```typescript
interface ExitPlanModeOutput {
  message: string;    // Confirmation message
  approved?: boolean; // Whether user approved the plan
}
```

### ListMcpResources Output

**Tool name:** `ListMcpResources`

```typescript
interface ListMcpResourcesOutput {
  resources: Array<{
    uri: string;
    name: string;
    description?: string;
    mimeType?: string;
    server: string;
  }>;
  total: number; // Total number of resources
}
```

### ReadMcpResource Output

**Tool name:** `ReadMcpResource`

```typescript
interface ReadMcpResourceOutput {
  contents: Array<{
    uri: string;
    mimeType?: string;
    text?: string;
    blob?: string;
  }>;
  server: string; // Server that provided the resource
}
```

## Permission Types

### `PermissionUpdate`

Operations for updating permissions.

```typescript
type PermissionUpdate =
  | {
      type: "addRules";
      rules: PermissionRuleValue[];
      behavior: PermissionBehavior;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "replaceRules";
      rules: PermissionRuleValue[];
      behavior: PermissionBehavior;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "removeRules";
      rules: PermissionRuleValue[];
      behavior: PermissionBehavior;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "setMode";
      mode: PermissionMode;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "addDirectories";
      directories: string[];
      destination: PermissionUpdateDestination;
    }
  | {
      type: "removeDirectories";
      directories: string[];
      destination: PermissionUpdateDestination;
    }
```

### `PermissionBehavior`

```typescript
type PermissionBehavior = "allow" | "deny" | "ask";
```

### `PermissionUpdateDestination`

```typescript
type PermissionUpdateDestination =
  | "userSettings"    // Global user settings
  | "projectSettings" // Per-directory project settings
  | "localSettings"   // Gitignored local settings
  | "session"         // Current session only
```

### `PermissionRuleValue`

```typescript
type PermissionRuleValue = {
  toolName: string;
  ruleContent?: string;
}
```

## Other Types

### `ApiKeySource`

```typescript
type ApiKeySource = "user" | "project" | "org" | "temporary";
```

### `SdkBeta`

Available beta features that can be enabled via the `betas` option. See [Beta headers](/docs/en/api/beta-headers) for more information.

```typescript
type SdkBeta = "context-1m-2025-08-07";
```

| Value | Description | Compatible Models |
|:------|:------------|:------------------|
| `'context-1m-2025-08-07'` | Enables 1 million token context window | Claude Opus 4.6, Claude Sonnet 4.5, Claude Sonnet 4 |

### `SlashCommand`

Information about an available slash command.

```typescript
type SlashCommand = {
  name: string;
  description: string;
  argumentHint: string;
}
```

### `ModelInfo`

Information about an available model.

```typescript
type ModelInfo = {
  value: string;
  displayName: string;
  description: string;
}
```

### `McpServerStatus`

Status of a connected MCP server.

```typescript
type McpServerStatus = {
  name: string;
  status: "connected" | "failed" | "needs-auth" | "pending";
  serverInfo?: {
    name: string;
    version: string;
  };
}
```

### `AccountInfo`

Account information for the authenticated user.

```typescript
type AccountInfo = {
  email?: string;
  organization?: string;
  subscriptionType?: string;
  tokenSource?: string;
  apiKeySource?: string;
}
```

### `ModelUsage`

Per-model usage statistics returned in result messages.

```typescript
type ModelUsage = {
  inputTokens: number;
  outputTokens: number;
  cacheReadInputTokens: number;
  cacheCreationInputTokens: number;
  webSearchRequests: number;
  costUSD: number;
  contextWindow: number;
}
```

### `ConfigScope`

```typescript
type ConfigScope = "local" | "user" | "project";
```

### `NonNullableUsage`

A version of `Usage` with all nullable fields made non-nullable.

```typescript
type NonNullableUsage = {
  [K in keyof Usage]: NonNullable<Usage[K]>;
}
```

### `Usage`

Token usage statistics (from `@anthropic-ai/sdk`).

```typescript
type Usage = {
  input_tokens: number | null;
  output_tokens: number | null;
  cache_creation_input_tokens?: number | null;
  cache_read_input_tokens?: number | null;
}
```

### `CallToolResult`

MCP tool result type (from `@modelcontextprotocol/sdk/types.js`).

```typescript
type CallToolResult = {
  content: Array<{
    type: "text" | "image" | "resource";
    // Additional fields vary by type
  }>;
  isError?: boolean;
}
```

### `AbortError`

Custom error class for abort operations.

```typescript
class AbortError extends Error {}
```

## Sandbox Configuration

### `SandboxSettings`

Configuration for sandbox behavior. Use this to enable command sandboxing and configure network restrictions programmatically.

```typescript
type SandboxSettings = {
  enabled?: boolean;
  autoAllowBashIfSandboxed?: boolean;
  excludedCommands?: string[];
  allowUnsandboxedCommands?: boolean;
  network?: NetworkSandboxSettings;
  ignoreViolations?: SandboxIgnoreViolations;
  enableWeakerNestedSandbox?: boolean;
}
```

| Property | Type | Default | Description |
| :------- | :--- | :------ | :---------- |
| `enabled` | `boolean` | `false` | Enable sandbox mode for command execution |
| `autoAllowBashIfSandboxed` | `boolean` | `false` | Auto-approve bash commands when sandbox is enabled |
| `excludedCommands` | `string[]` | `[]` | Commands that always bypass sandbox restrictions (e.g., `['docker']`). These run unsandboxed automatically without model involvement |
| `allowUnsandboxedCommands` | `boolean` | `false` | Allow the model to request running commands outside the sandbox. When `true`, the model can set `dangerouslyDisableSandbox` in tool input, which falls back to the permissions system |
| `network` | `NetworkSandboxSettings` | `undefined` | Network-specific sandbox configuration |
| `ignoreViolations` | `SandboxIgnoreViolations` | `undefined` | Configure which sandbox violations to ignore |
| `enableWeakerNestedSandbox` | `boolean` | `false` | Enable a weaker nested sandbox for compatibility |

> **Note:** Filesystem and network access restrictions are NOT configured via sandbox settings. Instead, they are derived from permission rules:
> - **Filesystem read restrictions**: Read deny rules
> - **Filesystem write restrictions**: Edit allow/deny rules
> - **Network restrictions**: WebFetch allow/deny rules
>
> Use sandbox settings for command execution sandboxing, and permission rules for filesystem and network access control.

#### Example usage

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const result = await query({
  prompt: "Build and test my project",
  options: {
    sandbox: {
      enabled: true,
      autoAllowBashIfSandboxed: true,
      network: {
        allowLocalBinding: true
      }
    }
  }
});
```

> **Warning:** The `allowUnixSockets` option can grant access to powerful system services. For example, allowing `/var/run/docker.sock` effectively grants full host system access through the Docker API, bypassing sandbox isolation. Only allow Unix sockets that are strictly necessary and understand the security implications of each.

### `NetworkSandboxSettings`

Network-specific configuration for sandbox mode.

```typescript
type NetworkSandboxSettings = {
  allowLocalBinding?: boolean;
  allowUnixSockets?: string[];
  allowAllUnixSockets?: boolean;
  httpProxyPort?: number;
  socksProxyPort?: number;
}
```

| Property | Type | Default | Description |
| :------- | :--- | :------ | :---------- |
| `allowLocalBinding` | `boolean` | `false` | Allow processes to bind to local ports (e.g., for dev servers) |
| `allowUnixSockets` | `string[]` | `[]` | Unix socket paths that processes can access (e.g., Docker socket) |
| `allowAllUnixSockets` | `boolean` | `false` | Allow access to all Unix sockets |
| `httpProxyPort` | `number` | `undefined` | HTTP proxy port for network requests |
| `socksProxyPort` | `number` | `undefined` | SOCKS proxy port for network requests |

### `SandboxIgnoreViolations`

Configuration for ignoring specific sandbox violations.

```typescript
type SandboxIgnoreViolations = {
  file?: string[];
  network?: string[];
}
```

| Property | Type | Default | Description |
| :------- | :--- | :------ | :---------- |
| `file` | `string[]` | `[]` | File path patterns to ignore violations for |
| `network` | `string[]` | `[]` | Network patterns to ignore violations for |

### Permissions Fallback for Unsandboxed Commands

When `allowUnsandboxedCommands` is enabled, the model can request to run commands outside the sandbox by setting `dangerouslyDisableSandbox: true` in the tool input. These requests fall back to the existing permissions system, meaning your `canUseTool` handler will be invoked, allowing you to implement custom authorization logic.

> **Note:** `excludedCommands` vs `allowUnsandboxedCommands`:
> - `excludedCommands`: A static list of commands that always bypass the sandbox automatically (e.g., `['docker']`). The model has no control over this.
> - `allowUnsandboxedCommands`: Lets the model decide at runtime whether to request unsandboxed execution by setting `dangerouslyDisableSandbox: true` in the tool input.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const result = await query({
  prompt: "Deploy my application",
  options: {
    sandbox: {
      enabled: true,
      allowUnsandboxedCommands: true // Model can request unsandboxed execution
    },
    permissionMode: "default",
    canUseTool: async (tool, input) => {
      // Check if the model is requesting to bypass the sandbox
      if (tool === "Bash" && input.dangerouslyDisableSandbox) {
        // The model wants to run this command outside the sandbox
        console.log(`Unsandboxed command requested: ${input.command}`);

        // Return true to allow, false to deny
        return isCommandAuthorized(input.command);
      }
      return true;
    }
  }
});
```

> **Warning:** Commands running with `dangerouslyDisableSandbox: true` have full system access. Ensure your `canUseTool` handler validates these requests carefully.
>
> If `permissionMode` is set to `bypassPermissions` and `allowUnsandboxedCommands` is enabled, the model can autonomously execute commands outside the sandbox without any approval prompts. This combination effectively allows the model to escape sandbox isolation silently.

## See also

- [SDK overview](/docs/en/agent-sdk/overview) - General SDK concepts
- [Python SDK reference](/docs/en/agent-sdk/python) - Python SDK documentation
- [CLI reference](https://code.claude.com/docs/en/cli-reference) - Command-line interface
- [Common workflows](https://code.claude.com/docs/en/common-workflows) - Step-by-step guides
