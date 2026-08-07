# Elicitation Engine & Domain Record

The step-0 machinery: how to generate the hidden risks of any request, how to tag what you know,
and how to persist it so later reviews catch contradictions. This is a *generator*, not a
checklist — coverage comes from the request's own nouns/verbs crossed with universal axes, so it
produces risks no remembered list would contain.

## Table of contents

1. The three-gap generator
2. The boundary dimension table
3. Provenance tiers (and the anti-laundering rule)
4. The filter — what to actually ask
5. The domain record: format
6. Conflict handling on later runs

---

## 1. The three-gap generator

Hidden risk lives between what the request *said* and what must be *true*. Walk three gaps; each
is universal (applies to any request) and generative (the request fills in the content).

- **Intent gap — solution stated, goal unstated.** Requests arrive as solutions ("add a queue",
  "add a cache"). Recover the goal and the observable done-check: *"What breaks if we don't do
  this? What does 'done' look like, measured how?"* Catches XY-problems and mis-scoping.
- **Boundary gap — central case stated, edges unstated.** Take each **noun** (input, entity,
  resource, actor) and each **verb** (action) the request names, and push it through the universal
  dimensions in §2. Each cell is a candidate risk: *"When `<noun>` is `<extreme>`, or `<verb>`
  meets `<extreme>`, what happens?"* This is where coverage comes from — the nouns are the
  request's, the dimensions are universal, so you generate failures the request's author never
  mentioned.
- **Invariant gap — desired behavior stated, forbidden outcomes unstated.** Name what must
  **never** happen regardless of path — data loss, double-effect (double-charge, double-send),
  PII / secret exposure, corruption, cost/rate blowup — and what would violate each. Users omit
  these because they feel "obvious"; that is exactly why they are the silent failures.

Run all three. They are near-MECE: intent = why, boundary = the edges of what, invariant = the
shadow of what.

---

## 2. The boundary dimension table

Cross every noun/verb in the request with these. Not every cell is real — but generating them all
first is how you avoid missing the one that matters.

| Dimension | Extremes to test |
|---|---|
| **Count** | zero · one · many · huge / max · over-limit |
| **Time** | never · now · late / delayed · concurrent · out-of-order · forever / never-completes |
| **Validity** | valid · malformed · malicious · stale / expired · duplicate |
| **Presence** | present · absent · partial / half-done · revoked / withdrawn |
| **Ordering** | first · retried · replayed · interleaved with another actor |

Generate the full grid first (each noun/verb × each extreme), then keep the cells that are real
risks for this request. Coverage comes from the request's own nouns crossed with the universal
extremes, so it surfaces edges the request never named.

---

## 3. Provenance tiers (and the anti-laundering rules)

Every fact the design leans on gets one tag. **The tag records where a claim came from — it does
not, by itself, make the claim true.**

- **user-confirmed** — the user *said* it, and you cite **where** (a quote, or a pointer to the
  actual user message). The anchor proves the user said it; it does **not** prove it is true.
  Legitimate **only** for things that are genuinely the user's to decide — a requirement,
  preference, priority, or constraint — where there is nothing in the repo to check against.
- **artifact-verified** — established by *your own* reading of the repo (code, README, config,
  tests), with a *verify-against anchor* (file / symbol / command) so a later run can re-check.
  **This is the only tag that means "checked against evidence."**
- **assumed** — a guess, or any unverified claim. Lowest trust. An **open question**, not a fact.

**Rule 1 — anyone's word is a claim, not proof. Find the evidence yourself.** This is the rule the
weak-model test broke on, so hold it hard. A statement about *how the system actually behaves* —
"X is the source of truth", "the endpoint returns a bool", "the spawn layer already has a queue" —
is a **CLAIM even when the user says it**, and the user can be wrong, vague, or misremembering. You
may **never** record such a claim as verified because the user — or the request wording, or your
own reading of intent — said so. If it is checkable, **go find the evidence in the repo yourself;
only evidence earns `artifact-verified`.** If the evidence contradicts the claim, that is a
conflict — surface it, do not paper over it. **If you cannot find the evidence, you have not
verified anything — ask the user to point you to it, or leave it `assumed` and flagged. Never
launder an unproven claim into a fact.** `user-confirmed` is for decisions the user *owns*, quoted
to their words — not for facts the user (or you) merely *asserts*.

**Rule 2 — anti-laundering on read (load-bearing).** An `assumed` fact must never be read — now or
on a later run — as though it were confirmed. Honored, the record catches drift; violated, it
*launders guesses into facts and spreads them*, which is worse than no record. The tag travels with
the fact on read, not just on write.

**Why both, together.** `user-confirmed` is exactly where a rushed or weak model launders a guess —
or a *misreading of the request* — into "the user said so." (Observed in testing: a model tagged
"no peer-to-peer" as `user-confirmed` when the request literally asked *for* peer-to-peer; a later
run then honored that fabricated tag as a real prior decision and built on it.) A citable anchor
makes the tag **checkable instead of trusted**; requiring evidence for factual claims stops
anyone's word — the user's, or your version of it — from becoming unearned truth.

---

## 4. The filter — what to actually ask

The generator over-produces (nouns × verbs × dimensions is combinatorial). Do not dump it on the
user. Filter each generated risk:

1. **Verifiable from the repo?** → verify it yourself; tag `artifact-verified`. Don't ask.
2. **Load-bearing** (a wrong answer changes the design) **AND unverifiable?** → **ask the user.**
   These are few — usually the same handful the review's step 6 would flag as the riskiest
   decisions.
