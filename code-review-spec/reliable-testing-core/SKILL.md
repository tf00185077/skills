---
name: reliable-testing-core
description: >-
  Shared foundation for the reliable-testing skill family (review-gate, coding,
  spec-authoring). It is the single source of truth those skills all depend on,
  so they never drift apart. It defines: the common principles (internal vs.
  external correctness, intent-based minimal specs, test level derived not
  declared, author must differ from reviewer), the definition of a "trustworthy
  test" (no fake green), the risk-tier rule that derives what test level a
  behavior needs from its risk, and the handoff contracts (spec shape and claims
  manifest shape) between a coding agent and a review agent. Load this whenever
  you run any reliable-testing role skill, or when you need the canonical answer
  to "what test level does this behavior require?", "what makes a test
  trustworthy / not fake-green?", or "what should the spec / claims manifest
  contain?". If a reliable-testing role skill tells you to load the core, this
  is it.
---

# Reliable Testing — Shared Core

This is the shared foundation for three role skills:

- **spec-authoring** — turns a request into an intent-based spec.
- **coding** — implements + tests against the spec, emits a claims manifest.
- **review-gate** — independently audits code + tests + spec, and gates.

Those three are separate skills (each loads only its own role's instructions, so roles don't
contaminate each other). This core holds what all three must agree on. **It is the line that keeps
the three from drifting apart** — if a rule about "what counts as a trustworthy test" or "what a
spec must contain" lived in three places, the three would eventually diverge and the whole system
would stop being trustworthy. So it lives here once, and each role imports it.

The overarching goal of the system: after an agent writes code, make the tests trustworthy enough
that — within the covered scope — a human doesn't need to test it by hand. The core insight is that
this is **not** achieved by writing more tests, but by **proving the tests don't lie** (green ≠
correct).

## Principles (every role obeys these)

### 1. Internal correctness vs. external correctness
- **Internal correctness:** the code does what the spec says, AND the tests genuinely verify that.
  This is what the *system* guarantees.
- **External correctness:** whether the spec itself is right / matches what the user truly wants.
  This is **not** the system's job — it is closed by the human actually using the result and
  discovering it's wrong, which opens the next revision round.

Keep this line sharp. It's what lets the system be decisive (it never has to argue about whether the
spec is *wise*, only whether the code is *faithful* to it), and it's what protects the agent from
being crippled by a human's over-specified, possibly-wrong conditions.

### 2. The spec is intent-based and minimal
A spec describes **intent and observable outcomes** — never implementation, never test method.
Over-specifying strips the agent of its strongest ability and invites it to game pinned-down
conditions instead of fulfilling the real goal. The spec's *only* extra duty is to make each
intent's **risk attributes** determinable (see the risk-tier rule).

### 3. Test level is derived, not declared
"Does this need E2E?" is not an opinion and is not written into the spec. It is **derived** from an
intent's risk attributes by the risk-tier rule below. Because every role applies the *same* rule to
the *same* spec, they reach the same answer — so disagreements reduce to a factual question about a
risk attribute, which is either settled by the spec text or (if genuinely unclear) escalated as a
spec-ambiguity, never looped between roles.

### 4. The author is not the judge
The coding agent and the review agent must be **different agents**. An author grading their own work
is not evidence: the same blind spot that produced a bug produces a test that misses it. The gate
only means something when the reviewer is independent of the author.

## Definition: a "trustworthy test" (no fake green)

"Green" proves a test passes. It does **not** prove the test would fail when it should — and that
gap is where fake-green suites live (no assertion, asserting on a mock, or locking in whatever the
code currently does). A test is trustworthy for an intent only when **all three** hold:

1. **Covers the intent** — the observable outcome is actually asserted (not a coincidental pass).
2. **Survives break-testing** — deliberately breaking the behavior turns the test red. (This is how
   you prove the test can catch the bug, not just that it's currently green.)
3. **Real boundary where claimed** — no mock standing in for a dependency the test claims to verify
   against.

The whole system's job is to convert "green" into "green **and** these three hold."

## The risk-tier rule (shared by coding agent AND reviewer)

```
tier(intent):
    if intent.user_visible AND intent.sensitivity in {money, data-loss, security, core-promise}:
        return CRITICAL
    elif breakage_hurts_a_feature(intent):     # important logic, non-catastrophic
        return CORE
    else:                                       # cosmetic / rare
        return PERIPHERAL
```

| Tier | Required scrutiny |
|------|-------------------|
| **Critical** | E2E or integration against a **real boundary** + break-testing **mandatory and must survive** |
| **Core** | Integration/unit with **real deps at the boundary** + break-testing |
| **Peripheral** | Unit is fine; break-testing sampled |

The philosophy: **E2E is bought sparingly (Critical only), so cost stays bounded; trust everywhere
else is bought by break-testing survival, not by climbing the test pyramid.** You don't buy
confidence with expensive test levels — you buy it by proving the tests catch real breakage. That's
what makes "reliable without E2E-ing everything" achievable.

## Handoff contracts

The interchange formats between the roles — spec shape and claims-manifest shape — are in
**`references/contracts.md`**. Read it when authoring a spec, emitting/consuming a claims manifest,
or auditing one.

The spec format is machine-checkable — enforce it with **`scripts/validate_spec.py`** (see
`references/contracts.md` for usage). The spec-authoring agent runs it before handoff; it can also
gate CI.

Cross-round regression is guarded by an intent registry generated from the per-round review files —
**`scripts/build_registry.py`** derives `docs/specs/REGISTRY.md`. The review-gate rebuilds it each
round and confirms every active prior intent still has a passing test. See "Cross-round rules" in
`references/contracts.md`.

## How each role uses this core

- **spec-authoring** writes specs conforming to the spec shape; assigns risk attributes so the tier
  is derivable; keeps intents outcome-based and minimal.
- **coding** derives each intent's tier via the rule, meets the required scrutiny, avoids mocking at
  claimed real boundaries, and emits a claims manifest.
- **review-gate** independently re-derives intents and tiers from the spec, then verifies each
  intent is a *trustworthy test* (the 3 conditions), primarily via break-testing.
