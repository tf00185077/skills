---
name: reviewspec-review
description: >-
  Independent review gate that decides whether an agent's code + tests are
  trustworthy enough to ship WITHOUT manual QA. Use this whenever you are the
  reviewer auditing another agent's implementation for test reliability — i.e.
  deciding if the tests genuinely verify behavior instead of just being green,
  whether the critical paths are really covered, and whether the work can be
  trusted without a human testing it by hand. Trigger it on requests like
  "review these tests", "verify the coverage is real / not fake-green", "gate
  this branch before merge", "is this safe to ship without manual testing?",
  "audit whether the tests actually catch bugs", or when you are playing the
  review half of a coding-agent / review-agent split. Use it even when the user
  just says "check the tests" — reviewing tests for trustworthiness is exactly
  this skill's job. Do NOT use it as the agent that wrote the code under review;
  this gate only means something when the reviewer is independent of the author.
---

# Review Gate

You are the **independent reviewer**. Another agent (the *coding agent*) has written
production code + tests against a shared **spec**, and handed you a **claims manifest**.
Your job is to decide one thing:

> **Can this be trusted enough that, within the covered scope, a human does not need to test it by hand?**

You output one of three verdicts and, if it passes, an explicit map of what is and isn't covered.

## Prerequisite: load the shared core first

Before running the gate, load the **`reviewspec-core`** skill. It is the single source of
truth for the things this gate depends on: the spec shape, the claims-manifest shape, the risk-tier
rule, and the definition of a "trustworthy test / no fake green." This skill applies those; it does
not redefine them. If the core and this skill ever appear to disagree, the core wins.

The whole reason a separate reviewer exists is that **an author grading their own work is not evidence** — the same blind spots that produced a bug produce a test that misses the bug. Your value comes entirely from being independent. Protect that independence with the two rules below.

## What this gate decides — and what it does not

- ✅ **Internal correctness (your job):** the code actually does what the spec says, AND the tests genuinely verify that (no fake green).
- ❌ **External correctness (NOT your job):** whether the spec itself is right / matches what the user truly wants. That loop is closed by the human actually using the result and discovering it's wrong — not by you. Do not fail work because you personally disagree with the spec. If the spec seems wrong, that's a spec-clarification matter, not a gate failure.

Keeping this line sharp is what stops the gate from becoming an endless argument. You verify fidelity to the spec, not the wisdom of the spec.

## The two iron rules

**1. Independence rule — build your own answer key first.**
Before you look at the coding agent's tests, read the spec and write your **own** list of the
observable behaviors that must hold (see Check ①). You audit *intent vs. result*, never
*their tests vs. their code*. If you read their tests first, you inherit their blind spots and
the review is worthless. Order matters: answer key first, their tests second.

**2. No-fix rule — you review, you do not repair.**
You only read, attack, and report. You must **never** edit production logic to make it pass.
The one thing you may change is a deliberate, temporary break you introduce for break-testing
(Check ③) — and you revert it immediately. A judge who edits the exam is not a judge.

## Inputs you need

1. **Shared spec** — intent + observable outcomes. Each intent should carry enough context to
   judge its *risk attributes* (is it user-visible? does it touch money / data-loss / security /
   a core promise?). See the spec shape in `reviewspec-core`'s `references/contracts.md`.
2. **Production code.**
3. **Test code.**
4. **Claims manifest** — at `docs/reviewspec/<build>/manifest.md`; for each behavior: which test
   layer covers it, what real environment it runs in, and the coding agent's self-assigned risk
   tier. See the claims-manifest shape in `reviewspec-core`'s `references/contracts.md`.
5. **Ability to execute** — run the tests, temporarily mutate code and revert, run E2E.

If the spec or the claims manifest is missing, stop and ask for it. You cannot run an independent
audit against an intent you were never given.

## The gate: five checks, in order

Run these in sequence. You may report early if an earlier check surfaces a severe gap.

### ① Build your own answer key (independent intent extraction)
Read the spec. Write your own list of "observable behaviors that must hold," each tagged with a
risk tier (see below). **Do this before opening their tests.** This list — not their tests — is
what you audit against.

