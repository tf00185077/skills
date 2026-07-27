#!/usr/bin/env python3
"""Validate reliable-testing spec files against the hard format contract.

The spec format is a hard interface contract (see ../references/contracts.md):
three independent agents parse and cross-reference these files without talking
to each other, so the *structure* must not vary. This script enforces that
structure so a malformed spec is caught before it reaches the coding or
review-gate agents.

It checks structure only. It does NOT judge whether the spec's content is good
or complete -- that stays a human/agent judgement, deliberately un-pinned.

Usage:
    python validate_spec.py                      # validates docs/specs/*.md under cwd
    python validate_spec.py path/to/spec.md ...  # validates the given files
    python validate_spec.py docs/specs           # validates *.md in a directory

Exit code 0 if every file passes, 1 if any file has errors (warnings don't fail).
"""

from __future__ import annotations

import glob
import os
import re
import sys

REQUIRED_FIELDS = ["intent", "observable", "user_visible", "sensitivity"]
USER_VISIBLE_VALUES = {"yes", "no"}
SENSITIVITY_VALUES = {"money", "data-loss", "security", "core-promise", "none"}

ID_RE = re.compile(r"^INT-\d+$")
INTENT_HEADING_RE = re.compile(r"^##\s+([^:]+?):\s*(.*)$")
FIELD_RE = re.compile(r"^-\s+([^:]+?):\s*(.*)$")
TITLE_RE = re.compile(r"^#\s+Spec:\s*\S+")
CONTEXT_RE = re.compile(r"^Context:\s*\S+")


class Issue:
    def __init__(self, line: int, msg: str, is_error: bool = True):
        self.line = line
        self.msg = msg
        self.is_error = is_error

    def __str__(self) -> str:
        kind = "ERROR" if self.is_error else "warn "
        where = f":{self.line}" if self.line else ""
        return f"  [{kind}]{where}  {self.msg}"


def validate_file(path: str) -> list[Issue]:
    issues: list[Issue] = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        return [Issue(0, f"cannot read file: {e}")]

    # --- structural warnings (title / context) ---
    if not any(TITLE_RE.match(ln) for ln in lines):
        issues.append(Issue(0, "missing '# Spec: <name>' title line", is_error=False))
    if not any(CONTEXT_RE.match(ln) for ln in lines):
        issues.append(Issue(0, "missing 'Context: ...' line", is_error=False))

    # --- split into intent blocks by '## ' headings ---
    # Each block: (heading_lineno, id_token, [(field_lineno, key, value), ...])
    blocks: list[tuple[int, str, list[tuple[int, str, str]]]] = []
    current: tuple[int, str, list[tuple[int, str, str]]] | None = None

    for i, raw in enumerate(lines, start=1):
        heading = INTENT_HEADING_RE.match(raw)
        if heading:
            id_token = heading.group(1).strip()
            current = (i, id_token, [])
            blocks.append(current)
            continue
        # a top-level '# ' heading (e.g. the title) closes any open block
        if raw.startswith("# "):
            current = None
            continue
        field = FIELD_RE.match(raw)
        if field and current is not None:
            key = field.group(1).strip()
            value = field.group(2).strip()
            current[2].append((i, key, value))

    if not blocks:
        issues.append(Issue(0, "no intents found (expected '## INT-<n>: <title>' blocks)"))
        return issues

    seen_ids: dict[str, int] = {}
    for heading_line, id_token, fields in blocks:
        # id format
        if not ID_RE.match(id_token):
            issues.append(
                Issue(heading_line, f"intent id '{id_token}' must match 'INT-<n>' (e.g. INT-1)")
            )
        # duplicate id
        if id_token in seen_ids:
            issues.append(
                Issue(
                    heading_line,
                    f"duplicate intent id '{id_token}' (also at line {seen_ids[id_token]})",
                )
            )
        else:
            seen_ids[id_token] = heading_line

        field_map: dict[str, tuple[int, str]] = {}
        for fline, key, value in fields:
            if key in field_map:
                issues.append(Issue(fline, f"{id_token}: duplicate field '{key}'"))
            else:
                field_map[key] = (fline, value)

        # unknown / forbidden fields
        for fline, key, _value in fields:
            if key not in REQUIRED_FIELDS:
                hint = ""
                if key in ("test_layer", "tier", "test_level", "layer"):
                    hint = " (the spec never states a test level; that's derived downstream)"
                issues.append(Issue(fline, f"{id_token}: unknown field '{key}'{hint}"))

        # missing required fields
        for req in REQUIRED_FIELDS:
            if req not in field_map:
                issues.append(Issue(heading_line, f"{id_token}: missing required field '{req}'"))

        # value checks
        if "intent" in field_map and not field_map["intent"][1]:
            issues.append(Issue(field_map["intent"][0], f"{id_token}: 'intent' is empty"))
        if "observable" in field_map and not field_map["observable"][1]:
            issues.append(Issue(field_map["observable"][0], f"{id_token}: 'observable' is empty"))
        if "user_visible" in field_map:
            fline, val = field_map["user_visible"]
            if val not in USER_VISIBLE_VALUES:
                issues.append(
                    Issue(fline, f"{id_token}: 'user_visible' is '{val}', must be yes|no")
                )
        if "sensitivity" in field_map:
            fline, val = field_map["sensitivity"]
            if val not in SENSITIVITY_VALUES:
                issues.append(
                    Issue(
                        fline,
                        f"{id_token}: 'sensitivity' is '{val}', must be one of "
                        f"{' | '.join(sorted(SENSITIVITY_VALUES))}",
                    )
                )

    return issues


def _is_spec_file(path: str) -> bool:
    """A spec is a `<slug>.md`, not a `.manifest.md` or `.review.md` sibling."""
    low = path.lower()
    return low.endswith(".md") and not (
        low.endswith(".manifest.md") or low.endswith(".review.md")
    )


def resolve_paths(args: list[str]) -> list[str]:
    # Default: every round's spec under docs/specs/<slug>/<slug>.md, skipping
    # the .manifest.md / .review.md siblings in the same folder.
    if not args:
        found = glob.glob(os.path.join("docs", "specs", "*", "*.md"))
        return sorted(p for p in found if _is_spec_file(p))
    paths: list[str] = []
    for arg in args:
        if os.path.isdir(arg):
            # A round folder (or docs/specs) — pick the spec file(s) inside.
            found = glob.glob(os.path.join(arg, "*.md"))
            paths.extend(sorted(p for p in found if _is_spec_file(p)))
        else:
            paths.append(arg)  # explicit file: validate exactly what was named
    return paths


def main(argv: list[str]) -> int:
    # Spec values are often non-ASCII (e.g. Chinese); make sure error messages
    # print them intact regardless of the console's default codepage.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    paths = resolve_paths(argv)
    if not paths:
        print("No spec files found. Pass file paths, a directory, or run where docs/specs/*.md exists.")
        return 1

    any_errors = False
    for path in paths:
        issues = validate_file(path)
        errors = [i for i in issues if i.is_error]
        warns = [i for i in issues if not i.is_error]
        if not issues:
            print(f"PASS  {path}")
            continue
        status = "FAIL" if errors else "PASS (with warnings)"
        print(f"{status}  {path}")
        for issue in sorted(issues, key=lambda x: (x.line, not x.is_error)):
            print(issue)
        if errors:
            any_errors = True

    print()
    print(f"{len(paths)} file(s) checked. {'FAILED' if any_errors else 'All structurally valid.'}")
    return 1 if any_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
