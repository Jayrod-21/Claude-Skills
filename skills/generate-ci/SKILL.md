---
name: generate-ci
description: "Scan project structure and generate a GitHub Actions CI workflow adapted to the stack"
user_invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep, Agent
---

# Generate CI Workflow

Scan the current project's folder structure, dependencies, and git remote, then generate a `.github/workflows/ci.yml` tailored to this project.

---

## Phase 1 — Project Detection

Run all of the following to understand the project:

```bash
# What's the project root?
echo "=== Project Root ==="
pwd
basename "$(pwd)"

# Git remote (for repo name)
echo "=== Git Remote ==="
git remote get-url origin 2>/dev/null || echo "No git remote"

# Top-level structure
echo "=== Top-Level Files ==="
ls -1
```

```bash
# Language/framework detection
echo "=== Stack Detection ==="

# Python
[ -f "requirements.txt" ] && echo "PYTHON: requirements.txt" && head -20 requirements.txt
[ -f "pyproject.toml" ] && echo "PYTHON: pyproject.toml"
[ -f "backend/requirements.txt" ] && echo "PYTHON_BACKEND: backend/requirements.txt" && head -20 backend/requirements.txt
[ -f "Pipfile" ] && echo "PYTHON: Pipfile"

# Node
[ -f "package.json" ] && echo "NODE: package.json" && python3 -c "import json; d=json.load(open('package.json')); print('  scripts:', list(d.get('scripts',{}).keys())); print('  deps:', list(d.get('dependencies',{}).keys())[:10])"
[ -f "frontend/package.json" ] && echo "NODE_FRONTEND: frontend/package.json" && python3 -c "import json; d=json.load(open('frontend/package.json')); print('  scripts:', list(d.get('scripts',{}).keys())); print('  deps:', list(d.get('dependencies',{}).keys())[:10])"
[ -f "backend/package.json" ] && echo "NODE_BACKEND: backend/package.json" && python3 -c "import json; d=json.load(open('backend/package.json')); print('  scripts:', list(d.get('scripts',{}).keys()))"

# TypeScript
[ -f "tsconfig.json" ] && echo "TYPESCRIPT: root"
[ -f "frontend/tsconfig.json" ] && echo "TYPESCRIPT: frontend"

# Docker
[ -f "docker-compose.yml" ] && echo "DOCKER: docker-compose.yml"
[ -f "docker-compose.prod.yml" ] && echo "DOCKER: docker-compose.prod.yml"
[ -f "Dockerfile" ] && echo "DOCKER: Dockerfile"

# Other
[ -f "Cargo.toml" ] && echo "RUST: Cargo.toml"
[ -f "go.mod" ] && echo "GO: go.mod"
[ -f "Makefile" ] && echo "MAKE: Makefile"
[ -f "DESCRIPTION" ] && echo "R: DESCRIPTION"
```

```bash
# Test infrastructure detection
echo "=== Test Infrastructure ==="

# pytest
[ -f "pytest.ini" ] && echo "PYTEST: pytest.ini (root)"
[ -f "backend/pytest.ini" ] && echo "PYTEST: backend/pytest.ini"
[ -f "backend/conftest.py" ] && echo "PYTEST: backend/conftest.py"
[ -d "tests" ] && echo "PYTEST: tests/ dir (root)" && ls tests/ 2>/dev/null | head -10
[ -d "backend/tests" ] && echo "PYTEST: backend/tests/ dir" && ls backend/tests/ 2>/dev/null | head -10

# Jest / Vitest
[ -f "jest.config.js" ] && echo "JEST: root"
[ -f "jest.config.ts" ] && echo "JEST: root (ts)"
[ -f "backend/jest.config.js" ] && echo "JEST: backend"
[ -f "vitest.config.ts" ] && echo "VITEST: root"
[ -f "frontend/vitest.config.ts" ] && echo "VITEST: frontend"
[ -f "frontend/vitest.config.js" ] && echo "VITEST: frontend (js)"

# Linters
command -v ruff &>/dev/null && echo "LINTER: ruff available"
[ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ] && echo "LINTER: eslint (root)"
[ -f "frontend/.eslintrc.js" ] || [ -f "frontend/.eslintrc.json" ] || [ -f "frontend/eslint.config.js" ] && echo "LINTER: eslint (frontend)"

# Existing CI
[ -d ".github/workflows" ] && echo "EXISTING CI:" && ls .github/workflows/ 2>/dev/null
```

