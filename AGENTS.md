# AGENTS.md — zarai-marketplace (repo root)

## What this repository is

PUBLIC-FACING GitHub repository of ZARAI-AI. Only publication-grade, export-appropriate, domain-general artifacts belong here. See README.md publication bar. This directory lives nested inside `~/.agents` but is an INDEPENDENT git repository (excluded from dot-agents tracking via its whitelist `.gitignore`).

## Laws for any agent working here

1. ITAR discernment before every commit: judge file CONTENT, not metadata. Anything defense-relevant, patent-pending-internal, workstation-specific, or client-confidential is forbidden in this repo. In doubt = do not add; ask kaptain.
2. This file and every child AGENTS.md are APPEND-ONLY: add your contribution under a dated header; never compress, reorder, or overwrite existing recorded state.
3. Every directory added to this repo receives a child AGENTS.md (DOX convention) stating its purpose and contract.
4. Backups are git: commit + push; roll back via history. No duplicate-file backups.

## Directory index

- `emergent-behaviors/apex-agents/setup/hooks/` — the zarai-ai-epic-apex-hooks series: session-lifecycle hooks encoding apex operating doctrine. See its child AGENTS.md.

## History

- 2026-07-13 — repo founded by fable (Claude Code) on kaptain's directive; initial artifact: hook-00 (must-do-asap-tasks session-start surfacing hook).
