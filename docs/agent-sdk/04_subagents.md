# Claude Agent SDK — Subagents

> Source: `platform.claude.com/docs/en/agent-sdk/subagents`

Subagents are separate agent instances that your main agent can spawn to handle focused subtasks. Use them to isolate context, run tasks in parallel, and apply specialized instructions without bloating the main agent's prompt.

## Overview

Three ways to create subagents:
1. **Programmatic** (recommended): use the `agents` parameter in `query()` options
2. **Filesystem-based**: define agents as markdown files in `.claude/agents/`
3. **Built-in general-purpose**: Claude can invoke the built-in `general-purpose` subagent via the Task tool without any definitions

Claude determines when to invoke a subagent based on its `description` field. You can also explicitly request one by name in your prompt.

## Benefits

### Context management

Subagents maintain separate context from the main agent, preventing information overload.

*Example*: a `research-assistant` subagent can explore dozens of files without cluttering the main conversation, returning only relevant findings.

### Parallelization

Multiple subagents can run concurrently, dramatically speeding up complex workflows.

*Example*: during a code review, run `style-checker`, `security-scanner`, and `test-coverage` subagents simultaneously.

### Specialized instructions

Each subagent can have tailored system prompts with specific expertise and constraints.

*Example*: a `database-migration` subagent with detailed knowledge about SQL best practices and rollback strategies.

### Tool restrictions

Subagents can be limited to specific tools, reducing risk of unintended actions.

*Example*: a `doc-reviewer` subagent with only `Read` and `Grep` — can analyze but never modify files.

## Creating subagents

### Programmatic definition

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Review the authentication module for security issues",
        options=ClaudeAgentOptions(
            # Task tool is required for subagent invocation
            allowed_tools=["Read", "Grep", "Glob", "Task"],
            agents={
                "code-reviewer": AgentDefinition(
                    # description tells Claude when to use this subagent
                    description="Expert code review specialist. Use for quality, security, and maintainability reviews.",
                    # prompt defines the subagent's role and behavior
                    prompt="""You are a code review specialist with expertise in security,
performance, and best practices.

When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards
- Suggest specific improvements

Be thorough but concise.""",
                    # tools restricts what the subagent can do
                    tools=["Read", "Grep", "Glob"],
                    # model overrides the default model
                    model="sonnet",
                ),
                "test-runner": AgentDefinition(
                    description="Runs and analyzes test suites. Use for test execution and coverage analysis.",
                    prompt="""You are a test execution specialist. Run tests and provide
clear analysis of results. Focus on running commands, analyzing output,
identifying failing tests, and suggesting fixes.""",
                    # Bash access lets this subagent run test commands
                    tools=["Bash", "Read", "Grep"],
                ),
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### `AgentDefinition` fields

| Field | Required | Description |
|:------|:---------|:------------|
| `description` | Yes | Natural language description of when to use this agent. Claude uses this to decide when to delegate. |
| `prompt` | Yes | The agent's system prompt defining its role and behavior |
| `tools` | No | Array of allowed tool names. If omitted, inherits all tools |
| `model` | No | `"sonnet"` \| `"opus"` \| `"haiku"` \| `"inherit"`. Defaults to main model. |

> **Note:** Subagents cannot spawn their own subagents. Do not include `Task` in a subagent's `tools` array.

## Invoking subagents

### Automatic invocation

Claude automatically invokes subagents based on task and `description`. Write clear, specific descriptions so Claude can match tasks to the right subagent.

### Explicit invocation

To guarantee a specific subagent is used, mention it by name in your prompt:

```text
"Use the code-reviewer agent to check the authentication module"
```

### Dynamic agent configuration (factory pattern)

Create agent definitions dynamically at runtime:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


def create_security_agent(security_level: str) -> AgentDefinition:
    is_strict = security_level == "strict"
    return AgentDefinition(
        description="Security code reviewer",
        prompt=f"You are a {'strict' if is_strict else 'balanced'} security reviewer. "
               "Identify vulnerabilities, check for injection risks, and flag unsafe patterns.",
        tools=["Read", "Grep", "Glob"],
        # Use a more capable model for high-stakes reviews
        model="opus" if is_strict else "sonnet",
    )


async def main():
    async for message in query(
        prompt="Review this PR for security issues",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob", "Task"],
            agents={
                "security-reviewer": create_security_agent("strict")
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)
```

## Detecting subagent invocation

Subagents are invoked via the Task tool. Messages from within a subagent's context include a `parent_tool_use_id` field:

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
                    description="Expert code reviewer.",
                    prompt="Analyze code quality and suggest improvements.",
                    tools=["Read", "Glob", "Grep"],
                )
            },
        ),
    ):
        # Check for subagent invocation in message content
        if hasattr(message, "content") and message.content:
            for block in message.content:
                if getattr(block, "type", None) == "tool_use" and block.name == "Task":
                    print(f"Subagent invoked: {block.input.get('subagent_type')}")

        # Check if this message is from within a subagent's context
        if hasattr(message, "parent_tool_use_id") and message.parent_tool_use_id:
            print("  (running inside subagent)")

        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

## Resuming subagents

Subagents can be resumed to continue where they left off. When a subagent completes, Claude receives its agent ID in the Task tool result.

```python
import asyncio
import json
import re
from claude_agent_sdk import query, ClaudeAgentOptions


def extract_agent_id(text: str) -> str | None:
    """Extract agentId from Task tool result text."""
    match = re.search(r"agentId:\s*([a-f0-9-]+)", text)
    return match.group(1) if match else None


async def main():
    agent_id = None
    session_id = None

    # First invocation
    async for message in query(
        prompt="Use the Explore agent to find all API endpoints in this codebase",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob", "Task"]),
    ):
        if hasattr(message, "session_id"):
            session_id = message.session_id
        if hasattr(message, "content"):
            content_str = json.dumps(message.content, default=str)
            extracted = extract_agent_id(content_str)
            if extracted:
                agent_id = extracted
        if hasattr(message, "result"):
            print(message.result)

    # Second invocation — resume the same session and ask follow-up
    if agent_id and session_id:
        async for message in query(
            prompt=f"Resume agent {agent_id} and list the top 3 most complex endpoints",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Grep", "Glob", "Task"],
                resume=session_id,
            ),
        ):
            if hasattr(message, "result"):
                print(message.result)


asyncio.run(main())
```

> You must resume the **same session** to access the subagent's transcript. Pass `resume=session_id` in options.

### Subagent transcript persistence

- Transcripts persist independently of the main conversation
- Main conversation compaction does **not** affect subagent transcripts
- Cleaned up based on `cleanupPeriodDays` setting (default: 30 days)

## Tool restrictions

| Use case | Tools | Description |
|:---------|:------|:------------|
| Read-only analysis | `Read`, `Grep`, `Glob` | Can examine code but not modify or execute |
| Test execution | `Bash`, `Read`, `Grep` | Can run commands and analyze output |
| Code modification | `Read`, `Edit`, `Write`, `Grep`, `Glob` | Full read/write, no commands |
| Full access | *(omit `tools` field)* | Inherits all tools from parent |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Claude not delegating | Include `Task` in `allowedTools`; use explicit name in prompt; write a clearer `description` |
| Filesystem agents not loading | `.claude/agents/` agents load at startup only — restart after adding new files |
| Windows long prompt failure | Keep prompts concise (command line limit: 8191 chars); use filesystem-based agents for long prompts |
