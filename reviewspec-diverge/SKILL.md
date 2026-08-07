---
name: reviewspec-diverge
disable-model-invocation: true
description: Phase 1 of the reviewspec chain — diverge. Explore a problem space before any spec, producing a problem statement plus candidate directions. Invoke by name, or via reviewspec-dispatch.
---

# reviewspec · Diverge (phase 1)

Understand the problem before shaping a solution. This phase is for **thinking, not deciding** —
open threads, investigate, let the shape emerge. Writing the spec (phase 2) or code (phase 4) here
is a mistake.

## Do

- Read the subsystem's decision memory first — `docs/decisions/<system>.md` — so you don't
  contradict a prior decision without noticing.
- **Ground it in reality**: investigate the actual codebase / context around the request; don't
  theorize in the abstract.
- **Open multiple directions, not one funnel**: what could this really be? where are the
  integration points? where is the hidden complexity? what analogies apply?
- **Challenge the framing**: is the stated request a *solution* to a deeper goal? Name the goal.

## Do NOT

- Write the spec — that is phase 2 (`reviewspec-converge`).
- Write implementation code — that is phase 4 (`reviewspec-build`).
- Force a conclusion — sometimes the value is just clarity.

## Hand off, then stop

Write `docs/reviewspec/<build>/explore.md`:

```markdown
# Explore · <build>
## Real goal (not just the stated solution)
## Candidate directions (2-4, each with a one-line trade-off)
## Integration points / hidden complexity noticed
## Open questions to resolve in phase 2
```

**Gate to advance (→ phase 2):** the problem is crisp enough to shape a spec. If it isn't, stay
here. **If the request is actually several independent problems, say so** — it should be
decomposed and each piece run through the chain separately.

Stop after writing the artifact. Whoever invoked you (you, or `reviewspec-dispatch`) decides
whether to proceed — this phase never jumps ahead on its own.
