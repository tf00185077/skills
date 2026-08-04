# Question Bank & Templates

Full checklists and ready-to-paste prompts for `design-review-first`. Use these when you want
the complete lists rather than the summaries in SKILL.md. Nothing here is domain-specific — it
applies to any structural change.

## Table of contents

1. Framing questions (step 1)
2. Failure-map prompts (step 2)
3. Incident tabletop template (step 3)
4. Failure-policy separation: the decision procedure (step 4)
5. Fitness-test patterns (step 5)
6. Adversarial-reviewer prompt — paste-ready (step 6)
7. A user-facing "before you code" prompt

---

## 1. Framing questions (step 1)

Ask these before designing. They exist to catch a problem framed as something simpler than it is.

1. What does this system **truly protect or guarantee**? What breaks in the real world if it fails?
2. What is the **worst realistic failure scenario**?
3. Is the **operator present** when it fails, or is it unattended / remote? If unattended, the
   real job usually includes *diagnosis and self-preservation*, not only the happy path.
4. If this piece breaks, **what diagnostic / repair entry point remains**?
5. Which failures should be **fail-closed** (refuse, don't proceed)?
6. Which failures are actually **transient** and should retry / warm up / degrade rather than
   hard-fail?
7. Which errors **must carry diagnostic data** to be actionable?
8. Will this design let a **working older/current system get blocked** by the new flow?
9. **If all tests passed, where could this still be wrong?**
10. Are **two different responsibilities being fused into one path** (e.g. normal use + repair +
    deploy)?
11. What is the cost of a **false reject** here, not just a false accept? (In unattended systems
    the two costs are often equal — both end in "no working system + nobody to fix it.")

---

## 2. Failure-map prompts (step 2)

Draw dependencies, then interrogate each edge:

- For each component: what depends on it? What user-facing path breaks when it's down?
- Which errors should **block** the main path vs. only be **reported**?
- Which operations need **rollback**?
- What happens when a component is **half-broken or half-updated**?
- If the primary path is down, what entry point can still reach in to fix it — **and does that
  entry point depend on the broken thing?** (Recursive check: a repair path hosted inside the
  process it repairs dies with it. Truly robust repair is out-of-band.)

---

## 3. Incident tabletop template (step 3)

Pick 5 real scenarios from the failure map. For each, fill in — on paper, no code:

| Scenario | System observes | System returns/does | Operator's next step | Working prior state preserved? |
|---|---|---|---|---|
| e.g. slow cold start | ... | ... | can they tell what's wrong? | ... |
| "up but not ready yet" | | | | |
| partial update / stale state | | | | |
| leftover lock or resource | | | | |
| nobody on-site, API-only diagnosis | | | | |

A row that ends in "operator sees an opaque code and can't act" or "the good prior version is
gone" is a finding. Fix the design before coding.

---

## 4. Failure-policy separation: the decision procedure (step 4)

The reusable rule: **separate concerns by their failure response, not by their subject matter.**

Procedure:

1. For each check / operation / path, record its **failure-policy vector** — the answers to:
   - Is the failure possibly **transient** (retry/wait helps) or **terminal**?
   - On failure, **refuse-and-never-proceed**, or **resume/continue forward**?
   - Is it **provable before you commit**, or only observable **during/after** real work?
   - Are you guarding against an **accident/crash** or an **adversary**? (These need *opposite*
     recovery: accident-guards may self-heal / resume; adversary-guards must never self-heal.)
2. **Group items with identical vectors.** The number of groups is not chosen — it is however
   many distinct vectors exist.
3. For any non-obvious split, apply the **merge reductio**: "if I merge A and B into one path or
   one error code, is there a real scenario that forces a demonstrably wrong action?"
   - Yes → they must stay separate (even if topically similar).
   - No → don't split; identical vectors don't earn a separate path.

Why it matters: fuse concerns with different failure policies into one path/error, and no single
policy can be right for the whole bag — some input is guaranteed a wrong response. Separation is
also what lets you later tune one dial (e.g. loosen a functional check) without removing a
security or transaction guarantee.

---

## 5. Fitness-test patterns (step 5)

Assertions about *shape*, checkable in CI, that stop regression to a known-bad structure. Adapt
the nouns to your system:

- "`<normal path>` must not import / call `<deploy or admin coordinator>`."
- "`<health/validation>` must return a structured result, not a bare boolean."
- "distinct failure families must not share one error code."
- "a terminal failure must include stage + expected + observed + a diagnostics handle."
- "captured stderr/stdout must be redacted, never discarded."
- "`<repair/diagnostic path>` must not depend on `<the thing it repairs>` being healthy."
- "`<state from subsystem X>` must not be able to block `<subsystem Y's>` normal operation."

**Boundary to state alongside them:** fitness tests lock only *already-known* bad shapes. They
prevent regression; they do not catch the first novel mis-framing. Steps 1–3 catch the new one;
fitness tests keep it dead. "We have fitness tests" ≠ "the architecture is sound."

---

## 6. Adversarial-reviewer prompt — paste-ready (step 6)

Give this to an independent subagent or a second model. It points at *framing*, not code:

```
You are reviewing ARCHITECTURE and PROBLEM FRAMING, not implementation.
Assume every unit test passes and the code is correct as written.

Challenge only these:
1. Is the problem mis-framed as something simpler than it really is?
2. What concerns are fused into one path/gate/error that should be separable
   (different failure responses)?
3. For each failure path: what does it do, and is that the right response?
4. Is any contract / rule defined in more than one place (drift risk)?
5. Does any repair, recovery, or diagnostic path depend on the very thing it
   is meant to fix?
6. Given all tests pass, what real-world outage could this design still cause?

Do not suggest code cleanups. Only surface structural/framing risks.
```

Interpretation: where an independent pass **agrees** with your design, that's strong evidence
it's sound. Where it **diverges**, that divergence marks the load-bearing, risky decision — look
there first.

---

## 7. A user-facing "before you code" prompt

For a human directing an agent, to paste at the start of any structural change:

```
Before writing code, do an architecture risk review. Don't jump to an implementation.
First answer:

1. What's the correct framing of this problem? Is it being mis-framed as something simpler?
2. If this runs unattended / fails remotely, how does the operator learn the cause?
3. What are the checks/paths here, grouped by how they must fail (terminal / retry / warming /
   report-only / roll back)?
4. If all unit tests pass, what outage could this design still cause?
5. Which error info is preserved, which is redacted, which must never be discarded?
6. Walk 5 incident scenarios through the design, end to end, no code.
7. List the architecture fitness tests that would stop this from regressing later.
8. Only then, give the code plan.
```

---

## Origin note

This skill was distilled from a post-mortem of a system where a managed auto-updater was fused
with the normal-traffic path and a repair path, used one opaque error code for every failure,
and collapsed a multi-valued health state into a single boolean — all while passing its full
test suite. The specific taxonomy from that case (integrity / transaction / health gates;
normal / maintenance / release planes) is a good *illustration* of step 4, but it is not
universal law. The universal part is the **process** in SKILL.md: reframe, map failures,
tabletop, separate by failure response, lock with fitness tests, review independently — before
code.