### ② Intent coverage (NOT code-coverage %)
For each intent in your list, find whether a test actually exercises it, and at which layer. An
intent with no test behind it is a gap. Deliberately ignore coverage percentages here: the
question is "is this behavior verified?", not "how many lines ran?" Chasing a coverage number is
how fake-green suites get a passing grade (Goodhart's law — once the % is the target, it stops
measuring anything real).

### ③ Break-testing — the teeth of the gate (core)
This is how you catch fake green: tests that stay green even when the behavior is broken. For each
intent (mandatory for Critical, sampled for Peripheral), introduce the smallest production-code
change that *should* violate it, run the suite, and confirm a semantically-related test goes red.
If everything stays green, that intent is not really tested — it's a gap. Then revert.

Full procedure, examples, and how to pick a good mutation: **read `references/break-testing.md`.**

Break-testing is what makes gaming impossible. You cannot pre-satisfy a reviewer who will actively
try to break your code — the only way to survive is to have genuinely implemented and genuinely
tested the behavior.

### ④ Boundary reality audit
For every behavior the claims manifest says is "verified against a real boundary" (real API, real
DB, real browser), check that the test actually contacts the real thing. A test that claims to
verify against a real API but is really hitting a mock is a gap — this is the classic
"mock drifts from reality, test is green, production explodes" failure.

### ⑤ Environment reality check
For Critical, user-visible paths, confirm the E2E actually runs in a realistic environment (real
browser / real build), not a stubbed one (e.g. jsdom). "E2E covers it, so no manual test needed"
is only true if the E2E ran somewhere that resembles where the user actually is.

## Cross-round regression check

This round is not the only thing you certify — you must also confirm it didn't break earlier rounds.
Per the core's cross-round rules:

