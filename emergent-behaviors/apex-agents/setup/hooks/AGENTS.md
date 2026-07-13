# AGENTS.md — apex-agents setup hooks (child)

Parent domain doc: `~/.agents/hooks/AGENTS.md` (the hooks-domain project root). Repo-root doc: `../../../../AGENTS.md`.

## Purpose

The **zarai-ai-epic-apex-hooks series**: numbered session-lifecycle hook scripts that inject standing operational doctrine into AI agent sessions. Numbering: `hook-00` fires first (must-do-asap task surfacing); higher numbers reserved for later lifecycle stages.

## Contract for hooks in this series

- Silent-fail on every filesystem error — a hook must never block session start.
- Output is plain text to stdout (injected as session context) — no side effects, no writes.
- Each hook documents WHY each surfaced item matters, so a fresh agent can act without re-briefing.
- Publication bar applies: hooks here must be domain-general in mechanism; workstation-specific task CONTENT is acceptable only while this repo is private-staging — strip or generalize before public release.

## Inventory

- `zarai-ai-epic-apex-hooks-series-hook-00-must-do-asap-tasks.sh` — surfaces the standing must-do-asap task list at session start. Registered in `~/.claude/settings.json` SessionStart. Added 2026-07-13.

## Captured-but-unclear (do not lose)

- 2026-07-13: kaptain's directive contained a fragment referencing `zarai-ai-epic-apex-hooks-series-hook-99-must-do-asap-tasks.sh` mid-sentence (context garbled by typing constraints). Interpretation pending: possibly a session-END counterpart to hook-00. Ask kaptain before creating.
