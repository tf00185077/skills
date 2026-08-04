---
name: design-review-first
description: >-
  Failure-first design review, run before code. Use when designing a new system or making a
  structural change — one crossing a subsystem boundary, setting a failure policy, defining a
  cross-party contract, or adding a recovery / repair / diagnostic path — even when the ask
  sounds small ("add X", "wire up Y", "fix the updater"). Not for local single-component changes.
---

# Design Review First

## What this defends against

The dangerous failures in real systems are usually not "the code is wrong." They are **"the
code correctly implements the wrong abstraction."** Every line is correct; the whole thing
solves a subtly wrong problem. Examples: a release check that also blocks normal traffic; a
repair path that depends on the very thing it repairs; a health check that collapses six
different failures into one useless error code; a validator that treats "still warming up" as
"broken."

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

## When to run this (triage — do not over-apply)

Running the full process on every change creates friction, and friction gets the process
abandoned. Spend it only where architecture is actually at stake. Run the full review when the
change touches **any** of these:

- a **cross-component dependency** (who calls / depends on whom);
- a **boundary between subsystems or modes** (e.g. a normal path vs. an admin/repair path vs. a
  deploy path);
- a **failure policy** — what happens on failure: retry, fail-closed, roll back, degrade, warn;
- a **contract** that more than one party must agree on (a schema, a status shape, a protocol);
- a **recovery, repair, or diagnostic path** — anything whose job is to save the system when
  something else is broken.

For a genuinely local, single-component change (a leaf function, a bug fix contained in one
module, a rename), skip this and implement directly. Say so in one line ("local change, no
subsystem boundary crossed — implementing directly") so the skip is a decision, not an
oversight.

If you are unsure whether a change is structural, it is — run the review.

## The process

Produce these **before** the code plan, in order. Keep each short — a few lines each; the aim is
to think on paper and expose structure.

### 1. Reframe the problem (catch the mis-framing first)

Before anything else, challenge the framing itself. The most expensive errors come from
solving a slightly-simpler-but-wrong version of the problem. Answer honestly:

- What is this system **actually protecting or guaranteeing**? (Not "what does the ticket say"
  — what breaks in the real world if it fails?)
- **Is the problem being mis-framed as something simpler than it is?** What did the framing
  quietly assume away?
- Who is **present** when it fails — a developer at a keyboard, or nobody (unattended, remote)?
  An unattended system's real job is often *diagnosis and self-preservation*, not just the
  happy-path function. Framing it as "just do the task" loses that.
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

Pick scenarios from the actual failure map: cold start / slow warmup, "up but not ready yet",
partial update leaving stale state, a lock/resource left behind, and *"nobody is at the machine,
only an API to diagnose through."* If a scenario ends in "the operator sees an opaque code and
can't act," or "the good old version is now gone," that is a finding, found before a line of code.

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
shape you already know is bad** — assertions about *shape*, run in CI forever (e.g. "the
normal-traffic path must not call the deploy coordinator"; "a terminal failure must carry
stage + expected + observed + a diagnostics handle"). Full pattern list in
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

### 7. Only now, write the code plan

With the framing checked, the failure map drawn, the tabletop survived, the concerns separated,
and the fitness tests named — write the implementation plan. It will be short, because the hard
decisions are already made and recorded.

## Output format

Produce a compact review before code — think on paper, a few lines per section. **This template
is the review's completion criterion: fill every section, or mark it N/A with one reason, before
writing code.**

```
## Design review: <change>

**Triage:** structural (crosses <which boundary>) — running full review.
   [or] local single-component change — skipping, implementing directly.

**Reframe:** what it really protects · the mis-framing risk · who's present on failure ·
   an outage green tests would miss

**Failure map:** <dependency sketch> + per-component: blocks vs. reports, needs-rollback,
   half-broken behavior, surviving repair entry point

**Tabletop (5):** scenario → observes / returns / operator's next step / prior state preserved

**Failure-policy families:** the groups that fell out, each with its policy; merge-reductio
   for any non-obvious split

**Fitness tests:** the shape assertions to add (+ their known-shape-only limitation)

**Independent review:** convergences (safe) and divergences (look here)

**Code plan:** <the now-short list of steps>
```

## Red flags that you are skipping the framing

Any of these means stop and run the review:

- "It's just wiring / just a small change" — but it crosses a subsystem boundary.
- You are about to add "more validation" to make something "more robust" — hardening that adds
  checks without asking *how the failure is reported* is exactly how the boolean-collapse and
  path-fusion errors get introduced.
- You cannot say, in one sentence, what happens when this fails and who sees it.
- The plan has no rollback and no "what if it's half-done" answer.
- You are relying on "the tests pass" as your evidence that the design is right.

## Further material

- `references/question-bank.md` — the full framing question bank, tabletop scenario templates,
  fitness-test patterns, and the ready-to-paste adversarial-reviewer prompt. Read it when you
  want the complete checklists rather than the summarized ones above.
