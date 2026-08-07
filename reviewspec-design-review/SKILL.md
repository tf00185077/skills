---
name: reviewspec-design-review
disable-model-invocation: true
description: Phase 3 of the reviewspec chain — the design gate. An independent agent stress-tests a spec's failure modes before any code (failure map, tabletop, failure-policy separation, fitness tests). Invoke by name, or via reviewspec-dispatch.
---

# reviewspec · Design Review (phase 3)

## Role in the chain

The **adversarial design gate**, run by an agent independent of whoever wrote the spec. It reviews
the *design* — not code — which in this chain means the spec produced by `reviewspec-converge`.

- **Reads:** `docs/reviewspec/<build>/spec.md` (the design under review) · `docs/reviewspec/<build>/explore.md` · `docs/decisions/<system>.md` (prior decisions) · the existing codebase it integrates with.
- **Writes:** `docs/reviewspec/<build>/design-review.md` — the findings, the go/no-go, and the **fitness tests** `reviewspec-build` must satisfy.
- **Gate:** clears only when no load-bearing risk is unresolved; then the build phase starts as a fresh, independent agent.

Standalone (outside the chain) it reviews any design or structural change the same way — "the spec"
below just means whatever design artifact you point it at.

## What this defends against

The dangerous failures in real systems are usually not "the code is wrong." They are **"the
code correctly implements the wrong abstraction."** Every line is correct; the whole thing
solves a subtly wrong problem.

**Tests cannot catch this, and here is the exact reason.** A test proves that the code does
what its rules say. But the rules and the tests are written from the *same mental model*, in
the *same session*, by the *same author*. If the model is wrong, the code is wrong **and** the
test that "verifies" it is wrong — they fail together and pass together. They are *correlated*.
You cannot catch a correlated error with more of the same correlated work. Green tests here are
not evidence of correctness; they are evidence that the code matches a model nobody checked.

Two things beat correlated errors, and this skill is built entirely from them:

1. **Independence** — introduce a viewpoint that does *not* share the blind spot: a different
   artifact type (a failure map instead of code), a different question (about failure and
   dependency, which tests never ask), or a different reviewer (a fresh, adversarial pass).
2. **Move the review upstream, to a cheaper layer** — architecture errors are nearly invisible
   in 800 lines of correct code, but obvious on a one-page failure map. Review the cheap
   artifact, not the expensive code.

So: before you write code for a structural change, you produce a few small, independent
artifacts and check *those*. That is the whole idea.

## What counts as structural

A change is structural — and gets the full review — when it touches **any** of these:

- a **cross-component dependency** (who calls / depends on whom);
- a **boundary between subsystems or modes**;
- a **failure policy** — what happens on failure: retry, fail-closed, roll back, degrade, warn;
- a **contract** that more than one party must agree on;
- a **recovery, repair, or diagnostic path** — anything whose job is to save the system when
  something else is broken.

Once a change is in scope, run every step through to the record — there is no opt-out partway.
When unsure whether a change is structural, treat it as structural.

## The process

Produce these **before** the code plan, in order. Keep each short — a few lines each; the aim is
to think on paper and expose structure. The nine steps group into four themes:

- **A · Frame the real problem** — step 0 (elicit) · step 1 (reframe): find what is *actually*
  being asked and what hidden risk it carries.
- **B · Map the failure surface** — step 2 (failure map) · step 3 (tabletop): find where and how
  it breaks.
- **C · Structure the solution** — step 4 (separate by failure response) · step 5 (fitness tests):
  organize by failure policy, then lock the good shape.
- **D · Verify & record** — step 6 (independent review) · step 7 (code plan) · step 8 (record):
  check from an independent angle, then persist the decision for traceability.

### 0. Elicit hidden risks (and load the domain record)

The user's request is never complete — hidden risk lives in the gap between what was *said* and
what must be *true*. Recover that gap before designing; guessing the domain silently is what goes
wrong.

Read the spec under review (`docs/reviewspec/<build>/spec.md`) and the subsystem's decision memory
`docs/decisions/<system>.md` **first**. Honor each recorded
entry by its provenance tag: a `user-confirmed` decision that a new decision would contradict is a
conflict to *surface*, not silently override; `artifact-verified` and `assumed` entries may be
stale — re-check them against current code. An `assumed` entry is an open question, never an
established fact — reading it as settled turns this record from a drift *detector* into a drift
*spreader*.

