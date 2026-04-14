---
name: session-review
description: "End-of-session review — analyze what changed, extract patterns and lessons, append to knowledge base"
user_invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Session Review

Analyze the current session's work, extract patterns and lessons learned, and append to the knowledge base. Run this at the end of a session to capture what worked and what to avoid next time.

> **Model tip:** Use Opus for best pattern analysis.

---

## Phase 1 — Gather Session Activity

```bash
echo "=== Project ==="
basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
git remote get-url origin 2>/dev/null || echo "No remote"

echo ""
echo "=== Recent Commits (last 8 hours) ==="
git log --since="8 hours ago" --oneline --all 2>/dev/null || echo "No recent commits"

echo ""
echo "=== Files Changed ==="
git diff HEAD~5..HEAD --stat 2>/dev/null || git diff --stat 2>/dev/null || echo "No changes"

echo ""
echo "=== Uncommitted Changes ==="
git status --short 2>/dev/null || echo "Clean"
```

```bash
echo "=== Diff Summary (what actually changed) ==="
git diff HEAD~5..HEAD --shortstat 2>/dev/null || echo "No diff"

echo ""
echo "=== Churn (files edited multiple times) ==="
git log --since="8 hours ago" --name-only --pretty=format: 2>/dev/null | sort | uniq -c | sort -rn | head -10
```

If there are no recent commits and no uncommitted changes, **STOP**: "No session activity detected. Nothing to review."

---

## Phase 2 — Analyze the Changes

Read the actual diff to understand what was done:

```bash
git diff HEAD~5..HEAD 2>/dev/null | head -500
```

Also read any files that were edited multiple times (churn indicates iteration/difficulty).

Look for these patterns:

### Positive Patterns (what worked well)
- Clean abstractions introduced
- Good test coverage added alongside features
- Proper error handling implemented
- Security measures added proactively
- Consistent code style maintained

### Anti-Patterns (what to avoid)
- Same file edited many times (thrashing — unclear requirements or approach)
- Magic numbers or hardcoded values
- Missing error handling on I/O operations
- Tests skipped or marked as TODO
- Security shortcuts (CORS wildcard, disabled auth for testing, etc.)
- Large functions that should be decomposed

### Repeated Mistakes
- Same type of bug fixed multiple times
- Import errors, typos, syntax issues that slowed things down
- Configuration issues that blocked progress

---

## Phase 3 — Write the Review

Prepare the lessons-learned entry. The target file is:

```
/root/Jared/7a. Claude Notes/lessons-learned.md
```

If the file doesn't exist, create it with a header:

```bash
[ ! -f "/root/Jared/7a. Claude Notes/lessons-learned.md" ] && echo "Creating lessons-learned.md..."
```

If creating for the first time, write the header:
```markdown
# Lessons Learned — Claude Code Sessions

A running log of patterns, mistakes, and techniques from coding sessions.
Reviewed periodically to identify recurring issues and compound knowledge.

---
```

Then append a new entry using the Write tool (append to end of file):

```markdown

## YYYY-MM-DD — <Project Name>

**What was done:**
- <1-3 bullet summary of the session's work>

**Patterns that worked:**
- <What went well — approaches, tools, patterns worth repeating>

**Mistakes to avoid:**
- <What went wrong — anti-patterns, time sinks, bugs introduced>
- <Include specific file/function references if relevant>

**Techniques learned:**
- <Any new approaches discovered during this session>

**Security notes:**
- <Any security-relevant changes made or needed>

---
```

**Guidelines for writing the entry:**
- Be specific — reference actual file names, function names, error messages
- Only include genuinely useful observations, not obvious things
- Focus on what would help FUTURE sessions, not just documenting this one
- If nothing notable happened in a category, skip it rather than writing filler
- Keep each entry under 20 lines — concise beats comprehensive

---

## Phase 4 — Display and Confirm

Display the entry you just appended so the user can review it.

```bash
echo "=== Entry appended to lessons-learned.md ==="
tail -30 "/root/Jared/7a. Claude Notes/lessons-learned.md"
```

Tell the user:
- "Session review saved. Over time, patterns will emerge — review this file monthly to spot recurring issues."
- If anti-patterns were found: "Consider addressing these before the next session."
