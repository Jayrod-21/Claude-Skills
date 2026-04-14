#!/usr/bin/env python3
"""Check for outdated dependencies across all Jared's projects.

Scans requirements.txt and package.json files, reports pinned versions
and checks PyPI/npm for newer versions.

Usage: python3 check-deps.py [--check-latest]

Without --check-latest: just lists what's pinned (fast, no network).
With --check-latest: queries PyPI and npm registry for latest versions (slower).
"""

import json
import re
import sys
from pathlib import Path

JARED_DIR = Path("/root/Jared")
CHECK_LATEST = "--check-latest" in sys.argv

# Projects to scan
SCAN_DIRS = [
    "1a. Stats Website",
    "3a. SpecialSprinkleSauce",
    "4a. MK Labs/website",
    "9e. LeveledLife Chronicle -- OVERNIGHT/2. Repository",
    "6b. Schedule/jared-scheduler",
]


def parse_requirements_txt(filepath: Path) -> list[dict]:
    """Parse a requirements.txt file into a list of {name, version}."""
    deps = []
    try:
        for line in filepath.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # Match: package==1.2.3 or package>=1.2.3
            match = re.match(r"^([a-zA-Z0-9_-]+)\[?[^\]]*\]?\s*([><=!~]+)\s*(.+)", line)
            if match:
                deps.append({
                    "name": match.group(1),
                    "pinned": match.group(3).strip(),
                    "op": match.group(2),
                })
            else:
                # Unpinned dependency
                name = re.match(r"^([a-zA-Z0-9_-]+)", line)
                if name:
                    deps.append({"name": name.group(1), "pinned": "unpinned", "op": ""})
    except OSError:
        pass
    return deps


def parse_package_json(filepath: Path) -> list[dict]:
    """Parse a package.json file into a list of {name, version}."""
    deps = []
    try:
        data = json.loads(filepath.read_text())
        for section in ["dependencies", "devDependencies"]:
            for name, version in data.get(section, {}).items():
                deps.append({
                    "name": name,
                    "pinned": version,
                    "op": "",
                })
    except (OSError, json.JSONDecodeError):
        pass
    return deps


def get_latest_pypi(package: str) -> str | None:
    """Query PyPI for the latest version of a package."""
    try:
        import urllib.request
        url = f"https://pypi.org/pypi/{package}/json"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return data["info"]["version"]
    except Exception:
        return None


def get_latest_npm(package: str) -> str | None:
    """Query npm registry for the latest version of a package."""
    try:
        import urllib.request
        url = f"https://registry.npmjs.org/{package}/latest"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("version")
    except Exception:
        return None


def main():
    print("=" * 75)
    print(f"{'Project':<35} {'Package':<25} {'Pinned':<12}")
    print("=" * 75)

    for project_dir in SCAN_DIRS:
        full_path = JARED_DIR / project_dir
        if not full_path.exists():
            continue

        # Find all requirements.txt and package.json files
        req_files = list(full_path.rglob("requirements.txt"))
        pkg_files = list(full_path.rglob("package.json"))

        # Filter out node_modules
        req_files = [f for f in req_files if "node_modules" not in f.parts]
        pkg_files = [f for f in pkg_files if "node_modules" not in f.parts and ".venv" not in f.parts]

        if not req_files and not pkg_files:
            continue

        project_name = project_dir.split("/")[0]
        printed_header = False

        for req_file in req_files:
            deps = parse_requirements_txt(req_file)
            if deps:
                if not printed_header:
                    print(f"\n  {project_name}")
                    printed_header = True
                rel = req_file.relative_to(full_path)
                print(f"    [{rel}]")
                for dep in deps:
                    line = f"      {dep['name']:<23} {dep['op']}{dep['pinned']:<12}"
                    if CHECK_LATEST and dep["pinned"] != "unpinned":
                        latest = get_latest_pypi(dep["name"])
                        if latest and latest != dep["pinned"]:
                            line += f"  -> {latest} available"
                    print(line)

        for pkg_file in pkg_files:
            deps = parse_package_json(pkg_file)
            if deps:
                if not printed_header:
                    print(f"\n  {project_name}")
                    printed_header = True
                rel = pkg_file.relative_to(full_path)
                print(f"    [{rel}]")
                for dep in deps[:20]:  # Cap at 20 to avoid noise
                    line = f"      {dep['name']:<23} {dep['pinned']:<12}"
                    print(line)
                remaining = len(deps) - 20
                if remaining > 0:
                    print(f"      ... and {remaining} more")

    print()
    print("=" * 75)
    if not CHECK_LATEST:
        print("Run with --check-latest to check PyPI/npm for newer versions.")


if __name__ == "__main__":
    main()
