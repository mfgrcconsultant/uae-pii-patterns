"""CLI: python -m uae_pii [file] [--json] [--min-confidence medium] [--no-mask]"""
from __future__ import annotations

import argparse
import json
import sys

from .detectors import detect, mask


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="uae-pii", description="Scan text for UAE PII.")
    p.add_argument("file", nargs="?", help="File to scan (default: stdin)")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--min-confidence", default="low", choices=["low", "medium", "high"])
    p.add_argument("--no-mask", action="store_true", help="Show full values (avoid on real data)")
    args = p.parse_args(argv)

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    matches = detect(text, min_confidence=args.min_confidence)
    rows = [{**m.to_dict(), "value": m.value if args.no_mask else mask(m.value)} for m in matches]

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        if not rows:
            print("No UAE PII found.")
        for r in rows:
            print(f"{r['confidence']:<7} {r['entity']:<18} {r['value']:<32} @ {r['start']}-{r['end']}")
    return 1 if rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
