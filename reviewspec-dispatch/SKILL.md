---
name: reviewspec-dispatch
disable-model-invocation: true
description: Dispatcher for the reviewspec chain. Locates which phase a build is at (from on-disk artifacts) and routes to that phase's skill — diverge → converge → design-review → build → review — gating each and handing off to a fresh session at every independence boundary. Invoke by name to run or resume.
---

# reviewspec · Dispatch (the router)

Routes **one build** through five phases, each a separate skill, and **will not let a phase start
until the previous one's gate has cleared.** It does not do the phases' work — it locates the
current phase, routes to that phase's skill, records the gate, and advances.

Two adversarial gates make this chain trustworthy: **design-review** (is the abstraction right,
before code) and **review** (do the tests genuinely verify it, after code). Neither is optional.

## When to run

For a **structural build** — a new system, or a change crossing a subsystem boundary, setting a
failure policy, defining a cross-party contract, or adding a recovery path. Not for a trivial
local change.

## Locate the current phase (every invocation)

State lives on disk, so the chain is **resumable across sessions** (which is what makes the
independence boundaries below possible). On invocation:

1. Read `docs/reviewspec/<build>/state.json` if present, then **cross-check against reality** — do
   the artifact files actually exist? If state and filesystem disagree, **the filesystem wins.**
2. **Derive the phase = the first gate not yet cleared:**

   | Artifacts present | Phase | Skill |
   |---|---|---|
   | none | **1 diverge** | `reviewspec-diverge` → `explore.md` |
   | explore.md | **2 converge** | `reviewspec-converge` → `spec.md` |
   | spec.md | **3 design-review** | `reviewspec-design-review` → `design-review.md` |
   | design-review.md | **4 build** | `reviewspec-build` → code + `manifest.md` |
   | manifest.md (no PASS review) | **5 review** | `reviewspec-review` → `review.md` |
   | review.md = `Verdict: PASS` | **done** | — |

3. If genuinely ambiguous, **ask the user** which phase. Otherwise announce the derived phase and
   proceed.

## The gates — record after each phase; never skip

- **G1** → explore.md exists and the problem is crisp.
- **G2** → spec.md exists, passes `validate_spec.py`, **and the user approved it** (a decision — ask).
- **G3** → design-review.md exists and its review **cleared** (no unresolved load-bearing risk).
- **G4** → code + manifest.md exist and the full accumulated test suite is green.
- **G5** → review.md carries `Verdict: PASS`.

**If unsure whether a gate is met, it is not.** Phase 2 hands to phase 3, not to code.

## Independence — hand off to a FRESH SESSION (author ≠ judge)

The gates only mean something if the reviewer is not the author. So the chain runs across **four
separate agent lineages**, and at three boundaries the dispatcher **stops and hands off to a new
session** (a new session, not a subagent — a subagent carries the caller's context and isn't
clean):

| Lineage | Phases | 
|---|---|
| **author** | 1 diverge · 2 converge |
| **design reviewer** | 3 design-review — **new session** |
| **implementer** | 4 build — **new session** |
| **code reviewer** | 5 review — **new session** |

At each boundary, stop and say, e.g.:
> "Phase 2 done (`spec.md` approved). Phase 3 must run as an independent agent. **Open a new
> session and run `reviewspec-dispatch`** — it will read the artifacts and continue at phase 3."

The fresh session reads `docs/reviewspec/<build>/` and resumes — the folder *is* the handoff, so
the new agent needs none of the prior conversation.

## Backward edges

- Phase 3 finds the design **mis-framed** → clear G2, return to phase 2 (or phase 1 if the
  *problem* was mis-scoped). Record why.
- Phase 5 returns **FAIL** → back to phase 4 (implementer fixes). **SPEC-AMBIGUITY** → back to
  phase 2 (spec clarification with the human), not to the implementer.

## Project memory (read at the start, append at the close)

Per-subsystem decision memory: `docs/decisions/<system>.md`, one file per subsystem, the single
source of truth for that subsystem's key decisions and why. Format, provenance rules, and the
compaction mechanism are in `references/project-memory.md`.

- **On invocation, before routing:** read `docs/decisions/<system>.md`; don't contradict a prior
  decision silently.
- **After phase 3:** append the run's **load-bearing, cross-build** decisions — decision · why ·
  what it superseded · provenance · a **link** to `design-review.md`; never restate detail.
- **When that file exceeds its size guideline:** run the compaction pass from
  `references/project-memory.md`. Git holds the full pre-compaction history.

## Flow

```
[1 diverge]--G1-->[2 converge]--G2-->[3 design-review]--G3-->[4 build]--G4-->[5 review]--G5-->done
   author              author      | new session         | new session    | new session
      ^                   ^        (design reviewer)      (implementer)    (code reviewer)
      +----- re-scope ----+<------- mis-framed -----------+       FAIL→4 / SPEC-AMBIGUITY→2
```

The five phase skills are independent — each has its own command and runs alone. This dispatcher
is only the router + gatekeeper + memory + session-boundary enforcer; it never re-implements them.
