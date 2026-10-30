---
name: project-memory-curation
description: Use when consolidating, correcting or reorganizing project memory, especially repeated receipts, mixed topics, duplicate facts or superseded guidance.
---

# Project memory curation

Preserve knowledge that changes a future decision, not a transcript of completed work. Curate meaning and applicability before shortening prose.

## Read and classify

1. Resolve the canonical product root. Keep separate products' memory separate, even inside one company. Read the project entry, index, relevant topics and actual result/decision evidence.
2. For routine review, inspect changed evidence and affected topics. For a bulk cleanup, read all selected input files completely and inspect their relevant formal authorities.
3. Retain a fact only when the situation is likely to recur in future work (a fact bound to one commit, line number or harness revision must be generalized or dropped), affects future judgment, has traceable support and has clear applicability. Exclude routine completion/review receipts, temporary state, milestone verdicts and acceptance history (these live in decisions), secrets and unsupported claims. Before keeping a fact, check whether a canonical project document (engineering, QA, decisions) already states it. If so, keep only the lesson that document lacks and link to it; if nothing is left, do not keep the topic. A qualifier the document omits (such as "this limit belongs to one script, not the platform") counts as a lesson it lacks.
4. Choose the necessary action:

| Action | Decision |
| --- | --- |
| Keep | The existing fact, scope and route are still correct; leave it unchanged. |
| Update | Correct the existing topic and its index summary; do not append a contradictory newer paragraph. |
| Split | Separate independently useful questions/triggers that were bundled together. |
| Merge | Combine overlapping facts or a failure and its bounded correction when they answer the same future question. |
| Remove | Take obsolete/nonreusable material out of active memory, preserving necessary historical evidence with its existing owner. Also remove, or reduce to a one-line pointer, a lesson that a formal document has since adopted. |
| Defer | Identify the exact unsupported claim or conflict; do not invent a fact or stop unrelated authorized work. |

## Reconcile authority and meaning

- Follow explicit approved supersession, not simply the newest timestamp. A pending proposal is not a decision; memory cannot approve scope, permissions, spending or retries.
- Preserve the fact's project, version, host, trigger and uncertainty wherever they bound its validity.
- Keep reasons and operating limits. State the main limit once, in How to apply; do not list every conclusion the evidence fails to support.

## Write the smallest useful store

`docs/memory/MEMORY.md` contains only a heading and one concise relative link per active topic. Each line says what is remembered and when to open it. No procedures, current-status paragraphs, Latest/Prior review blocks or maintenance receipts belong there.

Each `docs/memory/{ref}.md` answers one independently useful question, with a stable kebab-case filename and:

- YAML `name` matching the filename stem, a meaningful retrieval `description`, and `metadata.type: project`.
- `metadata.curated_on: YYYY-MM-DD`: read the current local date from the runtime when writing a changed topic. This is the curation date, not an event or verification date; leave it unchanged on a no-change review.
- **Context:** the recurring situation and the supported conclusion, written so it applies without knowing the original milestone. Mention the source incident in at most one sentence; leave candidate codes, exact values, line numbers and hashes in the evidence source.
- **Why:** its durable importance or approved rationale.
- **How to apply:** future use, practical action and limits.
- **Evidence:** links to durable project decisions, records or retained verification, bound to the claim. Every link must resolve as a file in this repository or as a public `https://` URL; host-relative routes such as `/api/...` or `/ISSUE/...`, local service URLs, sample-relative paths and private backups do not count. If the only supporting record lives in such a service, link the closest durable project document and name the non-portable source in the report.

Split by retrieval need, not paragraph, milestone or date. Do not map old sections or files to topics one-to-one; regroup by the situation in which a reader needs the knowledge. If one situation would make a reader open several topics together, merge them. Merge related observations when their correction needs to be understood together. There is no topic-file quota or target line count.

Follow [the format example](references/memory-curation-example.md) for every index line and topic file.

## Apply safely

- Read fresh bytes and preserve unrelated dirty work. Coordinate a conflicting writer; do not overwrite changes made after the review.
- Before a destructive merge/deletion or bulk replacement, preserve necessary source bytes outside active memory. Git HEAD is not a backup of uncommitted work.
- Create/validate destinations before changing the index or retiring sources. Repair active incoming reading routes (index, agent instructions, documents still in force). Do not edit historical decisions or reports only to update links to a retired memory file.
- Stay within authorized documentation changes. Do not start agents, replay experiments, alter services/permissions, add schedules, or commit/push merely to curate memory.

## Validate and report

Verify the changed topics' metadata/sections (including `curated_on`), one-to-one index/file targets, that every link resolves in the repository or is a public https URL, and relevant incoming routes. Separately read for lost qualifiers, unsupported stronger claims, and repeated disclaimers or incident detail that belongs in evidence. For each changed topic, check that How to apply is still actionable if the reader has never heard of the original candidate or milestone. Check a representative retrieval question after a substantial restructure. Before finishing, write for each active topic the one sentence it adds beyond canonical documents and other topics; merge or remove any topic for which you cannot write that sentence.

The normal deliverable is the updated index/topics and a concise result through the caller's existing reporting mechanism: changed refs and reason, or `Memory review: reviewed; no change`.

If synchronization fails, preserve valid content and report the exact gap and any partial changes already saved. Do not present an incomplete reorganization as complete. Distinguish files actually saved from downstream adoption or runtime behavior actually tested.
