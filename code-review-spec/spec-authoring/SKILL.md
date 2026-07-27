---
name: spec-authoring
description: >-
  The source role of the reliable-testing system: turn a user's request into a
  minimal, intent-based spec that the coding and review-gate skills both work
  from. Use this whenever you need to capture what to build as a spec of intents
  before implementation — especially when a coding-agent / review-agent workflow
  will consume it. Trigger it on requests like "write the spec for this",
  "turn these requirements into intents", "define what we're building before we
  code", or as the first step of the reliable-testing pipeline. It makes you
  state outcomes (not implementation or test methods), tag each intent's risk so
  the test level is derivable, keep the spec minimal, and check ONLY the genuinely
  ambiguous points with the human instead of over-specifying. Load
  `reliable-testing-core` alongside it. Not for freeform brainstorming — this
  produces a concrete spec artifact.
---

# Spec Authoring (the source role)

You turn a user's request into a **spec**: a list of intents, each an outcome stated in observable
terms, tagged with risk attributes. Two independent agents downstream — the **coding** agent and the
**review-gate** — will both work from this spec without talking to each other. So the spec is the
one shared anchor that lets them line up. Your job is to make it a *faithful, minimal* statement of
what the user wants — not a pile of conditions.

## Prerequisite: load the shared core

Load **`reliable-testing-core`** first. It defines the spec shape, the risk attributes, and the
risk-tier rule the downstream agents will apply. Conform to that shape; the core is authoritative.

## Two principles that shape everything you write

### 1. You capture intent — you do not perfect it
Whether the spec is ultimately *right* (matches what the user truly needs) is **external
correctness**, and that's closed by the human actually using the result and finding it wrong, which
opens the next round. Your job is a faithful, minimal statement of intent as understood *now* — not
a guarantee it's the correct intent. Don't agonize over covering every hypothetical; capture what's
asked, flag what's genuinely unclear, and let real use validate the rest. Trying to make the spec
"provably correct" up front is how specs bloat.

### 2. Minimal beats maximal — every extra condition is a future liability
The spec states **outcomes**, never implementation and never test method. Pinning down conditions
the user didn't actually need doesn't add safety — it invites the coding agent to game those
conditions instead of fulfilling the real goal, and it strips the agent of the freedom to solve the
problem well. When in doubt, leave it out and let the intent stand on the outcome.

## Drafting workflow

1. **Extract intents from the request.** For each thing the user wants, write it as an *outcome*
   observable from outside the system (a user-visible result, an API response, a stored value). If
   you can't state how you'd observe it, it's not yet an intent — sharpen it. Give each a **stable
   `id`** (`INT-1`, `INT-2`, …) — downstream agents reference intents by id, so don't renumber them
   later.
2. **Tag risk attributes.** For each intent set `user_visible` and `sensitivity` (money / data-loss
   / security / core-promise / none). These exist *only* so the downstream tier is derivable — you
   are not choosing a test level, you're supplying the facts the rule needs.
3. **Minimize.** Strip anything that's implementation detail, test method, or a condition that
   doesn't correspond to a real user-facing outcome. Ask of each line: "if I delete this, does a
   user-observable promise disappear?" If no, delete it.
4. **Confirm only the genuine ambiguities** (below).

## When to ask the human vs. decide yourself

This is the heart of the role, and it's where over-eager humans usually damage a project. Default to
**deciding yourself**; escalate sparingly.

**Ask the human ONLY when** an ambiguity would change *what gets built* or *an intent's risk
attribute*, AND you cannot resolve it from context or a reasonable default. Example worth asking:
"When a payment partially fails, should the whole order roll back or keep the succeeded items?" —
different intents, and it touches money.

**Decide yourself (don't ask) when:** a sensible default exists, it's an implementation choice, it's
style/wording, or it's a low-stakes detail. Asking anyway recreates the exact problem this system
guards against — a human dumping conditions and pinning things down that didn't need pinning.

**How to ask, when you do:** be specific, offer concrete options, and give your recommendation, so
the human's load is a quick yes/no rather than open-ended design work. Batch genuine questions; don't
interrogate one at a time.

## What not to do

- **Don't specify implementation or test method.** "Reject negative amounts" is an intent; "validate
  in `checkAmount()` and unit-test it" is not your call.
- **Don't inflate.** Conditions the user didn't ask for become gaming targets downstream and noise
  for the reviewer.
- **Don't chase provable correctness.** A faithful, minimal spec that a human can validate by using
  the result beats an exhaustive one that pins the wrong things.
- **Don't leave risk attributes unstated.** If `user_visible`/`sensitivity` can't be determined, the
  downstream tier can't be derived and the whole gate loses its footing — that's the one thing you
  must always pin down.

## Handoff

Create a folder for this round and write the spec inside it, in the **target project**:
`docs/specs/<slug>/<slug>.md`, in the format defined in the core's `references/contracts.md` (one
block per intent: `id`, `intent`, `observable`, `user_visible`, `sensitivity`). The coding agent's
manifest and the reviewer's verdict will later join it in the same `<slug>/` folder. Version it
alongside the code.

**Before handing off, run the format validator and fix any errors until it passes:**

```
python <reliable-testing-core>/scripts/validate_spec.py docs/specs/<slug>/<slug>.md
```

This catches structural breaks (bad `id`, wrong `sensitivity` value, a stray `tier` field, a missing
field) before they reach the coding and review agents — where a malformed spec would otherwise cause
silent mis-alignment. It only checks structure, not whether your content is right; that's still your
judgement and the human's.

It goes to the coding agent (who implements + tests from it) and the review-gate (who independently
re-derives intents from it). Neither should need to ask you what you meant — if they would, the
ambiguity belonged in your "confirm with the human" step.
