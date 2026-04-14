---
name: weekly-review
description: "Cross-project weekly code review — robustness, security, performance — generates a dated report"
user_invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep, Agent
---

# Weekly Review

Review all active projects for the past week. Evaluate code changes across three dimensions in order: (1) robustness/reliability, (2) security, (3) performance. Generate a consolidated report.

> **Model tip:** Use Opus for best analysis quality across multiple projects.

---

## Phase 1 — Enumerate Active Projects

Check each known project for recent activity:

```bash
echo "=== Scanning Active Projects ==="

PROJECTS=(
  "/root/Jared/1a. Stats Website"
  "/root/Jared/3a. SpecialSprinkleSauce"
  "/root/Jared/4a. MK Labs/website"
  "/root/Jared/9e. LeveledLife Chronicle -- OVERNIGHT/2. Repository"
)

ACTIVE_PROJECTS=()

for proj in "${PROJECTS[@]}"; do
  if [ -d "$proj/.git" ]; then
    COMMITS=$(cd "$proj" && git log --since="7 days ago" --oneline --all 2>/dev/null | wc -l | tr -d ' ')
    if [ "$COMMITS" -gt 0 ]; then
      NAME=$(basename "$proj")
      echo "ACTIVE: $NAME ($COMMITS commits this week)"
      ACTIVE_PROJECTS+=("$proj")
    else
      echo "QUIET:  $(basename "$proj") (no commits this week)"
    fi
  fi
done

echo ""
echo "Active projects: ${#ACTIVE_PROJECTS[@]}"
```

If zero active projects, **STOP**: "No projects had commits this week. Nothing to review."

---

## Phase 2 — Gather Changes Per Project

For each active project, collect:

```bash
# Run this for each active project
cd "<project_path>"

echo "=== $(basename "$(pwd)") ==="
echo ""

echo "--- Commits ---"
git log --since="7 days ago" --oneline --all

echo ""
echo "--- File Changes ---"
# Get the diff between now and 7 days ago
OLDEST_COMMIT=$(git log --since="7 days ago" --format="%H" --reverse | head -1)
if [ -n "$OLDEST_COMMIT" ]; then
  git diff "$OLDEST_COMMIT"..HEAD --stat | tail -20
fi

echo ""
echo "--- Churn (most-edited files) ---"
git log --since="7 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -10
```

---

## Phase 3 — Code Review (Per Project)

For each active project, launch an Agent to review the changes. The agent should read the actual diffs and changed files.

**Review must be done IN THIS ORDER — this is intentional priority ordering:**

### 3a. Robustness & Reliability (FIRST)
- Are new functions handling errors properly? (try/catch, error returns)
- Are I/O operations (network, file, database) wrapped in error handling?
- Are there retry mechanisms where appropriate?
- Are null/undefined checks in place for external data?
- Are there any bare `except:` or `catch(e) {}` blocks that swallow errors?
- Are there race conditions in async code?
- Is input validated before use?

### 3b. Security (SECOND)
- Were any new endpoints added without auth middleware?
- Are there hardcoded secrets, API keys, or credentials in the diff?
- Is user input sanitized before database queries?
- Are there new CORS settings that are too permissive?
- Were any dependencies added with known vulnerabilities?
- Are there new file upload handlers without validation?

### 3c. Performance (THIRD)
- Are there N+1 query patterns (query inside a loop)?
- Are there large payloads being fetched without pagination?
- Are there unindexed database queries on large tables?
- Are there synchronous blocking calls that should be async?
- Are expensive computations being repeated instead of cached?

---

## Phase 4 — Generate Report

Create the weekly report file:

```bash
REPORT_DIR="/root/Jared/7a. Claude Notes/weekly-reviews"
mkdir -p "$REPORT_DIR"
DATE=$(date +%Y-%m-%d)
echo "Report: $REPORT_DIR/$DATE.md"
```

Write the report using the Write tool:

```markdown
# Weekly Code Review — YYYY-MM-DD

## Summary
- **Projects reviewed:** X
- **Total commits this week:** X
- **Findings:** X robustness, X security, X performance

---

## <Project Name>

### Changes This Week
- <commit summary bullets>

### Robustness & Reliability
- **[PASS]** or **[ISSUE]** <description, file:line reference>

### Security
- **[PASS]** or **[ISSUE]** <description, file:line reference>

### Performance
- **[PASS]** or **[ISSUE]** <description, file:line reference>

### Recommendations
- <Specific actionable items>
- Consider running `/security-audit` on this project
- Consider running `/generate-edge-tests` on <specific file>

---

(Repeat for each project)

## Action Items
1. [ ] <Highest priority item across all projects>
2. [ ] <Second priority>
3. [ ] ...
```

---

## Phase 5 — Present Results

Display the report summary to the user.

```bash
echo "=== Weekly Review Complete ==="
DATE=$(date +%Y-%m-%d)
echo "Full report: /root/Jared/7a. Claude Notes/weekly-reviews/$DATE.md"
```

Highlight:
- Any security issues found (P0/P1)
- Any robustness gaps in critical paths
- Which projects need the most attention
- Suggest specific slash commands to run: `/security-audit`, `/generate-edge-tests`

If the lessons-learned.md exists, mention: "See also `/session-review` entries for session-level patterns."
