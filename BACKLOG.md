# Backlog — Parked Ideas

Items documented for future implementation. Not prioritized now but worth revisiting.

---

## Cross-Model Validation
**What:** After Claude reviews code, pass the same code to Gemini or Codex for an independent second opinion.
**Why parked:** Needs API keys. Jared has $100 free student credit for Google/OpenAI — revisit when that's activated.
**How to implement:** MCP server or Python script that calls the other model's API and returns a structured review. Could be a `/cross-validate` skill.

## OpenProject Docker
**What:** Replace GitHub Issues with a full project management tool (Gantt charts, sprints, time tracking).
**Why parked:** Overkill for current scale (solo dev, 4-5 active projects). GitHub Issues + `/create-ticket` covers the need.
**Revisit when:** Multiple contributors on the same project, or sprint planning becomes a bottleneck.

## Obsidian Knowledge Base Integration
**What:** Pipe `/session-review` and `/weekly-review` output into an Obsidian vault with backlinks and graph view.
**Why parked:** Manual file-based approach works for now. Obsidian is installed but not actively used for dev notes.
**Revisit when:** `lessons-learned.md` gets long enough that search/navigation becomes painful.

## Automatic Session-End Hooks
**What:** Auto-run `/session-review` when a Claude Code session ends.
**Why parked:** Risk of noise — auto-logging tends to produce entries you never read. Manual `/session-review` is better because you only run it when you actually want to reflect.
**Revisit when:** You find yourself forgetting to run `/session-review` on important sessions.

## Caveman Mode Token Optimization
**What:** Strip verbosity from prompts to reduce token usage by ~75% (reportedly).
**Why parked:** The 75% claim is exaggerated. Skill files are already terse. Claude Code optimizes context internally. Not worth the readability tradeoff.
**Revisit when:** Token costs become a real constraint (e.g., hitting API limits regularly).

## Staging Environment
**What:** Add a staging branch/environment between feature branches and production.
**Why parked:** Only needed when running multiple agents building different features simultaneously. Current workflow (feature branch → PR → main → deploy) is sufficient.
**Revisit when:** Joe and Jared are both running agents that build features at the same time.
