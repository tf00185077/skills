#!/usr/bin/env python3
"""Build the cross-round intent registry from per-round review files.

Regression guard (see ../references/contracts.md, "Cross-round rules"): once an
intent has been certified PASS by the review-gate, it becomes a standing
contract -- later rounds must not silently break it. To enforce that, we need a
single collection point listing every intent ever certified and the test that
guards it.

Rather than maintain a separate ledger (which would drift from the reviews),
this script DERIVES that collection point from the per-round review files, which
remain the single source of truth. It scans docs/reviewspec/*/review.md,
reads each PASS verdict's registry-readable coverage table, and writes a
generated docs/reviewspec/REGISTRY.md.

The script aggregates and lints structure. It does NOT run the test suite -- so
it cannot itself confirm the guarding tests still PASS. That runtime check is
the review-gate's job each round; this registry gives it the checklist of what
must stay green.

Usage:
    python build_registry.py                   # scan docs/reviewspec/ under cwd
    python build_registry.py <reviewspec_dir>  # scan a given reviewspec directory

Exit code 0 if the registry built cleanly, 1 if a structural problem was found
(unparseable PASS review, duplicate <slug>/<id> key).
"""

from __future__ import annotations

import datetime
import glob
import os
import re
import sys

VERDICT_RE = re.compile(r"^\s*verdict\s*:\s*(.+?)\s*$", re.IGNORECASE)
COVERAGE_COLS = {"intent", "tier", "guarding_test", "status"}


def _clean(cell: str) -> str:
    return cell.strip().strip("*`").strip()


def _parse_verdict(lines: list[str]) -> str | None:
    for ln in lines:
        m = VERDICT_RE.match(ln)
        if m:
            return _clean(m.group(1)).upper()
    return None


def _parse_coverage_rows(lines: list[str]) -> list[dict[str, str]] | None:
    """Find the coverage table by its header and return its rows.

    Returns None if no coverage table is present.
    """
    header_idx = None
    col_order: list[str] = []
    for i, ln in enumerate(lines):
        if "|" not in ln:
            continue
        cells = [_clean(c).lower() for c in ln.strip().strip("|").split("|")]
        if COVERAGE_COLS.issubset(set(cells)):
            header_idx = i
            col_order = cells
            break
    if header_idx is None:
        return None

    rows: list[dict[str, str]] = []
    for ln in lines[header_idx + 1:]:
        if "|" not in ln:
            break
        raw = [_clean(c) for c in ln.strip().strip("|").split("|")]
        # skip the markdown separator row (---|---|...)
        if all(set(c) <= set("-: ") for c in raw):
            continue
        if len(raw) != len(col_order):
            break
        rows.append(dict(zip(col_order, raw)))
    return rows


def _slug_of(review_path: str) -> str:
    # docs/reviewspec/<build>/review.md  ->  the folder name (<build>) keys the intent
    return os.path.basename(os.path.dirname(review_path))


def build(specs_dir: str) -> tuple[str, list[str], int]:
    """Return (registry_markdown, warnings, active_count)."""
    review_paths = sorted(glob.glob(os.path.join(specs_dir, "*", "review.md")))
    warnings: list[str] = []
    # key: "<slug>/<id>" -> entry dict
    entries: dict[str, dict[str, str]] = {}

    for path in review_paths:
        slug = _slug_of(path)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            warnings.append(f"cannot read {path}: {e}")
            continue

        verdict = _parse_verdict(lines)
        if verdict is None:
            warnings.append(f"{path}: no 'Verdict:' line found")
            continue
        if verdict != "PASS":
            # FAIL / SPEC-AMBIGUITY rounds contribute no certified intents.
            continue

        rows = _parse_coverage_rows(lines)
        if not rows:
            warnings.append(
                f"{path}: verdict PASS but no registry-readable coverage table "
                f"(need columns: {', '.join(sorted(COVERAGE_COLS))})"
            )
            continue

        for row in rows:
            intent_id = row.get("intent", "").strip()
            if not intent_id:
                continue
            key = f"{slug}/{intent_id}"
            if key in entries:
                warnings.append(f"duplicate registry key '{key}' (in {path})")
            entries[key] = {
                "slug": slug,
                "intent": intent_id,
                "tier": row.get("tier", ""),
                "guarding_test": row.get("guarding_test", ""),
                "status": (row.get("status", "active") or "active").lower(),
                "review": path.replace("\\", "/"),
            }

    active = [e for e in entries.values() if e["status"] != "superseded"]
    active.sort(key=lambda e: (e["slug"], e["intent"]))
    superseded = sorted(
        (e for e in entries.values() if e["status"] == "superseded"),
        key=lambda e: (e["slug"], e["intent"]),
    )

    now = datetime.date.today().isoformat()
    out: list[str] = []
    out.append("# Intent Registry")
    out.append("")
    out.append(
        "> GENERATED by `reviewspec-core/scripts/build_registry.py` from the "
        "per-round `*.review.md` files. DO NOT EDIT BY HAND — rerun the script."
    )
    out.append(f"> Generated: {now}")
    out.append("")
    out.append("## Active intents (regression contract — each must keep a passing test)")
    out.append("")
    if active:
        out.append("| key | tier | guarding_test | review |")
        out.append("|-----|------|---------------|--------|")
        for e in active:
            out.append(
                f"| {e['slug']}/{e['intent']} | {e['tier']} | {e['guarding_test']} | {e['review']} |"
            )
    else:
        out.append("_None yet._")
    out.append("")
    out.append(f"**Active intents: {len(active)}.** "
               "The review-gate must confirm every one still has a passing test each round; "
               "a lost or failing guarding test is a regression (FAIL), unless the intent was "
               "formally superseded via a spec amendment.")
    out.append("")
    if superseded:
        out.append("## Superseded intents (kept for audit)")
        out.append("")
        out.append("| key | tier | review |")
        out.append("|-----|------|--------|")
        for e in superseded:
            out.append(f"| {e['slug']}/{e['intent']} | {e['tier']} | {e['review']} |")
        out.append("")

    return "\n".join(out) + "\n", warnings, len(active)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    specs_dir = argv[0] if argv else os.path.join("docs", "reviewspec")
    if not os.path.isdir(specs_dir):
        print(f"specs directory not found: {specs_dir}")
        return 1

    registry_md, warnings, active_count = build(specs_dir)
    out_path = os.path.join(specs_dir, "REGISTRY.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(registry_md)

    print(f"Registry written: {out_path}")
    print(f"Active intents: {active_count}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  [warn]  {w}")
        return 1
    print("No structural problems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
