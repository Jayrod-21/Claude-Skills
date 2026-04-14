#!/usr/bin/env python3
"""Count test files and test functions across all Jared's projects.

Usage: python3 count-tests.py [--verbose]
"""

import re
import sys
from pathlib import Path

JARED_DIR = Path("/root/Jared")

PROJECTS = [
    ("1a. Stats Website", "backend/src/tests"),
    ("1a. Stats Website", "frontend/src/tests"),
    ("3a. SpecialSprinkleSauce", "backend/tests"),
    ("3a. SpecialSprinkleSauce", "frontend/src"),
    ("4a. MK Labs/website", "backend/src/tests"),
    ("4a. MK Labs/website", "frontend/src/tests"),
    ("9e. LeveledLife Chronicle -- OVERNIGHT/2. Repository", "backend/tests"),
    ("9e. LeveledLife Chronicle -- OVERNIGHT/2. Repository", "frontend/src"),
]

# Patterns that identify test files
TEST_FILE_PATTERNS = [
    "test_*.py", "*_test.py",
    "*.test.js", "*.test.jsx", "*.test.ts", "*.test.tsx",
    "*.spec.js", "*.spec.ts", "*.spec.tsx",
]

# Patterns that identify test functions inside files
PYTHON_TEST_RE = re.compile(r"^\s*def (test_\w+)", re.MULTILINE)
JS_TEST_RE = re.compile(r"^\s*(?:it|test)\s*\(", re.MULTILINE)

verbose = "--verbose" in sys.argv


def count_tests_in_file(filepath: Path) -> int:
    """Count test functions/cases in a single test file."""
    try:
        content = filepath.read_text(errors="replace")
    except OSError:
        return 0

    if filepath.suffix == ".py":
        return len(PYTHON_TEST_RE.findall(content))
    else:
        return len(JS_TEST_RE.findall(content))


def find_test_files(directory: Path) -> list[Path]:
    """Find all test files in a directory tree."""
    if not directory.exists():
        return []

    files = []
    for pattern in TEST_FILE_PATTERNS:
        files.extend(directory.rglob(pattern))

    # Filter out node_modules, __pycache__, .venv
    files = [
        f for f in files
        if "node_modules" not in f.parts
        and "__pycache__" not in f.parts
        and ".venv" not in f.parts
    ]
    return sorted(set(files))


def main():
    total_files = 0
    total_tests = 0

    print("=" * 65)
    print(f"{'Project':<40} {'Files':>6} {'Tests':>6}")
    print("=" * 65)

    project_totals: dict[str, tuple[int, int]] = {}

    for project, test_subdir in PROJECTS:
        test_dir = JARED_DIR / project / test_subdir
        files = find_test_files(test_dir)

        file_count = len(files)
        test_count = sum(count_tests_in_file(f) for f in files)

        # Aggregate by project name (some have multiple test dirs)
        base_project = project.split("/")[0]
        prev_files, prev_tests = project_totals.get(base_project, (0, 0))
        project_totals[base_project] = (prev_files + file_count, prev_tests + test_count)

        if verbose and files:
            print(f"\n  {project} / {test_subdir}:")
            for f in files:
                fc = count_tests_in_file(f)
                print(f"    {f.name:<40} {fc:>3} tests")

    for project, (file_count, test_count) in sorted(project_totals.items()):
        print(f"  {project:<38} {file_count:>6} {test_count:>6}")
        total_files += file_count
        total_tests += test_count

    print("-" * 65)
    print(f"  {'TOTAL':<38} {total_files:>6} {total_tests:>6}")
    print("=" * 65)


if __name__ == "__main__":
    main()
