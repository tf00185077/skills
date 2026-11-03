# Format examples

Use these shapes for the ROADMAP derivation, CURRENT, a task Purpose paragraph and an owner question. Both projects and all links are fictional. They show that the same derivation can produce very different milestone orders.

## Example A — a new puzzle game

### Derivation (working notes, not a ROADMAP section)

- **Destination:** a player new to the game finishes it in one evening and wants to replay it to beat their move count. **Constraints:** solo developer; desktop only.
- **Unknowns, ranked by the cost of being wrong:**
  1. Value: is the swap-and-glow rule satisfying? If not, every level and asset is wasted.
  2. Usability: does a full session hold attention?
  3. Delivery: can strangers install and run it?
- **Cheapest evidence:** (1) the owner plays a 10-level build; (2) two outside testers play a 30-level build; (3) a public demo download.

### `docs/roadmap/ROADMAP.md`

```markdown
# Roadmap

## Destination
A player new to the game finishes it in one evening and wants to replay it to beat their move count.
Constraints: solo developer; desktop only.

## Milestones

### M1 — Is the core puzzle satisfying? (done)
Evidence path: the owner plays a 10-level build.
Exit: the owner says the rule is fun or names what to change. Confirmed 2026-03-02.

### M2 — Does a full session hold attention? (active)
Evidence path: 30 levels and an end screen → two outside testers play start to finish.
Exit: both finish in under 90 minutes without a blocker; the owner confirms the pacing.
Remaining: levels 21–30 and the end screen.

### M3 — Can strangers install and enjoy it? (next)
Exit: a public demo is installed and finished by people we did not recruit; the owner approves.

### Later
Store release on one platform.

## Not now
- Level editor, leaderboards and final art — revisit at M3.
- Platform signing — revisit when M3 picks a store.

## Task selection
A task counts only if it is a step on the active milestone's evidence path.
Priority: 1) direct owner request; 2) a blocker on the evidence path; 3) the next evidence-path step.
Thresholds: ask after 3 consecutive non-advancing tasks, or when a blocker lasts more than 2 days.

## Review history
- 2026-02-20 — first roadmap approved by the owner ([decision](../decisions/roadmap-v1.md)).
- 2026-03-02 — M1 done; M2 activated by the owner ([decision](../decisions/m1-review.md)).
```

## Example B — a client system upgrade (milestones only)

Destination: the client's billing runs on the new payment component by 30 June with no change to existing invoices. Constraint: the ledger database schema must not change. The top unknown is compatibility, not value, so the derivation starts there.

```markdown
### M1 — Can the new component post a refund through the existing ledger? (active)
Evidence path: a spike on the hardest flow, refunds, against a copy of production data.
Exit: refunds reconcile to the cent on 1,000 replayed cases; the client's lead engineer signs off.

### M2 — Do all existing invoice types still produce identical output? (next)
Exit: a side-by-side comparison of a month of invoices shows no difference; the client accepts the comparison report.

### Later
Cut-over and rollback rehearsal.
```

## `docs/CURRENT.md`

```markdown
# Current state — 2026-03-09

**Try it:** [build 0.4](builds/0.4.md), levels 1–20, keyboard only.

**Active milestone:** M2 — does a full session hold attention? Remaining on the evidence path: levels 21–30, the end screen, then the tester session.

**Active tasks**
- Levels 21–25 design (evidence path: levels 21–30).

**Blockers:** none.

**Next candidates**
1. Levels 26–30.
2. End screen with a move-count summary.

**Pending owner decisions:** none.

**Counters:** non-advancing tasks in a row: 0 of 3 · longest blocker: none.
```

## Task Purpose paragraph

```markdown
## Purpose

M2 asks whether a full session holds attention. This task adds levels 21–25 so the tester session can reach the late game. Readable difficulty progression matters more than visual polish. Art changes and new mechanics are out of scope.
```

## Owner question

```markdown
Testers can now play all 30 levels, but the new art set will not be finished for about three weeks. We can run M2's tester session now with the current art, or wait for the new art.

A. Run the tester session this week with the current art. Pacing evidence arrives in about 5 days; we may retest after the art changes. Recommended.
B. Wait for the new art, then run the session. Pacing evidence arrives in about 4 weeks; one session covers both.
C. Something else.

While waiting: level bug fixes already in progress continue. No art-integration task starts.
```
