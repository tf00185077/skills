# Format example

Use this shape for ROADMAP, CURRENT, a task Purpose paragraph and an owner question. The project, its content and its links are fictional.

## `docs/roadmap/ROADMAP.md`

```markdown
# Roadmap

## Destination

A short, cosy puzzle game that a new player finishes in one evening and wants to replay to beat their move count.

## Milestones

### M1 — Is the core puzzle satisfying? (done)
Exit: the owner plays 10 levels and says the swap-and-glow rule is fun, or names what to change. Owner confirmed 2026-03-02.

### M2 — Does a full session hold attention? (active)
Exit: a 30-level build plays start to finish without a blocker; two outside testers finish it in under 90 minutes; the owner confirms the pacing.
Remaining: levels 21–30 and the end screen.

### M3 — Is it ready to show strangers? (next)
Exit: art and sound at shareable quality; owner approves a public demo.

### Later
Store release on one platform.

## Not now
Level editor, online leaderboards and platform signing — revisit after M3.

## Task-selection rule
1. A direct owner request.
2. Anything blocking the active milestone's exit.
3. Work toward the active milestone's question.
4. Tooling, verification or platform work, only when it unblocks 1–3.

## Escalation thresholds
- Ask after 3 consecutive tasks that do not advance the active milestone's question.
- Ask when any blocker lasts more than 2 days.

## Review history
- 2026-02-20 — first roadmap approved by the owner ([decision](../decisions/roadmap-v1.md)).
- 2026-03-02 — M1 done; M2 activated by the owner ([decision](../decisions/m1-review.md)).
```

## `docs/CURRENT.md`

```markdown
# Current state — 2026-03-09

**Try it:** [build 0.4](builds/0.4.md) — levels 1–20, keyboard only.

**Active milestone:** M2 — does a full session hold attention? Levels 21–30 and the end screen remain.

**Active tasks**
- Levels 21–25 design (serves M2: session length).

**Blockers**
- None.

**Next candidates**
1. Levels 26–30 (rule 3).
2. End screen with move-count summary (rule 3).

**Pending owner decisions**
- None.

**Counters:** non-advancing tasks in a row: 0 of 3 · longest blocker: none.
```

## Task Purpose paragraph

```markdown
## Purpose

M2 asks whether a full session holds attention. This task adds levels 21–25, so a tester can reach the late game. Readable difficulty progression matters more than visual polish. Art changes and new mechanics are out of scope.
```

## Owner question

```markdown
M2's exit criteria look met: 30 levels play through, and two testers finished in 70 and 85 minutes ([evidence](qa/m2-session-test.md)). Before starting M3, please confirm M2 and choose the next focus.

A. Confirm M2 and start M3 (art and sound for a public demo). Recommended.
B. Stay in M2 to rebalance levels 24–27, which both testers found slow.
C. Something else.

While waiting: only the M2 bug fixes already in progress continue; no M3 work starts.
```
