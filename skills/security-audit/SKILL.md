---
name: security-audit
description: "Run a security audit on the current project using a separate agent context (pentest from fresh eyes)"
user_invocable: true
allowed-tools: Bash, Read, Glob, Grep, Agent
---

# Security Audit

Run a comprehensive security audit on the current project using a **separate agent context** — the auditor has no knowledge of how the code was built, simulating an external penetration tester.

> **Model tip:** Use Opus for best analysis quality.

---

## Phase 1 — Project Reconnaissance

Gather project context to brief the auditor agent:

```bash
echo "=== Project Root ==="
pwd

echo "=== Git Remote ==="
git remote get-url origin 2>/dev/null || echo "No remote"

echo "=== Top-Level Structure ==="
ls -1

echo "=== Stack Detection ==="
[ -f "requirements.txt" ] && echo "Python (root)" && head -5 requirements.txt
[ -f "backend/requirements.txt" ] && echo "Python (backend)" && head -5 backend/requirements.txt
[ -f "package.json" ] && echo "Node (root)"
[ -f "frontend/package.json" ] && echo "Node (frontend)"
[ -f "backend/package.json" ] && echo "Node (backend)"
[ -f "docker-compose.yml" ] && echo "Docker"
```

```bash
echo "=== Entry Points ==="
# Python entry points
find . -maxdepth 3 -name "main.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null
find . -maxdepth 3 -name "app.py" -not -path "*/node_modules/*" 2>/dev/null
find . -maxdepth 3 -name "index.js" -not -path "*/node_modules/*" 2>/dev/null
find . -maxdepth 3 -name "index.ts" -not -path "*/node_modules/*" 2>/dev/null

echo "=== Auth Files ==="
find . -maxdepth 4 -name "*auth*" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null

echo "=== Route/Endpoint Files ==="
find . -maxdepth 4 -name "*route*" -not -path "*/node_modules/*" 2>/dev/null
find . -maxdepth 4 -name "*router*" -not -path "*/node_modules/*" 2>/dev/null

echo "=== Config Files ==="
find . -maxdepth 3 \( -name "*.env*" -o -name "config.*" -o -name "settings.*" \) -not -path "*/node_modules/*" 2>/dev/null

echo "=== Middleware ==="
find . -maxdepth 4 -path "*/middleware/*" -not -path "*/node_modules/*" 2>/dev/null
```

Read the key files identified above (entry points, auth, routes, config, middleware) to understand the attack surface.

---

## Phase 2 — Launch Pentest Agent

Launch a separate agent using the Agent tool. This is critical — the auditor must run in its own context window, not yours.

**Agent prompt must include:**
1. The project root path
2. The detected stack (Python/Node/both)
3. The list of entry point, auth, route, config, and middleware file paths discovered in Phase 1
4. The contents of key files you read

**Agent instructions:**

```
You are a security auditor performing a penetration test on this project.
You have NO context on how this code was built — approach it as an external attacker would.

Project root: <path>
Stack: <detected stack>
Key files: <list from Phase 1>

Perform these 8 security scans. For EACH scan, search the actual codebase — do not guess or assume.

## Scan 1 — Hardcoded Secrets
Search for: API keys, passwords, tokens, connection strings in source code.
Patterns: sk-, AKIA, ghp_, password=, api_key=, secret=, token=, Bearer, DATABASE_URL with credentials
Check: .env files committed to git, config files with real values, comments with credentials.
Run: grep -rn for each pattern. Check git log for accidentally committed secrets.

## Scan 2 — SQL Injection
Search for: String concatenation in database queries.
Patterns: f"SELECT, f"INSERT, f"UPDATE, f"DELETE, `${...}` in SQL strings, .query() with template literals, .execute() with % or .format()
Verify: Are parameterized queries used consistently? Any raw SQL with user input?

## Scan 3 — XSS Vectors
Search for: Unescaped user content in rendered HTML.
Patterns: dangerouslySetInnerHTML, v-html, innerHTML=, document.write, template literals in HTML responses
Check: Are user-provided values escaped before rendering? Is there a Content-Security-Policy header?

## Scan 4 — Authentication & Authorization Bypass
Check: Are all protected routes actually using auth middleware?
Look for: Routes that should require auth but don't have middleware applied.
Verify: Is role-based access control enforced server-side? Can a regular user access admin endpoints?
Check: JWT configuration — is secret strong? Is expiry set? Is algorithm pinned (not "none")?

## Scan 5 — CORS Misconfiguration
Search for: CORS settings in the codebase.
Patterns: allow_origins, cors(), Access-Control-Allow-Origin, CORS_ORIGIN
Red flags: "*" as allowed origin, reflection of Origin header without validation, credentials with wildcard.

## Scan 6 — Dependency Vulnerabilities
Run: Check for known vulnerable packages.
For Python: Look at requirements.txt versions against known CVEs.
For Node: Check package.json for outdated/vulnerable packages.
Flag: Any pinned versions that are significantly outdated.

## Scan 7 — Missing Rate Limiting
Check: Are public-facing endpoints rate-limited?
Look for: Login endpoints, registration, password reset, API endpoints accepting user input.
Verify: Is there rate-limiting middleware applied? Per-IP? Per-user?

## Scan 8 — Insecure Defaults & Misconfigurations
Check: Debug mode in production configs, permissive file upload settings, missing security headers.
Look for: DEBUG=True, ALLOWED_HOSTS=["*"], missing HTTPS redirect, session cookies without Secure/HttpOnly flags.
Verify: Is there a .env.example? Are production configs separate from dev configs?

## Output Format

For each finding, report:

**[P0-CRITICAL]** — Exploitable now, data at risk (e.g., hardcoded production API key, SQL injection on login)
**[P1-HIGH]** — Significant risk, needs fix before deploy (e.g., missing auth on admin route, CORS wildcard with credentials)
**[P2-MEDIUM]** — Should fix soon (e.g., outdated dependency with known CVE, missing rate limiting on login)
**[P3-LOW]** — Best practice improvement (e.g., missing CSP header, no .env.example)

For each finding include:
- File path and line number
- What the vulnerability is
- How an attacker would exploit it
- Specific fix recommendation

End with a summary table: count of P0/P1/P2/P3 findings.
```

---

## Phase 3 — Present Results

Collect the agent's findings and present them to the user organized by priority:

1. **P0 — Critical** (fix immediately)
2. **P1 — High** (fix before deploy)
3. **P2 — Medium** (fix soon)
4. **P3 — Low** (best practice)

Display the summary table:

```
Security Audit Summary
═══════════════════════
  P0 Critical:  X findings
  P1 High:      X findings
  P2 Medium:    X findings
  P3 Low:       X findings
  ─────────────────────
  Total:         X findings
```

If P0 or P1 findings exist, emphasize: **"This project has critical/high-priority security issues that should be fixed before deploying."**

Suggest next steps:
- Fix P0/P1 issues first
- Run `/security-audit` again after fixes to verify
- Consider adding the security baseline checklist to the project's CLAUDE.md (template at `/root/Jared/11a. Workflow Automation/templates/security-baseline.md`)
