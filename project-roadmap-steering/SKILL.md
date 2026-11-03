---
name: project-roadmap-steering
description: Use when you plan or choose a project's work — at project start, after accepting or rejecting a task result, before writing the next task, or when work seems to drift from the goal. Keeps a goal-based ROADMAP, a one-page CURRENT state and an append-only PROGRESS history, and states exactly when the owner must decide.
---

# Project roadmap steering

Keep the project's direction stable across fresh sessions. Deciding *what* to propose and *which* task to pick is your judgment. Deciding *when* to stop and ask the owner is a rule: follow the triggers below even when the next step looks reasonable, because drift is invisible one step at a time.

## Three documents, three jobs

| Document | Job | Who changes it |
| --- | --- | --- |
| `docs/ROADMAP.md` | Where the project is going and how to choose work | The owner approves; you draft and propose changes |
| `docs/CURRENT.md` | One page: where the project is now | You overwrite it after every result |
| `docs/PROGRESS.md` | History of what happened | You append to it; never rewrite earlier entries |

Use the project's own paths if it names others. Follow [the format example](references/roadmap-example.md) for ROADMAP, CURRENT, a task Purpose paragraph and an owner question.

## Who decides what

- **The owner decides** the destination, the milestones with their order and exit criteria, the Not-now list, the task-selection rule and the escalation thresholds. An answer relayed by an authorized liaison counts as the owner's decision only within that liaison's recorded delegation. Silence, a pending question or your own recommendation is not approval.
- **You decide**, within an approved ROADMAP: which task comes next, how to scope and write it, whether evidence meets an exit criterion (state the evidence), and what to propose when a trigger fires.
- Existing authority boundaries still apply. Spec, architecture, spending, permissions and publication stay with whoever the project's owner direction names.

## ROADMAP: required sections

1. **Destination**: the experience or outcome the project exists to deliver, not a feature list.
2. **Milestones**: for each, the question it answers, observable exit criteria (including owner feedback when the question is about value or feel), and status: `not started`, `active`, `exit claimed` or `done`. Detail the active milestone. Give the next one a question and exit criteria only. Give later ones a direction only.
3. **Not now**: work that is deliberately excluded until a named milestone or decision.
4. **Task-selection rule**: an ordered priority list the owner approved.
5. **Escalation thresholds**: the owner's values for the triggers below, such as the maximum number of consecutive tasks that do not advance the active milestone's question, and the maximum days blocked.
6. **Review history**: date, what changed and the reference to the owner's approval.

If the ROADMAP is missing or incomplete, draft it from the project's goal, spec and recorded owner decisions. Mark each unresolved choice `OWNER DECISION NEEDED`, give 2–4 options with your recommendation, and escalate. Until the owner answers, choose only work that existing approved documents already require, and say so in CURRENT.

## CURRENT: one page, overwritten

Write in plain language for a reader with no history. Use links, not hashes or ledger counts. Include:

- The latest accepted build or deliverable, and how the owner can try it.
- The active milestone and what remains before its exit criteria.
- Active tasks, each with the milestone question it serves.
- Blockers, with the date each started.
- The next 1–3 candidate tasks, in task-selection-rule order.
- Pending owner decisions.
- The trigger counters: consecutive tasks that did not advance the active question, and the longest current block.

Keep it to about one screen. Move detail into PROGRESS or the task records.

## Choose the next task

1. Read ROADMAP, CURRENT, the owner direction and open tasks.
2. List the candidates. For each one, write the milestone question it advances, or the higher-priority item it unblocks. Do not choose a candidate that does neither. If such work seems necessary, it is a ROADMAP change: escalate.
3. Rank the candidates with the task-selection rule.
4. Check every escalation trigger before dispatching.
5. Open the task contract with a **Purpose** paragraph: the milestone, the question it serves, which trade-off matters most, and what is out of scope. Workers should need only their contract and the documents it names, not PROGRESS.

## Escalate to the owner: mandatory triggers

Stop starting new work in the affected direction and ask the owner when any of these is true:

- The active milestone's exit criteria are met, or you are about to claim they are. The owner confirms the claim and chooses what comes next.
- The next task is not covered by the ROADMAP, or it would add, drop or reorder a milestone or a Not-now item.
- The consecutive-task threshold or the blocked threshold is reached.
- The work needs a change to the approved spec, architecture or scope.
- The ROADMAP is missing, or an `OWNER DECISION NEEDED` item blocks task selection.

Write the question so the owner can answer it without reading history: the situation in 2–3 sentences, 2–4 options with their consequences, your recommendation, and what continues while waiting. Send it through the project's owner-question channel; where `paperclip-hermes-notify` is installed, that skill is the channel. Record the pending decision in CURRENT. While waiting, finish in-flight work that is inside the approved milestone. Do not open a new direction.

## Maintenance rules

- After each task result is accepted or rejected: append a short PROGRESS entry, overwrite CURRENT and update the trigger counters.
- When a milestone's status changes or the owner answers: update the ROADMAP and its review history.
- Never edit earlier PROGRESS entries. PROGRESS is history for tracing. It is not required reading for other roles.

## Validate before finishing a planning turn

- CURRENT reflects the latest result and today's date.
- Every active task names the milestone question it serves.
- No trigger condition is met without a recorded pending owner question.
- Every in-force milestone has an owner-approval reference in the review history.

Report what you dispatched or proposed, and why, through the caller's existing reporting mechanism.