Then surface what the request left implicit by walking three gaps. The request supplies the nouns
and verbs; the universal axes supply the coverage — so you generate risks no static checklist
(bounded by its author's memory) would contain:

- **Intent gap** — the request states a solution; recover the *goal* and the observable done-check
  ("why this? what does done look like, measurably?"). Step 1's reframe questions come from here.
- **Boundary gap** — the request states the central case; generate edges by pushing each noun/verb
  through universal dimensions — count (0 / 1 / many / max), time (never / now / late / concurrent
  / out-of-order), validity (valid / malformed / malicious / stale / duplicate), presence (present
  / absent / partial / revoked).
- **Invariant gap** — the request states what *should* happen; name what must **never** happen,
  regardless of path, and what would violate it.

Tag every fact you now rely on: **user-confirmed / artifact-verified / assumed**. Verify `assumed`
facts from the repo where you can; the ones that are **load-bearing AND unverifiable** are your
questions for the user — ask those, not the whole generated list. **Anyone's word is a claim, not
proof — including the user's and including your own reading of the request.** A claim about how the
system behaves is verified only when *you* find the evidence in the repo (`artifact-verified` with
an anchor); if you can't find it, ask — never record it as fact. `user-confirmed` is only for
decisions the user owns, quoted to their actual words. Full provenance rules and record format in
`references/domain-record.md`.

**Done when:** each gap has been walked against the request's own nouns/verbs; every relied-on
fact is provenance-tagged; and the load-bearing-unverifiable set has been asked or queued.

### 1. Reframe the problem (catch the mis-framing first)

Before anything else, challenge the framing itself. The most expensive errors come from
solving a slightly-simpler-but-wrong version of the problem. Answer honestly:

- What is this system **actually protecting or guaranteeing**? (Not "what does the ticket say"
  — what breaks in the real world if it fails?)
- **Is the problem being mis-framed as something simpler than it is?** What did the framing
  quietly assume away?
- When it fails, **who learns of it, how, and how soon?** The further the audience is from the
  failure, the more the system's real job includes *diagnosis and self-preservation*, not just
  the happy path.
- If all unit tests passed, **what outage could this design still cause?**

If reframing changes the problem, stop and re-scope before designing. The rest is wasted on the
wrong problem.

**Done when:** each of the four questions has a one-line answer, and you've stated explicitly
whether the framing changed. Full framing question set in `references/question-bank.md` §1.

### 2. Draw the failure map

A dependency picture plus a failure column. For each component: **what depends on it, and what
user-facing path breaks when it is down?**

```
Caller
  -> Component A ──┐
  -> Component B   ├─ shared store
  -> Component C ──┘
```

Then walk it and answer:

- Which failures should **block** the main path, and which should only be **reported**?
- Which operations need **rollback**?
- If a component is **half-broken / half-updated**, what user path is wrongly blocked?
- If the primary path is down, **what entry point is left to diagnose or repair it** — and does
  that entry point depend on the thing that is broken? (Apply this recursively: a repair path
  that lives inside the process it repairs dies with it.)

You review *this map*, not the code. Fused paths and circular repair-dependencies are visible
here and nowhere else.

**Done when:** every component in the sketch has, written beside it, its block-vs-report call,
its rollback need, its half-broken behavior, and its surviving repair entry point — none blank.

### 3. Run an incident tabletop (no code)

Walk **5 real failure scenarios** through the design on paper. For each, state:

1. what the system **observes**,
2. what it **returns / does**,
3. what the **operator's next step** is (can they even tell what went wrong?),
4. whether a **working prior state is preserved**.

Pick each scenario from a distinct edge of the actual failure map — not a generic placeholder. If
a scenario ends in the operator unable to tell what went wrong or act on it, or a working prior
state lost, that is a finding, found before a line of code.

**Done when:** 5 scenarios, each drawn from a distinct edge of the failure map (not generic
placeholders), have all four fields filled, and every "operator can't act / prior state lost"
ending is recorded as a finding.

### 4. Separate concerns by failure response

The core structural move, and it is general. **Group things by what you must DO when they fail,
not by what they are about** — two checks share a path only if they share a *failure-policy
vector* (transient/terminal, retry/refuse, provable-now/observable-later, accident/adversary).
Split by topic and you get an unbounded list; split by failure response and a small number of
families fall out on their own — the count is not chosen, it is however many distinct vectors
your checks need. Validate any non-obvious split with the **merge reductio** (see
`references/question-bank.md` §4). The stakes: fuse different failure policies into one path or
one error code and no single policy can be right for the whole bag — some input is guaranteed a
wrong response.

**Done when:** every check/operation is assigned to exactly one family, and each non-obvious
split has its merge-reductio recorded.

### 5. Propose architecture fitness tests

Ordinary tests check behavior. **Fitness tests check that the architecture cannot regress to a
shape you already know is bad** — assertions about *shape*, run in CI forever. Pattern list in
`references/question-bank.md` §5. They are the only durable, automatable defense here, and they
matter because *this class of error is usually introduced by a later, well-meaning "fix"* that
re-fuses what you separated — a fitness test makes that commit fail CI.

**Their boundary, stated so nobody over-trusts them:** a fitness test locks only a bad shape you
have *already* identified; it cannot catch the first novel mis-framing. Steps 1–3 catch the new
error; fitness tests keep it dead. "We have fitness tests" ≠ "the architecture is sound."

**Done when:** each finding from steps 2–4 that can be phrased as a shape assertion has one named.

### 6. Get an independent adversarial review of the framing

Correlated errors need an *independent* viewpoint (see the top of this file). Before coding,
obtain one pass that challenges the **problem framing and structure**, not the implementation —
the paste-ready reviewer prompt is in `references/question-bank.md` §6.

- If subagents are available, spawn one pointed at framing, not correctness.
- If not, do the pass yourself in a deliberately adversarial frame (weaker — the blind spot may
  be shared, so say so), or hand the user that prompt for a second model.

Convergence between two independent passes is strong evidence; **divergence points straight at
the load-bearing, risky decision.**

### 7. Write the code plan

With the framing checked, the failure map drawn, the tabletop survived, the concerns separated,
and the fitness tests named — write the implementation plan. It will be short, because the hard
decisions are already made.

### 8. Record the decisions — before you implement

Write or update `docs/reviewspec/<build>/design-review.md` **before writing implementation code**, so the
architectural decision is durable and traceable even if the code is later abandoned or rewritten.
The record precedes the code, not the other way round. It has two mandatory parts:

- **Current state** (a living snapshot, updated in place so no reader follows a retired design):
  **purpose** (intent gap) · **boundary conditions** (boundary gap) · **invariants / cautions**
  (invariant gap) · **scenarios** (tabletop) · every load-bearing **fact with its provenance tag**
  · links · open questions. Link out to any authoritative domain doc (README, domain model,
  OpenSpec) rather than restating it, so you never create a second source of truth.
- **Decision log** (append-only, newest first, never edited away): one dated entry per review round
  that touched architecture. A decision is **never silently overwritten** — when a round changes
  one, update the current-state section *and* append a log entry naming the old decision, the new
  one, and **why it changed**. A conflict resolved this round (step 0 / step 6) is logged here as
  old → new + why + the provenance that settled it. This log is the architecture-change trail: a
  reader months later must be able to trace *why* the design became what it is from the record
  alone, without this conversation.

Format, log-entry shape, and conflict rules in `references/domain-record.md`.

**Done when:** the current-state sections reflect this round; an **append-only dated log entry**
records what this round changed, what it superseded and why (or "first review"); no prior decision
was silently overwritten; every non-`user-confirmed` fact has a verify-against anchor; and any
conflict is surfaced, classified (fact / assumption / decision), and logged with its resolution —
or, for a decision conflict, left for the user.

## Output format

Produce a compact review before code — think on paper, a few lines per section. **This template
is the review's completion criterion: fill every section, or mark it N/A with one reason, before
writing code.**

```
## Design review: <change>

**Triage:** structural (crosses <which boundary>) — running full review.
   [or] local single-component change — skipping, implementing directly.

**Elicit:** prior record loaded (conflicts?) · intent/boundary/invariant gaps walked ·
   load-bearing-unverifiable questions for the user · facts tagged (confirmed/verified/assumed)

**Reframe:** what it really protects · the mis-framing risk · who learns on failure & how soon ·
   an outage green tests would miss

**Failure map:** <dependency sketch> + per-component: blocks vs. reports, needs-rollback,
   half-broken behavior, surviving repair entry point

**Tabletop (5):** scenario → observes / returns / operator's next step / prior state preserved

**Failure-policy families:** the groups that fell out, each with its policy; merge-reductio
   for any non-obvious split

**Fitness tests:** the shape assertions to add (+ their known-shape-only limitation)

**Independent review:** convergences (safe) and divergences (look here)

**Code plan:** <the now-short list of steps>

**Record (before code):** wrote/updated docs/reviewspec/<build>/design-review.md — current state
   (purpose · boundaries · invariants · scenarios · provenance-tagged facts) + an append-only
   dated decision-log entry (what changed this round + why it superseded the last)
```

## Red flags that you are skipping the framing

Any of these means stop and run the review:

- "It's just wiring / just a small change" — but it crosses a subsystem boundary.
- You are about to add "more validation" to make something "more robust" — hardening that adds
  checks without asking *how the failure is reported* is a common way this class of error enters.
- You cannot say, in one sentence, what happens when this fails and who sees it.
- The plan has no rollback and no "what if it's half-done" answer.
- You are relying on "the tests pass" as your evidence that the design is right.

## Further material

- `references/domain-record.md` — the step-0 engine: the three-gap generator, the boundary
  dimension table, provenance tiers + the anti-laundering rule, the ask/verify filter, the domain
  record format, and conflict handling across runs. Read it whenever you run step 0 or step 8.
- `references/question-bank.md` — seed question lists, tabletop templates, fitness-test patterns,
  and the ready-to-paste adversarial-reviewer prompt. Read it for the complete checklists — but
  the step-0 engine, tailored to the request, takes precedence over these fixed lists.
