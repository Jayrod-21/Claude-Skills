---
name: generate-edge-tests
description: "Analyze existing tests and generate 20+ edge case tests per file — works for pytest, jest, and vitest"
user_invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Generate Edge Case Tests

Analyze existing test files in the current project, then generate additional edge case tests to dramatically increase coverage.

> **Model tip:** Sonnet is fine for this task — the patterns are well-defined.

---

## Phase 1 — Discover Test Files

```bash
echo "=== Python Test Files ==="
find . -maxdepth 4 \( -name "test_*.py" -o -name "*_test.py" \) \
  -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/__pycache__/*" \
  -not -name "*edge_cases*" 2>/dev/null | sort

echo ""
echo "=== JavaScript/TypeScript Test Files ==="
find . -maxdepth 4 \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.test.jsx" -o -name "*.spec.ts" -o -name "*.spec.tsx" \) \
  -not -path "*/node_modules/*" -not -name "*edge*" 2>/dev/null | sort

echo ""
echo "=== Test Runner Config ==="
[ -f "pytest.ini" ] && echo "pytest (root)"
[ -f "backend/pytest.ini" ] && echo "pytest (backend)"
[ -f "backend/conftest.py" ] && echo "conftest (backend)"
[ -f "jest.config.js" ] || [ -f "jest.config.ts" ] && echo "jest (root)"
[ -f "backend/jest.config.js" ] && echo "jest (backend)"
[ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ] && echo "vitest (root)"
[ -f "frontend/vitest.config.ts" ] && echo "vitest (frontend)"
```

If no test files are found, **STOP**: "No existing test files found. Write some base tests first, then run this skill to generate edge cases."

---

## Phase 2 — Analyze Each Test File

For each test file found:

1. **Read the test file** to understand what's being tested and how
2. **Find the source file** it tests:
   - Python: `test_users.py` → look for `users.py`, `services/users.py`, `routes/users.py`
   - JS/TS: `auth.test.ts` → look for `auth.ts`, `auth.js`, `auth.tsx`
3. **Read the source file** to understand the actual implementation
4. Identify:
   - What functions/endpoints are tested
   - What patterns the tests use (fixtures, mocks, assertions)
   - What's NOT tested (error paths, edge cases, boundary conditions)

---

## Phase 3 — Generate Edge Case Tests

For each test file, generate a NEW companion file with 20+ additional edge case tests.

**Naming convention:**
- Python: `test_users.py` → `test_users_edge_cases.py` (same directory)
- JS/TS: `auth.test.ts` → `auth.edge.test.ts` (same directory)

**Edge case categories to cover (aim for at least 3 tests per category where applicable):**

### Input Boundaries
- Empty strings, None/null/undefined
- Maximum length strings (boundary + 1)
- Zero, negative numbers, MAX_INT
- Empty arrays/objects, single-element, very large collections
- Unicode, special characters, emoji in text fields

### Error Paths
- Network timeouts and connection refused
- Database errors (constraint violations, deadlocks)
- File not found, permission denied
- Invalid JSON/malformed request bodies
- Expired tokens, malformed tokens, missing headers

### Authentication & Authorization
- Unauthenticated requests to protected endpoints
- Wrong role accessing restricted resources
- Expired sessions, revoked tokens
- User accessing another user's resources

### State Edge Cases
- Empty database (first user, first record)
- Single record operations
- Concurrent modifications (where applicable)
- Duplicate submissions (idempotency)

### Data Integrity
- SQL injection attempts in input fields
- XSS payloads in text inputs
- Fields at max length, fields just over max length
- Required fields missing, extra unexpected fields

### Performance Boundaries
- Pagination edge cases (page 0, page -1, page beyond max)
- Large payload handling
- Sort by invalid field, filter by nonexistent value

**Rules for generated tests:**
- Mirror the existing test file's style, imports, and patterns exactly
- Use the same fixtures, mocks, and setup/teardown patterns
- Each test must have a clear, descriptive name: `test_<function>_<edge_case>`
- Include a brief comment explaining what edge case each test covers
- Do NOT modify or duplicate anything from the original test file
- Import from the same source as the original tests
- If using pytest: use same conftest fixtures. If using jest/vitest: use same beforeEach/afterEach patterns

Write the new edge case test file using the Write tool.

---

## Phase 4 — Verify

For each generated test file, try running it:

**Python:**
```bash
python3 -m pytest <new_test_file> -x -q --tb=short 2>&1 | tail -20
```

**JS/TS:**
```bash
cd <project_dir> && npx vitest run <new_test_file> --reporter=verbose 2>&1 | tail -20
# OR
cd <project_dir> && npx jest <new_test_file> --verbose 2>&1 | tail -20
```

Report results:
- How many tests were generated
- How many passed, failed, or errored
- Any tests that need manual adjustment (e.g., missing fixtures, unknown mocks)

**It is expected that some edge case tests may fail** — this is intentional. Failing tests reveal actual bugs or missing validation in the source code. Flag these as potential issues to investigate.

---

## Phase 5 — Summary

```
Edge Case Tests Generated
═══════════════════════════
  Original file:     <path>
  New file:          <path>
  Tests generated:   <count>
  Tests passing:     <count>
  Tests failing:     <count> (potential bugs found!)
  Tests erroring:    <count> (may need fixture adjustments)
```

Repeat for each test file processed.

End with:
- Total new tests across all files
- List of any failing tests that suggest real bugs
- Suggest: "Run the full test suite to make sure nothing is broken: `pytest -v` or `npm test`"
