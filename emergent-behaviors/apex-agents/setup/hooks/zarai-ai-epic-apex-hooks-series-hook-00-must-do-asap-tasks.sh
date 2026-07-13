#!/usr/bin/env bash
# zarai-ai-epic-apex-hooks-series-hook-00-must-do-asap-tasks.sh
# SessionStart hook: surfaces the standing MUST-DO-ASAP task list so no session
# forgets open structural debts. Read-only; silent-fail; never blocks session start.
# Series contract: see AGENTS.md alongside this file.

set +e  # silent-fail law: a broken hook must never block a session

cat << 'MUSTDO' 2>/dev/null
[ZARAI APEX HOOK-00 — MUST-DO-ASAP STANDING TASKS]
1. HERMES-AGENT-MAKER TOTAL OVERHAUL (P1): the maker must create profiles ONLY via the
   official `hermes profile create` (bare-mkdir profiles are unlaunchable husks — HTTP 400).
   Current maker quality assessed as intern-grade ("knows hermes agent syntax, nothing more");
   rebuild it to master standard: blueprint-driven, self-testing, forging agents that
   self-evolve. Fleet law: project buildout goes BLUEPRINT.json → hermes-agent-maker →
   hermes kanban squads (never claude-code subagents for project code).
2. EchoSDK DOES NOT EXIST YET (gap, 2026-07-13): agent-summon SDK (kaptain prefers SDK over
   loose scripts — .py + template .yaml/.json partner config, simple commands, no migration
   debt). /skillforge currently implements loop-back inside its own prompt (DoD self-audit +
   /goal dispatch line); once EchoSDK exists, wire slash-command → /goal natively through it.
3. GLOBAL ~/.claude/CLAUDE.md CONTAINS A DUPLICATED CHARTER BLOCK (~line 1177 onward,
   flagged 2026-07-13, PART 6 §6.7): diff as evolutionary siblings and reconcile — only on
   kaptain's explicit word.
Act on these when session scope allows; each closes only with witnessed evidence.
MUSTDO

exit 0
