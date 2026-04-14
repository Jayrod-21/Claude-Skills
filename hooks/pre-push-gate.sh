#!/bin/bash
# PreToolUse hook — run project tests before allowing git push
# Blocks push if any tests fail. Multi-project: detects test runner dynamically.
#
# Exit codes:
#   0 = allow (tests passed or no tests found)
#   2 = block (tests failed — feedback sent via stderr)

# Parse input JSON from stdin (same pattern as post-tool-use.sh)
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only intercept Bash tool calls that are git push commands
if [[ "$TOOL_NAME" != "Bash" ]]; then
  exit 0
fi

# Match git push (with optional flags/remote/branch)
if ! echo "$COMMAND" | grep -qE '^\s*git\s+push'; then
  exit 0
fi

echo "Pre-push gate: Running tests before push..." >&2

# ═══════════════════════════════════════
# PROJECT TYPE DETECTION
# (reuses logic from session-start.sh)
# ═══════════════════════════════════════
HAS_PYTHON=false
HAS_NODE=false
PYTHON_TEST_DIR=""
NODE_TEST_CMD=""

# Python detection
if [[ -f "requirements.txt" || -f "pyproject.toml" || -f "setup.py" ]]; then
  HAS_PYTHON=true
fi
# Check for backend subdirectory (common in fullstack projects)
if [[ -d "backend" && (-f "backend/requirements.txt" || -f "backend/pyproject.toml") ]]; then
  HAS_PYTHON=true
fi

# Node detection
if [[ -f "package.json" ]]; then
  HAS_NODE=true
fi
# Check for frontend subdirectory
if [[ -d "frontend" && -f "frontend/package.json" ]]; then
  HAS_NODE=true
fi

# ═══════════════════════════════════════
# FIND AND RUN TESTS
# ═══════════════════════════════════════
TESTS_RAN=false
TESTS_FAILED=false
FEEDBACK=""

# --- Python tests ---
if [[ "$HAS_PYTHON" == true ]] && command -v pytest &>/dev/null; then
  # Find test directory: check backend/tests, tests, test
  for TEST_DIR in "backend/tests" "backend/test" "tests" "test"; do
    if [[ -d "$TEST_DIR" ]]; then
      PYTHON_TEST_DIR="$TEST_DIR"
      break
    fi
  done

  # Also check for any test_*.py files in the project
  if [[ -z "$PYTHON_TEST_DIR" ]]; then
    TEST_FILES=$(find . -maxdepth 3 -name "test_*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null | head -1)
    if [[ -n "$TEST_FILES" ]]; then
      PYTHON_TEST_DIR=$(dirname "$TEST_FILES")
    fi
  fi

  if [[ -n "$PYTHON_TEST_DIR" ]]; then
    FEEDBACK+="Running pytest ($PYTHON_TEST_DIR)...\n"
    PYTEST_OUT=$(timeout 120 python3 -m pytest "$PYTHON_TEST_DIR" -x -q --tb=short 2>&1)
    PYTEST_EXIT=$?
    TESTS_RAN=true

    if [[ $PYTEST_EXIT -ne 0 ]]; then
      TESTS_FAILED=true
      FEEDBACK+="\n❌ PYTEST FAILED:\n$PYTEST_OUT\n"
    else
      FEEDBACK+="✅ pytest passed\n"
    fi
  fi
fi

# --- Node tests ---
if [[ "$HAS_NODE" == true ]]; then
  # Check root package.json for test script
  if [[ -f "package.json" ]] && python3 -c "import json; d=json.load(open('package.json')); exit(0 if 'test' in d.get('scripts',{}) else 1)" 2>/dev/null; then
    FEEDBACK+="Running npm test...\n"
    NODE_OUT=$(timeout 120 npm test -- --passWithNoTests 2>&1)
    NODE_EXIT=$?
    TESTS_RAN=true

    if [[ $NODE_EXIT -ne 0 ]]; then
      TESTS_FAILED=true
      FEEDBACK+="\n❌ NPM TEST FAILED:\n$(echo "$NODE_OUT" | tail -20)\n"
    else
      FEEDBACK+="✅ npm test passed\n"
    fi
  fi

  # Check frontend and backend subdirectories
  for SUB_DIR in "frontend" "backend"; do
    if [[ -f "$SUB_DIR/package.json" ]] && python3 -c "import json; d=json.load(open('$SUB_DIR/package.json')); exit(0 if 'test' in d.get('scripts',{}) else 1)" 2>/dev/null; then
      FEEDBACK+="Running npm test ($SUB_DIR)...\n"
      SUB_OUT=$(timeout 120 bash -c "cd '$SUB_DIR' && npm test -- --passWithNoTests" 2>&1)
      SUB_EXIT=$?
      TESTS_RAN=true

      if [[ $SUB_EXIT -ne 0 ]]; then
        TESTS_FAILED=true
        FEEDBACK+="\n❌ NPM TEST ($SUB_DIR) FAILED:\n$(echo "$SUB_OUT" | tail -20)\n"
      else
        FEEDBACK+="✅ npm test ($SUB_DIR) passed\n"
      fi
    fi
  done
fi

# ═══════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════
if [[ "$TESTS_FAILED" == true ]]; then
  echo -e "\n🚫 PRE-PUSH GATE: Tests failed — push blocked.\n$FEEDBACK" >&2
  echo "Fix failing tests before pushing." >&2
  exit 2
fi

if [[ "$TESTS_RAN" == true ]]; then
  echo -e "$FEEDBACK" >&2
  echo "Pre-push gate: All tests passed." >&2
fi

# If no tests found, allow the push silently
exit 0