```bash
# Framework-specific detection
echo "=== Framework Detection ==="

# Python frameworks
grep -l "fastapi\|FastAPI" backend/requirements.txt requirements.txt 2>/dev/null && echo "FRAMEWORK: FastAPI"
grep -l "django\|Django" backend/requirements.txt requirements.txt 2>/dev/null && echo "FRAMEWORK: Django"
grep -l "flask\|Flask" backend/requirements.txt requirements.txt 2>/dev/null && echo "FRAMEWORK: Flask"

# Node frameworks
grep -l "\"next\"" frontend/package.json package.json 2>/dev/null && echo "FRAMEWORK: Next.js"
grep -l "\"react-scripts\"" frontend/package.json package.json 2>/dev/null && echo "FRAMEWORK: Create React App"
grep -l "\"vite\"" frontend/package.json package.json 2>/dev/null && echo "FRAMEWORK: Vite"
grep -l "\"express\"" backend/package.json package.json 2>/dev/null && echo "FRAMEWORK: Express"

# Database
grep -l "psycopg2\|sqlalchemy\|pg " backend/requirements.txt requirements.txt backend/package.json package.json 2>/dev/null && echo "DATABASE: PostgreSQL likely"
grep -l "sqlite" backend/requirements.txt requirements.txt 2>/dev/null && echo "DATABASE: SQLite"

# Python version hint
[ -f ".python-version" ] && echo "PYTHON_VERSION: $(cat .python-version)"
grep -m1 "python_requires" pyproject.toml 2>/dev/null
```

---

## Phase 2 — Analyze and Decide

Based on Phase 1 output, determine:

1. **Project layout**: monorepo (frontend/ + backend/), single app, or library
2. **Backend stack**: Python (FastAPI/Django/Flask) or Node (Express) — or both
3. **Frontend stack**: Next.js, CRA, Vite, or none
4. **Test runners**: pytest, jest, vitest, or none
5. **Linters**: ruff, eslint, or none
6. **Database**: PostgreSQL (needs CI service), SQLite (no service needed), or none
7. **Package manager**: npm, yarn, pnpm (check lock files)
8. **Python version**: from .python-version, pyproject.toml, or default to 3.12
9. **Node version**: from .nvmrc, package.json engines, or default to 20
10. **Existing CI**: if `.github/workflows/ci.yml` already exists, warn the user and ask before overwriting

Build a mental model of what jobs are needed:
- `backend-lint` → if Python with ruff, or Node backend with eslint
- `backend-test` → if pytest or backend jest exists
- `frontend-lint` → if frontend eslint exists
- `frontend-build` → if frontend has a `build` script
- `frontend-test` → if frontend has a `test` script or vitest/jest config
- `type-check` → if TypeScript (tsconfig.json) exists

For each job, determine:
- Working directory (`backend/`, `frontend/`, or root)
- Dependencies to install
- Whether it needs a PostgreSQL service container
- Environment variables needed (use safe CI defaults, never real secrets)

---

## Phase 3 — Generate the CI Workflow

Create `.github/workflows/ci.yml` using the Write tool.

**Rules for generation:**
- Always use pinned action versions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`)
- Trigger on `push: branches: [main]` AND `pull_request: branches: [main]`
- Use caching (`cache: pip` or `cache: npm`) for faster runs
- Set `cache-dependency-path` to the correct lock/requirements file
- If PostgreSQL is needed: add a `services.postgres` block with health checks
- For test jobs, add `needs: [lint-job]` so lint runs first
- Use `--passWithNoTests` for npm/vitest to avoid failing on empty test suites
- For CRA projects: set `CI: "true"` env and use `--watchAll=false` for tests
- For Next.js projects: provide dummy `NEXT_PUBLIC_*` env vars for build
- Include section comment headers (`# PYTHON BACKEND`, `# NODE FRONTEND`) for readability
- Never include deploy steps — CI is test-only

**Template structure:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # Jobs generated based on detection...
```

---

## Phase 4 — Verify

```bash
# Confirm the file was created
cat .github/workflows/ci.yml | head -5

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('Valid YAML')" 2>/dev/null || echo "Note: PyYAML not installed, skipping validation"
```

Display a summary to the user:

```
CI Workflow Generated: .github/workflows/ci.yml

Jobs created:
  ✅ backend-lint    — ruff (Python 3.12)
  ✅ backend-test    — pytest, needs PostgreSQL service
  ✅ frontend-lint   — eslint
  ✅ frontend-build  — npm run build (Next.js)
  ✅ frontend-test   — vitest

Triggers: push to main, PRs targeting main
```

If an existing CI file was found, remind: "An existing CI file was detected. The new file has been written — review the diff before committing."

Suggest next steps:
- "Commit and push on a branch to test: `/smart-commit` then `/create-pr`"
- "Or run tests locally first to make sure they pass: `pytest -v` / `npm test`"
