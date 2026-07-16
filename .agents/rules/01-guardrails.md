---
description: "Strict behavioral guardrails for safety and iteration limits."
alwaysApply: true
---

# Agent Iteration & Safety Guardrails

- **Strict Iteration Limit:** You are permitted a maximum of 3 tool calls to
  solve a problem. If tests/linters fail after 3 attempts, you MUST stop
  execution, summarize the failure, and wait for human input. Do NOT attempt a
  4th fix.
- **No Blind Retries:** If a tool call fails, do NOT immediately retry with the
  exact same arguments. Change your approach or ask the user.
- **Destructive Action Halt:** NEVER run `rm -rf`, `git reset --hard`, or drop
  database tables without explicit user confirmation.
- **No Git Operations:** Do not use `git` to sync or commit changes unless
  explicitly told to. The human is the final QC step.
