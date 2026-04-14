# 11a. Workflow Automation

## What
Reusable hooks, templates, and skills for Claude Code workflow improvements across all projects. Born from Vasu's vibe coding session recommendations.

## Repo
- GitHub: Jayrod-21/Claude-Skills
- SSH: git@github.com:Jayrod-21/Claude-Skills.git

## Structure
```
├── hooks/              # Claude Code hooks (PreToolUse, PostToolUse, etc.)
│   └── pre-push-gate.sh    # Blocks git push if tests fail
├── templates/
│   ├── security-baseline.md # 10-item security checklist for new projects
│   └── ci/
│       ├── python-node-ci.yml  # CI template: Python + Node fullstack
│       └── deploy-ec2.yml      # Deploy template: EC2 via SSH + Docker
├── skills/
│   ├── generate-ci/         # /generate-ci — auto-detect stack and create CI workflow
│   ├── security-audit/      # /security-audit — pentest with separate agent context
│   ├── generate-edge-tests/ # /generate-edge-tests — 20+ edge cases per test file
│   ├── session-review/      # /session-review — end-of-session lessons learned
│   ├── weekly-review/       # /weekly-review — cross-project code review
│   └── create-ticket/       # /create-ticket — GitHub Issues via gh CLI
└── scripts/            # Deterministic Python utilities (Phase 4)
```

## Installed Hooks
- `pre-push-gate.sh` → `~/.claude/settings.json` PreToolUse hook
  - Symlinked into Plugin-Marketplace workspace-tools hooks
  - Blocks `git push` if project tests fail
  - Auto-detects Python (pytest) and Node (npm test) projects

## Rules
- **NEVER push directly to main** — always create a branch
- **Always use SSH** for git push
