# I-Form Invenio Repository - AGENTS.md

## Project Identity

- **Goal:** Manage a customized Invenio RDM instance for I-Form research.
- **Scale:** High-volume data, extreme reconfigurability.
- **Tech Stack:** Invenio RDM, Python, OCI-compliant (Docker/Podman).

## Core Principles

1. **Human-in-the-Loop:** Do not perform git commits or destructive database
   actions without explicit human approval.
2. **Deterministic Tooling:** Always prefer `uv` for environment management.
3. **Safety First:** If a tool/command fails, stop and report. Do not blindly
   retry.
4. **Tool Integrity:** Use `sequential-thinking` for planning and `LSP`
   (ruff/typescript) for validation.

## Records

- All agent logs must be synced to `agents/history.md`.
- All handoffs must be documented in `agents/handoff.md`.
