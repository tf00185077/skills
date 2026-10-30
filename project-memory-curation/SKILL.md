---
name: project-memory-curation
description: Use when consolidating, correcting or reorganizing project memory, especially repeated receipts, mixed topics, duplicate facts or superseded guidance.
---

# Project memory curation

Preserve knowledge that changes a future decision, not a transcript of completed work. Curate meaning and applicability before shortening prose.

## Read and classify

1. Resolve the canonical product root and existing document owners. Keep separate products' memory separate, even inside one company. Read the project entry, index, relevant topics and actual result/decision evidence.
2. For routine review, inspect changed evidence and affected topics. For a bulk cleanup, read all selected input files completely and inspect their relevant formal authorities. Do not reread every transcript merely to prove diligence.
3. Retain a fact only when it remains useful beyond the task, affects future judgment, has traceable support and has clear applicability. Exclude routine completion/review receipts, temporary state, secrets and unsupported claims. Keep candidate-specific counts/budgets with their original owners unless a precise value is needed to understand the reusable fact.
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
- Preserve the fact's project, candidate/version, host, trigger and uncertainty wherever they bound its validity. A historical successful build is not current runtime readiness; source/static acceptance is not integration or release acceptance.
- Keep reasons and operating limits. Do not turn a script-specific guard into a platform constant, a corrected harness into a product fix, or an unexecuted branch into an observed result.
- Retain meaningful evidence requirements explicitly: actual source/export hashes are not merely “provenance.” Distinguish authored work from generated output and use the applicable contract rather than copying its full tables into memory.

## Write the smallest useful store

`docs/memory/MEMORY.md` contains only a heading and one concise relative link per active topic. Each line says what is remembered and when to open it. No procedures, current-status paragraphs, Latest/Prior review blocks or maintenance receipts belong there.

Each `docs/memory/{ref}.md` answers one independently useful question, with a stable kebab-case filename and:

- YAML `name` matching the filename stem, a meaningful retrieval `description`, and `metadata.type: project`.
- **Context:** the supported fact, triggering conditions and only necessary incident detail.
- **Why:** its durable importance or approved rationale.
- **How to apply:** future use, practical action and limits.
- **Evidence:** real canonical decisions, records or retained verification, bound to the claim.

Split by retrieval need, not paragraph, milestone or date. Merge related observations when their correction needs to be understood together. There is no topic-file quota or target line count. A smaller index can coexist with more total Markdown; do not claim token/latency savings without measuring them.

Use [the anonymized worked example](references/memory-curation-example.md) when learning the transformation or reviewing an ambiguous split/merge/supersession. It is example data, not another project's operating policy.

## Apply safely

- Read fresh bytes and preserve unrelated dirty work. Coordinate a conflicting writer; do not overwrite changes made after the review.
- Before a destructive merge/deletion or bulk replacement, preserve necessary source bytes outside active memory. Prefer existing retained evidence over creating a duplicate archive. Git HEAD is not a backup of uncommitted work.
- Create/validate destinations before changing the index or retiring sources. Repair active incoming reading routes. Historical citations may point to an unchanged retained witness; do not rewrite historical verdicts or edit frozen deliveries.
- Use canonical project/native evidence links in active topics. Sample-relative paths, audit outputs and private rollback backups are not substitutes for a usable project evidence route.
- Stay within authorized documentation changes. Do not start agents, replay experiments, alter services/permissions, add schedules, or commit/push merely to curate memory.

## Validate and report

Verify the changed topics' metadata/sections, one-to-one index/file targets, relative links and relevant incoming routes. Separately read for lost qualifiers, contradictory defaults and unsupported stronger claims. Check a representative retrieval question after a substantial restructure. Use the smallest adequate checks; an independent model review is not required on every routine edit.

The normal deliverable is the updated index/topics and a concise result through the caller's existing reporting mechanism: changed refs and reason, or `Memory review: reviewed; no change`. Do not create a task, waiting comment or another agent wake solely to record a review. No mandatory verification folder, JSON/CSV ledger, before/after package or independent review report is required.

If synchronization fails, preserve valid content and report the exact gap and any partial changes already saved. Do not present an incomplete reorganization as complete or replay product work to fill evidence gaps. Distinguish files actually saved from downstream adoption or runtime behavior actually tested.
