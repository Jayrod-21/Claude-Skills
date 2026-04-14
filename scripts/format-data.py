#!/usr/bin/env python3
"""Convert between CSV, JSON, and JSONL formats.

Usage:
  python3 format-data.py input.csv --to json -o output.json
  python3 format-data.py input.json --to csv -o output.csv
  python3 format-data.py input.json --to jsonl -o output.jsonl
  python3 format-data.py input.csv --to json  (prints to stdout)
"""

import argparse
import csv
import io
import json
import sys
from pathlib import Path


def read_csv(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8-sig")  # Handle BOM
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def read_json(filepath: Path) -> list[dict]:
    data = json.loads(filepath.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Try common wrapper keys
        for key in ["data", "results", "items", "records", "rows"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return []


def read_jsonl(filepath: Path) -> list[dict]:
    records = []
    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def write_csv(records: list[dict], output: Path | None):
    if not records:
        print("No records to write.", file=sys.stderr)
        return

    fieldnames = list(records[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

    if output:
        output.write_text(buf.getvalue(), encoding="utf-8")
        print(f"Wrote {len(records)} records to {output}")
    else:
        print(buf.getvalue())


def write_json(records: list[dict], output: Path | None):
    text = json.dumps(records, indent=2, ensure_ascii=False)
    if output:
        output.write_text(text, encoding="utf-8")
        print(f"Wrote {len(records)} records to {output}")
    else:
        print(text)


def write_jsonl(records: list[dict], output: Path | None):
    lines = [json.dumps(r, ensure_ascii=False) for r in records]
    text = "\n".join(lines) + "\n"
    if output:
        output.write_text(text, encoding="utf-8")
        print(f"Wrote {len(records)} records to {output}")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(description="Convert between CSV, JSON, and JSONL")
    parser.add_argument("input", type=Path, help="Input file path")
    parser.add_argument("--to", required=True, choices=["csv", "json", "jsonl"], help="Output format")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output file (stdout if omitted)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    # Auto-detect input format
    suffix = args.input.suffix.lower()
    if suffix == ".csv":
        records = read_csv(args.input)
    elif suffix == ".jsonl":
        records = read_jsonl(args.input)
    elif suffix == ".json":
        records = read_json(args.input)
    else:
        print(f"Error: Unknown input format '{suffix}'. Use .csv, .json, or .jsonl", file=sys.stderr)
        sys.exit(1)

    print(f"Read {len(records)} records from {args.input}", file=sys.stderr)

    # Write output
    writers = {"csv": write_csv, "json": write_json, "jsonl": write_jsonl}
    writers[args.to](records, args.output)


if __name__ == "__main__":
    main()