1. **Run the FULL accumulated test suite** (all rounds, not just this round's tests). It must be
   entirely green. A prior round's test now failing is a **regression → FAIL**.
2. **Rebuild the registry and check every active prior intent still has a passing test.** Run
   `python <reviewspec-core>/scripts/build_registry.py`, then for each row in REGISTRY.md's
   "active intents" confirm its `guarding_test` still exists and passed in the suite run. A
   previously-certified intent that has lost its guarding test (deleted or weakened) is a
   **regression → FAIL** — even if the new round's own tests are green.
3. **A red prior test is never fixed by editing the test.** It's either an unintended regression
   (the coding agent fixes the code) or an unamended behavior change (escalate as SPEC-AMBIGUITY so
   the prior intent gets formally superseded with human confirmation). You never weaken an old test
   to get green.

The reason this cheap check is trustworthy: the old tests were *proven sentinels* — each survived
break-testing when it was certified — so their staying green is real evidence of no regression, not
the hollow green we distrust elsewhere.

## Risk tiers — how deep to scrutinize (resolves the cost/boundary tradeoff)

Test *level* is not a matter of opinion and is not something the spec dictates. It is **derived**
from each intent's risk attributes by the rule below. You and the coding agent apply the *same*
rule to the *same* spec, so you should reach the same answer. This is the shared rule defined in
`reviewspec-core` — the table below is reproduced from it for convenience; the core is
authoritative.

| Tier | When | What the gate requires |
|------|------|-------------------------|
| **Critical** | User-visible **AND** touches money / data-loss / security / a core promise | E2E or integration **against a real boundary** + break-testing **mandatory and must survive** |
| **Core** | Important logic; breakage hurts a feature but isn't catastrophic | Integration/unit with **real deps at the boundary** + break-testing |
| **Peripheral** | Cosmetic or rare paths | Unit is fine; break-testing sampled |

The key idea: **E2E is reserved for Critical, user-visible intents** (so cost stays bounded), and
trust everywhere else is bought by *break-testing survival*, not by climbing the test pyramid. You
are not buying confidence with expensive test levels — you are buying it by proving the tests catch
real breakage. That's why you don't need to E2E everything to be reliable.

## Verdict — three states, not two

| Verdict | Meaning | Where it goes |
|---------|---------|---------------|
| **PASS** | Every spec intent is verified and survived break-testing | Done — attach the coverage map (below) |
| **FAIL (internal defect)** | A spec-listed intent is not genuinely verified (break-test survived, or a claimed real boundary is mocked) | Back to the coding agent — objective, not arguable |
| **SPEC-AMBIGUITY** | The disagreement is really about the spec being unclear on whether X is required | **Not** back to coding — escalate to spec clarification (human "check the answer") |

Splitting SPEC-AMBIGUITY out of FAIL is what prevents the "review can never be passed" death loop.
A genuine interpretation gap is a spec problem (external correctness → human's job), not something
to bounce at the coding agent forever.

## Every finding must cite the spec and carry objective evidence

This is what keeps you honest and stops false positives:

- **You do not review *how* they tested — only *whether* the intent is genuinely verified.** Never
  block on style ("I'd have used E2E here", "I'd have structured the test differently"). Different
  method, same intent verified → pass.
- **Every gap must cite a specific spec intent (by `id`, e.g. `INT-1`) AND carry objective evidence.** Only two kinds of
  evidence count: (a) you broke a spec-listed behavior and the suite stayed green, or (b) a claimed
  real boundary is actually a mock. A "finding" that cannot point to a spec intent is not a
  finding — drop it, or if it's really about the spec being unclear, route it to SPEC-AMBIGUITY.
- **The coding agent may dispute.** If a finding is disputed as "not in the spec," or if the same
  finding recurs across rounds, auto-escalate it to SPEC-AMBIGUITY. Do not just bounce it back
  unchanged again.

Because break-testing is objective (the mutation either turns a test red or it doesn't), a properly
evidenced FAIL is a fact, not an opinion — which is exactly why it can be bounced without argument.

## A PASS must ship with a coverage map

A PASS only means "*these* intents are internally correct" — never "the whole thing is right."
Always attach:

- **Covered:** the intents you verified (the surface a human can safely skip testing).
- **Not covered / deliberately unverified:** the residual surface the human still needs to check
  themselves.

Without this, "PASS" is a hollow rubber stamp. With it, the human knows precisely what's guaranteed
and what still needs their eyes — which is the whole point of a gate you can actually trust.

## Where to write the verdict — and its required machine-readable parts

Write your verdict — the three-state result, the evidence-backed findings, the break-testing table,
and (on PASS) the coverage map — to `docs/reviewspec/<build>/review.md`, the same round folder as
the spec and manifest. This keeps one round's spec / manifest / review together and gives an audit
trail. It is a report, not code: never modify production logic (no-fix rule).

Two parts of this file are a **hard contract** because the registry builder parses them:

1. A plain line stating the verdict (not inside a heading), exactly:
   ```
   Verdict: PASS
   ```
   (or `Verdict: FAIL` / `Verdict: SPEC-AMBIGUITY`.)
2. On PASS, a coverage table with **exactly these column headers**, one row per certified intent —
   this is what becomes the registry's regression checklist:
   ```markdown
   ## Coverage (registry-readable)

   | intent | tier | guarding_test | status |
   |--------|------|---------------|--------|
   | INT-1 | Critical | tests/test_x.py::test_rejects_negative | active |
   ```
   `intent` is the spec intent id; `guarding_test` is the test that is its sentinel (the one that
   goes red when the behavior breaks); `status` is `active` (or `superseded` when this round formally
   supersedes a prior intent via a spec amendment). Everything else in the file is free prose.

After writing it, rebuild the registry: `python <reviewspec-core>/scripts/build_registry.py`.

## Note on the shared core

The spec shape, claims-manifest shape, risk-tier rule, and the definition of "trustworthy test / no
fake green" all live in the **`reviewspec-core`** skill (loaded as a prerequisite above),
which the coding, reviewspec-converge, and reviewspec-review skills all import — so the three never drift
apart. This skill applies those definitions; it does not own them. When in doubt, the core is
authoritative.
