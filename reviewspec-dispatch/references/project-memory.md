# Project Memory — per-system decision records

A durable, agent-to-agent memory of a project's **key decisions and why they were made**,
split by subsystem, one file per subsystem, each the **single source of truth** for that
subsystem. Any agent reads it before touching a subsystem (so it doesn't contradict prior
decisions) and appends to it when a key decision is made.

Usable standalone — not only from `reviewspec-dispatch`.

## Where it lives

`docs/decisions/<system>.md` — one file per subsystem (e.g. `worker.md`, `comfyui.md`,
`lora-training.md`, `prompt-library.md`, `discord-bot.md`). The split follows the project's
actual subsystems; a decision that spans two subsystems is recorded in the one it most
constrains, and linked from the other.

## What goes in (the filter)

Only **key, cross-cutting, load-bearing** decisions — the ones that will *constrain or surprise
a future agent*. Not every choice; a memory that records everything becomes noise nobody reads.
A decision earns an entry when it: sets a subsystem-wide rule or invariant, chooses between real
alternatives with a non-obvious rationale, or supersedes an earlier decision.

**Link, don't restate.** Detail that lives in an area record (`docs/reviewspec/<build>/design-review.md`),
a design doc, or code stays there — the memo holds the decision + why + a link. Copying detail in
creates a second source of truth that drifts (the exact failure this whole system exists to
prevent).

## File structure

```markdown
# Decisions · <system>

_Read/write: read this before changing <system>; to contradict a prior decision, append a
superseding entry (never edit the old one)._
_Compacted <date>: <N> → <M> entries; full history is in git._

## Settled (densified — one line per decision lineage)
- <current decision> · why: <net reason> · supersedes: <what> · <provenance> · <link>

## Active log (append-only, newest first — recent decisions not yet densified)
### <date> · <task> · <one-line decision>
- **Decision:** <what was decided>
- **Why:** <rationale>
- **Supersedes:** <prior decision + why it changed>   (or "—")
- **Provenance:** user-confirmed@"<quote>" | artifact-verified @<file:symbol> | assumed
- **Link:** <area record / design doc / code>

## Open questions (load-bearing, unresolved — must survive every compaction)
- <question> [why load-bearing]
```

## Write discipline

- **Append-only within a compaction cycle** — never edit or delete a past entry; supersede by
  appending a new one that names the old decision and why it changed.
- **Provenance on every entry** — same rules as the design record: `user-confirmed` needs a quote
  of the user's actual words; a claim about how the system behaves is `artifact-verified` (you
  found the evidence) or `assumed`, never `user-confirmed` on anyone's say-so.
- **Load-bearing filter** — if it wouldn't constrain or surprise a future agent, it doesn't go in.

## Read discipline

- Before working on a subsystem, **read its file first**. Honor each entry by its provenance:
  an `assumed` entry is an open question, not settled fact; a new decision that contradicts a
  `user-confirmed` one is a conflict to surface, then resolve by appending a superseding entry.
- If the memory and the code disagree, **the code wins** — flag the stale entry (append a
  correction; don't silently trust the memo).

## Compaction — densify, never lose the truth

The single-file rule means the file cannot spill into archives, so compaction is the only way to
bound size. Compaction is **densification, not amnesia**, and it is safe because the file is
git-tracked: **git holds every pre-compaction version, so nothing is truly lost** — the working
file is the current dense truth; git is the full append-only archive.

**Trigger:** when the file exceeds ~400 lines, or the Active log holds more than ~15 entries
(guidelines, not magic numbers — the aim is "readable in one pass"). 

**Action — collapse lineages, keep the net:**
1. For each *resolved* decision lineage in the Active log (A → B → … → current), collapse the
   whole chain into **one line in Settled**: current decision · net why · what it superseded ·
   provenance · link.
2. Merge duplicate or overlapping entries.
3. Move densified lineages out of the Active log; keep the last few full entries there for recency.
4. Add/update the header line: `Compacted <date>: <N> → <M> entries; full history is in git.`

**Preserve unconditionally — never dropped by compaction:**
- every **current** decision and its net why;
- every **open question**;
- every **provenance** tag and anchor;
- the **supersession net** (that current superseded X, and why) — even when the verbose steps go.

**Never during compaction:** launder an `assumed` into a fact, drop an open question, change a
provenance tag, or relitigate a settled decision. When unsure whether to fold an entry, keep it —
a slightly long file beats a lost truth.

## Why this shape

- **Per-system single file** → each subsystem's truth is in one place; no hunting, no drift.
- **Settled (dense) + Active (full) + Open** → recent decisions keep their detail; old churn is
  densified; unresolved risk is always visible.
- **Git as archive** → single-file working truth without ever destroying history.
- **Same provenance + anti-laundering rules as the design record** → the memory can't quietly
  turn a guess into a fact, at project scope.
