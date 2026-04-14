---
name: create-ticket
description: "Create, list, and manage GitHub Issues for the current repo via gh CLI"
arguments: "<title> [| <body>] [--label <label>]"
user_invocable: true
allowed-tools: Bash, Read
---

# Create Ticket

Create and manage GitHub Issues for the current repository. Replaces local ticket.md files with proper issue tracking.

---

## Phase 1 — Detect Repository

```bash
echo "=== Repository ==="
REMOTE=$(git remote get-url origin 2>/dev/null)
echo "Remote: $REMOTE"

# Parse owner/repo from SSH or HTTPS URL
if [ -n "$REMOTE" ]; then
  REPO=$(echo "$REMOTE" | sed -E 's|.*github\.com[:/](.+)(\.git)?$|\1|' | sed 's/\.git$//')
  echo "Repo: $REPO"
fi

echo ""
echo "=== Open Issues ==="
gh issue list --limit 10 2>/dev/null || echo "gh CLI not authenticated or not available"
```

If `gh` is not available or not authenticated, **STOP**: "The `gh` CLI is required. Run `gh auth login` first."

If no git remote, **STOP**: "No git remote found. This command works with GitHub repositories."

---

## Phase 2 — Parse Arguments

The user's input (`$ARGUMENTS`) can take several forms:

1. **Just a title:** `Fix the login timeout bug`
2. **Title + body separated by pipe:** `Fix the login timeout bug | The session expires after 30 seconds instead of 30 minutes`
3. **Title + labels:** `Fix the login timeout bug --label bug --label urgent`
4. **Title + body + labels:** `Fix the login timeout bug | Session timeout is wrong --label bug`
5. **No arguments:** Show open issues and ask what to create

If `$ARGUMENTS` is empty or not provided, display the open issues list and ask the user what issue they'd like to create.

Parse the arguments:
- Split on first `|` to get title and body
- Extract any `--label <value>` flags from the end
- Trim whitespace from all parts

---

## Phase 3 — Check for Duplicates

```bash
# Search existing issues for similar titles
gh issue list --search "<title keywords>" --limit 5 2>/dev/null
```

If similar issues exist, show them and ask: "These existing issues look similar. Still want to create a new one?"

---

## Phase 4 — Create the Issue

Build the `gh issue create` command:

```bash
gh issue create \
  --title "<parsed title>" \
  --body "<parsed body or auto-generated description>" \
  [--label "<label1>" --label "<label2>"]
```

If no body was provided, generate a brief one based on the title:
```
Created via `/create-ticket` in Claude Code.

**Context:** <infer from title>
**Priority:** To be triaged
```

---

## Phase 5 — Report

Display the created issue:

```bash
# The gh command outputs the issue URL
echo "Issue created successfully."
```

Show:
- Issue number and URL
- Title, labels, assignee
- "View all issues: `gh issue list`"
- "Close when done: `gh issue close <number>`"
- "Add to a PR: include `Closes #<number>` in the PR description"
