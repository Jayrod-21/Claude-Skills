#!/usr/bin/env python3
"""Batch rename files matching a pattern.

Usage:
  python3 rename-files.py --dir ./photos --pattern "IMG_(\\d+)" --replacement "photo_\\1" --dry-run
  python3 rename-files.py --dir ./docs --pattern "\\.txt$" --replacement ".md"
  python3 rename-files.py --dir . --pattern "test_(.+)_old" --replacement "test_\\1"

Always use --dry-run first to preview changes.
"""

import argparse
import re
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Batch rename files with regex")
    parser.add_argument("--dir", type=Path, required=True, help="Directory to scan")
    parser.add_argument("--pattern", required=True, help="Regex pattern to match in filenames")
    parser.add_argument("--replacement", required=True, help="Replacement string (supports \\1, \\2 groups)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without renaming")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories too")
    args = parser.parse_args()

    if not args.dir.exists():
        print(f"Error: Directory {args.dir} not found", file=sys.stderr)
        sys.exit(1)

    regex = re.compile(args.pattern)

    # Collect matching files
    if args.recursive:
        files = sorted(args.dir.rglob("*"))
    else:
        files = sorted(args.dir.iterdir())

    files = [f for f in files if f.is_file()]

    renames = []
    for filepath in files:
        old_name = filepath.name
        new_name = regex.sub(args.replacement, old_name)

        if new_name != old_name:
            new_path = filepath.parent / new_name
            renames.append((filepath, new_path))

    if not renames:
        print("No files matched the pattern.")
        return

    # Display changes
    max_old = max(len(str(old.name)) for old, _ in renames)
    print(f"{'Current Name':<{max_old + 2}} -> New Name")
    print("-" * (max_old + 30))

    for old, new in renames:
        prefix = "[DRY RUN] " if args.dry_run else ""
        print(f"{prefix}{old.name:<{max_old + 2}} -> {new.name}")

    if args.dry_run:
        print(f"\n{len(renames)} files would be renamed. Remove --dry-run to execute.")
        return

    # Execute renames
    conflicts = [new for _, new in renames if new.exists()]
    if conflicts:
        print(f"\nError: {len(conflicts)} target files already exist. Aborting.", file=sys.stderr)
        for c in conflicts[:5]:
            print(f"  Conflict: {c}", file=sys.stderr)
        sys.exit(1)

    for old, new in renames:
        old.rename(new)

    print(f"\nRenamed {len(renames)} files.")


if __name__ == "__main__":
    main()
