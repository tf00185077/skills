---
name: reviewspec-converge
disable-model-invocation: true
description: Phase 2 of the reviewspec chain — converge. Turn an explored problem into a minimal, intent-based spec the user approves, in reviewspec-core's format. Invoke by name, or via reviewspec-dispatch.
---

# reviewspec · Converge (phase 2)

Turn the explored problem into a **spec the user approves** — a minimal list of intents, each an
outcome in observable terms, risk-tagged so downstream tiers are derivable. Two independent agents
later work from this spec without talking to each other (the design reviewer, then the coding
agent and its reviewer), so the spec is the shared anchor that lets them line up.

## Prerequisite: load the core

Load **`reviewspec-core`** first — it defines the spec shape, the risk attributes, and the
risk-tier rule everyone downstream applies. Conform to that shape; the core is authoritative.

## Do

- Read `docs/reviewspec/<build>/explore.md` (phase 1) and `docs/decisions/<system>.md` first.
- **Extract intents from the problem.** For each thing the user wants, write it as an *outcome*
  observable from outside (a user-visible result, an API response, a stored value). Give each a
  stable `id` (`INT-1`, `INT-2`, …) — never renumbered.
- **Tag risk attributes** on each intent: `user_visible` (yes/no) and `sensitivity`
  (money | data-loss | security | core-promise | none). These exist *only* so the tier is
  derivable — you are not choosing a test level.
- **Minimize.** Strip anything that is implementation detail, test method, or a condition with no
  real user-facing outcome. Of each line ask: "if I delete this, does a user-observable promise
  disappear?" If no, delete it. Over-specifying invites gaming downstream.

## Provenance & how much to ask

Anyone's word is a claim, not proof — including the user's and your own reading of the request. A
claim about how the system behaves is settled only when you find the evidence in the repo; if you
can't, keep it an **open question** for phase 3, don't record it as fact.

**Default to deciding yourself; escalate sparingly.** Ask the human ONLY when an ambiguity would
change *what gets built* or *an intent's risk attribute* AND you can't resolve it from context or a
sensible default. When you do ask: be specific, offer concrete options, give your recommendation,
and **batch** the genuine questions — don't interrogate. (A sensible default, an implementation
choice, or wording is *yours* to decide, not a question.)

## Hand off, then stop

On the user's approval, write the spec `docs/reviewspec/<build>/spec.md` in the core's format —
one block per intent:

```markdown
# Spec: <build>
Context: <1-2 lines of what this is>

## INT-1: <short intent title>
- intent: <the outcome>
- observable: <how it's observed from outside>
- user_visible: yes | no
- sensitivity: money | data-loss | security | core-promise | none
```

**Run the format validator and fix errors until it passes** (structure only, not content):
```
python <reviewspec-core>/scripts/validate_spec.py docs/reviewspec/<build>/spec.md
```

**Gate to advance (→ phase 3):** `spec.md` exists, passes the validator, **and the user approved
it**.

**This phase does not implement, and does not skip to implementation.** After approval, stop — the
next phase is the adversarial design review (`reviewspec-design-review`), run by a *different*
agent, not code. Going design → code past the review is the exact failure this chain prevents.
