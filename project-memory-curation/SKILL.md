---
name: project-memory-curation
description: Use when consolidating, correcting or reorganizing project memory, especially repeated receipts, mixed topics, duplicate facts or superseded guidance.
---

# Project memory curation

Preserve knowledge that changes a future decision, not a transcript of completed work. Curate meaning and applicability before shortening prose.

## Read and classify

1. Resolve the canonical product root. Keep separate products' memory separate, even inside one company. Read the project entry, index, relevant topics and actual result/decision evidence.
2. For routine review, inspect changed evidence and affected topics. For a bulk cleanup, read all selected input files completely and inspect their relevant formal authorities.
3. Retain a fact only when it remains useful beyond the task, affects future judgment, has traceable support and has clear applicability. Exclude routine completion/review receipts, temporary state, secrets and unsupported claims.
4. Choose the necessary action:

| Action | Decision |
| --- | --- |
| Keep | The existing fact, scope and route are still correct; leave it unchanged. |
| Update | Correct the existing topic and its index summary; do not append a contradictory newer paragraph. |
| Split | Separate independently useful questions/triggers that were bundled together. |
| Merge | Combine overlapping facts or a failure and its bounded correction when they answer the same future question. |
| Remove | Take obsolete/nonreusable material out of active memory, preserving necessary historical evidence with its existing owner. |
| Defer | Identify the exact unsupported claim or conflict; do not invent a fact or stop unrelated authorized work. |

## Reconcile authority and meaning

- Follow explicit approved supersession, not simply the newest timestamp. A pending proposal is not a decision; memory cannot approve scope, permissions, spending or retries.
- Preserve the fact's project, candidate/version, host, trigger and uncertainty wherever they bound its validity.
- Keep reasons and operating limits. Do not state a fact more broadly or more strongly than its evidence supports.
- Write dates as absolute dates (`YYYY-MM-DD`). Replace relative references such as "yesterday", "last week" or "recently" with the actual date.

## Write the smallest useful store

`docs/memory/MEMORY.md` contains only a heading and one concise relative link per active topic. Each line says what is remembered and when to open it. No procedures, current-status paragraphs, Latest/Prior review blocks or maintenance receipts belong there.

Each `docs/memory/{ref}.md` answers one independently useful question, with a stable kebab-case filename and:

- YAML `name` matching the filename stem, a meaningful retrieval `description`, and `metadata.type: project`.
- **Context:** the supported fact, triggering conditions and only necessary incident detail.
- **Why:** its durable importance or approved rationale.
- **How to apply:** future use, practical action and limits.
- **Evidence:** real canonical decisions, records or retained verification, bound to the claim.

Split by retrieval need, not paragraph, milestone or date. Merge related observations when their correction needs to be understood together. There is no topic-file quota or target line count.

Follow [the format example](references/memory-curation-example.md) for every index line and topic file.

## Apply safely

- Read fresh bytes and preserve unrelated dirty work. Coordinate a conflicting writer; do not overwrite changes made after the review.
- Before a destructive merge/deletion or bulk replacement, preserve necessary source bytes outside active memory. Git HEAD is not a backup of uncommitted work.
- Create/validate destinations before changing the index or retiring sources. Repair active incoming reading routes.
- Use canonical project/native evidence links in active topics. Sample-relative paths, audit outputs and private rollback backups are not substitutes for a usable project evidence route.
- Stay within authorized documentation changes. Do not start agents, replay experiments, alter services/permissions, add schedules, or commit/push merely to curate memory.

## Validate and report

Verify the changed topics' metadata/sections, one-to-one index/file targets, relative links and relevant incoming routes. Separately read for lost qualifiers, contradictory defaults and unsupported stronger claims. Check a representative retrieval question after a substantial restructure.

The normal deliverable is the updated index/topics and a concise result through the caller's existing reporting mechanism: changed refs and reason, or `Memory review: reviewed; no change`.

If synchronization fails, preserve valid content and report the exact gap and any partial changes already saved. Do not present an incomplete reorganization as complete. Distinguish files actually saved from downstream adoption or runtime behavior actually tested.