3. **Neither load-bearing nor verifiable?** → record as `assumed` with the guess, move on.

"Load-bearing" = if this assumption is wrong, some downstream decision flips. Rank by blast radius ×
likelihood; ask the top few, not the tail.

---

## 5. The domain record: format

One file per area at `docs/reviewspec/<build>/design-review.md`. It stores decisions, assumptions, and
links — **not** re-stated domain facts that already live in an authoritative doc (link to those
instead, so you never create a second source of truth). It composes directly from step 0 + the
review:

```markdown
# Design record: <build>

_Last review: <date> · commit <sha>_

## Decision log (append-only — newest first, never edit past entries)
### <date> · round <N> · <trigger: first review | answered Q<n> | conflict | new requirement>
- **Changed:** <the architectural decision that changed this round>
- **Supersedes:** <the prior decision> — **why:** <reason>   (or "— (first review)")
- **Carried over:** <what from prior rounds still holds unchanged>
- **Driver provenance:** <user-confirmed <date> | new requirement | conflict resolution (fact/assumption/decision)>

## Purpose (why this exists)
<the goal recovered from the intent gap — not the solution phrasing>

## Boundary conditions
<from the boundary gap: the edges that matter and the decided handling>
- <noun/verb> at <extreme> → <decided behavior>            [user-confirmed@"<quote/where>" | artifact-verified@<file:symbol> | assumed]

## Invariants / cautions (must never happen)
- <forbidden outcome> — guarded by <mechanism>             [tag @<anchor>]

## Scenarios (trial-and-error walkthroughs)
<the tabletop rows, kept because they are the failure modes this area is known to have>
- <scenario> → observes / returns / operator next step / prior state preserved

## Facts relied on
- <fact> [user-confirmed@"<user's actual words>" <date> | artifact-verified @<file:symbol> | assumed — OPEN QUESTION]
  (a claim about system behavior is artifact-verified or assumed — never user-confirmed on the user's say-so)

## Links (authoritative sources — do not restate)
- domain model: <path> · spec: <path> · key code: <path>

## Open questions
<assumed facts that are load-bearing but still unverified — the next review must resolve these>
```

This file *is* the "domain know-how + purpose + cautions + boundary conditions + trial scenarios"
the user asked for — assembled from the elicited answers plus the original request, with every
claim carrying its provenance.

**Two parts, and the write happens before implementation.** The **current-state** sections are the
fast read — always the latest design, updated in place so nobody follows a retired one. The
**decision log** is the traceability trail — append-only, newest first, and *no past entry is ever
edited or deleted*. A decision is never silently replaced: when a round changes one, update the
current-state section **and** append a log entry (old → new + why). The record is written **before
you implement**, so the architectural intent survives even if the code is abandoned. Together they
answer two different questions: current-state answers "what is the design now?", the log answers
"why did it become this?" — and a reader months later must get the second from the record alone.

---

## 6. Conflict handling on later runs

On run N, after loading the record, compare each new conclusion against it. Classify every
conflict — they resolve differently, so fusing them is wrong (a `merge reductio`: treat a decision
change as a fact error and you nag the user pointlessly; treat a fact error as a decision and you
auto-"resolve" something that was actually broken):

- **Fact conflict** (an `artifact-verified` entry no longer matches the repo) → something changed
  or was misread. Re-verify against current code; update the record.
- **Assumption conflict** (a new finding contradicts an `assumed` entry) → re-verify; the domain
  may have evolved. Never treat the old assumption as the tiebreaker.
- **Decision conflict** (a new decision contradicts a `user-confirmed` decision) → this is the
  "AB conflict nobody noticed" the record exists to catch. **Surface both to the user with their
  provenance; do not auto-resolve.**

Whatever the class, **the resolution is written to the decision log** (§5) as an append-only entry:
what the prior round held, its provenance, the new input, the classification, and how it was
settled. Updating the current-state section is not enough — without the log entry, the *why* of the
change is lost and the next reader cannot trace it. If the prior round's full reasoning is large,
freeze it verbatim in a sibling `_run<N>-snapshot.md` and link it, rather than deleting it.

If the record is missing, unreadable, or corrupt, degrade to a fresh step-0 elicitation and write
a new record — a bad record must never block the review.

---

## Fitness tests for this record mechanism

Shape assertions to keep the mechanism honest (they lock the design-review findings above):

- every record entry carries a provenance tag ∈ {user-confirmed, artifact-verified, assumed};
- `artifact-verified` and `assumed` entries carry a verify-against anchor;
- every `user-confirmed` entry cites the user's actual words (a quote / message pointer) — never
  "from the request" hand-waving that no later reader can check;
- a claim about how the system behaves is `artifact-verified` (evidence found) or `assumed` —
  **never `user-confirmed` on anyone's say-so**; if it is checkable but no evidence was found, it
  stays `assumed`/asked, not promoted to fact;
- a reader treats `assumed` as an open question, never as an established fact (anti-laundering);
- the record links to authoritative domain docs and does not restate facts that live in them;
- a missing/corrupt record degrades to fresh elicitation, never blocks the review;
- conflict output classifies each conflict as fact / assumption / decision, and leaves decision
  conflicts for the user;
- every architecture-touching round appends an immutable dated decision-log entry, and no prior
  entry is edited or deleted (a decision changed without a log entry is a silent overwrite);
- the record is written before implementation code — the decision exists even if the code doesn't.
