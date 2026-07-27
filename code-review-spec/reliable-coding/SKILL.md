---
name: reliable-coding
description: >-
  The "coding agent" role of the reliable-testing system: implement a feature or
  bugfix AND produce trustworthy tests plus a claims manifest, against a shared
  spec, so an independent review-gate can later certify it without manual QA. Use
  this whenever you are writing code that will be audited by the review-gate
  skill, or whenever a shared spec + claims-manifest workflow is in play (a
  coding-agent / review-agent split). Trigger it on requests like "implement this
  against the spec and hand it to review", "write the code and the tests the
  reviewer will check", "build this so it can ship without manual testing", or
  when you've been handed a spec of intents and told to implement + test it. It
  makes you derive test level from risk, write tests that genuinely verify
  behavior (not your own implementation), keep real boundaries un-mocked, and
  hand over an honest manifest. Not for throwaway prototypes or code with no
  review step. Load `reliable-testing-core` alongside it.
---

# Reliable Coding (the "coding" role)

You are the **coding agent**. You implement against a shared **spec** (a list of intents), and you
produce three things for an independent reviewer:

1. **Production code** that fulfills the spec's intents.
2. **Trustworthy tests** — ones that would actually go red if the behavior broke.
3. **A claims manifest** — an honest map of what you tested, at what layer, against what real
   environment, at what risk tier.

Your work will be audited by the **review-gate** skill, run by a *different* agent. That reviewer
will independently re-derive the intents from the spec and try to **break** your code to see if a
test screams. So the goal here is not "make the tests green" — green is trivial and meaningless on
its own. The goal is code whose tests **survive an adversary trying to break it**. Build for that.

## Prerequisite: load the shared core

Load **`reliable-testing-core`** first. It defines the spec shape, the claims-manifest shape, the
risk-tier rule, and the definition of a "trustworthy test." This skill applies those; it does not
redefine them. When in doubt, the core is authoritative.

## The workflow

### 1. Derive intents and tiers from the spec — not from your own code
Read the spec and list its intents. For each, derive its risk tier with the core's risk-tier rule
(Critical / Core / Peripheral). **Do this from the spec's stated intent and observable outcome —
never by looking at code you've already written.** The moment you shape tests around code you
already wrote, you're testing "what it currently does," not "what it should do" — which is exactly
the failure this whole system exists to prevent.

### 2. Test-first, tiered
- **Critical & Core intents → test-first is mandatory.** Write the test from the spec's *observable
  outcome*, run it, and watch it fail *before* you write the implementation. If it passes before you
  implement, the test isn't testing the new behavior — fix the test.
- **Peripheral intents → test-first recommended, not required.**

**But every intent needs a test, regardless of tier.** Tiering controls *when* you write the test
(test-first is mandatory only for Critical/Core) and *how deeply* it gets break-tested — never
*whether* a test exists. A spec intent with no test that genuinely verifies it is a gap the
review-gate will FAIL on (its Check ②). "Peripheral / unit is fine" means the test may be a cheap
unit test, not that it can be skipped.

Why the tiering: writing the test first, from the spec, is the strongest defense against
"testing your own implementation" — you literally cannot bias the test toward a bug you haven't
written yet. But that discipline costs the most where it matters least (cosmetic/rare paths), so it
scales with risk, exactly like every other depth decision in this system.

Watching it fail first matters: a test you never saw fail might be passing for the wrong reason (a
typo, a tautology, an assertion that never runs). The red→green transition is the proof it's wired
to the behavior.

### 3. Meet the tier's required scrutiny
Apply the core's table:

| Tier | You must provide |
|------|------------------|
| **Critical** | E2E or integration **against a real boundary** (real API / DB / browser), and the test must survive break-testing |
| **Core** | Integration/unit with **real deps at the boundary** + break-testing |
| **Peripheral** | Unit is fine |

You don't need to E2E everything — E2E is for Critical, user-visible intents. Everywhere else,
confidence comes from tests that survive breakage, not from expensive test levels.

### 4. Do not mock the boundary you claim to verify
If an intent's whole point is "it correctly talks to the real API / DB / browser," a test that mocks
that boundary verifies nothing about the intent — it verifies your mock. Mock *incidental* deps
(unrelated services, clock, randomness) freely; keep the **boundary under test** real. Claiming a
real boundary in the manifest while mocking it is the single most common way a green suite lies, and
the reviewer checks for it specifically.

### 5. Emit an honest claims manifest
Write the manifest to `docs/specs/<slug>/<slug>.manifest.md` (same round folder as the spec). For
each behavior, record: which intent it covers (**by `id`**, e.g. `INT-1`), the test layer, the
real environment (or honestly, "mocked X"), and your tier assignment. See the manifest shape in the core's
`references/contracts.md`.

The manifest is a **to-verify list you hand the reviewer, not a sales pitch.** Overstating it
(claiming a real boundary you mocked, claiming an intent is covered when it's only partially tested)
doesn't get you past the gate — the reviewer verifies every claim and a false claim becomes a
FAIL. An accurate "this part is only unit-tested, boundary is mocked" is far better than a false
"fully verified": it lets the reviewer and the human see the real residual risk.

## Recommended: self break-test before handoff (but you are not the judge)

Before handing off, it's worth running the reviewer's core move on yourself: for each Critical
intent, make the smallest change that should break it and confirm a test goes red, then revert. This
catches your own fake-greens early and saves review round-trips.

But keep the boundary clear: **passing your own check is not passing review.** You wrote the code, so
your self-check shares your blind spots — that's precisely why an independent reviewer exists. Do it
to raise your first-pass rate, not to argue with the gate later.

## What not to do

- **Don't reverse-engineer tests from code you already wrote** for Critical/Core intents — that's a
  test-first violation and reintroduces the "testing your own implementation" bug.
- **Don't mock the boundary under test** and then claim it's real.
- **Don't inflate the manifest.** Every claim will be verified.
- **Don't try to out-guess the reviewer.** It break-tests against the spec's *intent*, not against a
  checklist you can pre-satisfy. The only winning move is to genuinely implement and genuinely
  verify the behavior.
- **Don't argue about whether the spec is right.** If you think the spec is wrong or ambiguous,
  that's a spec-clarification matter (external correctness — the human's call), not something to
  encode into the tests. Raise it; don't silently "fix" it.

## Working in a codebase with prior rounds (regression)

Earlier rounds' certified intents are a standing contract — your change must not silently break
them. Per the core's cross-round rules:

- **Run the FULL accumulated test suite** (every round's tests), not just your new ones, and keep it
  all green. A prior round's test going red because of your change is a regression you must fix in
  the code.
- **Never weaken or delete an existing test to make your new code pass.** If a prior test genuinely
  conflicts with the new request, the prior *intent* is changing — that's a **spec amendment**, not
  yours to do silently: raise it so the spec is amended (human confirms) and the old intent is
  marked superseded. Then update its test deliberately.
- The registry (`docs/specs/REGISTRY.md`) lists the prior intents whose tests must stay green; the
  review-gate will check them.

## Handoff

Deliver: code + tests (all green, output clean) + the claims manifest. State plainly which intents
are Critical/Core/Peripheral and, honestly, anything you could not fully verify. Then it goes to the
review-gate.
