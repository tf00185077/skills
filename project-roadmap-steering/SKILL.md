---
name: project-roadmap-steering
description: Use when you plan or choose a project's work — at project start, after accepting or rejecting a task result, before writing the next task, or when work seems to drift from the goal. Derives a ROADMAP from the project's destination and riskiest unknowns, keeps a one-page CURRENT and an append-only PROGRESS, and states exactly when the owner must decide.
---

# Project roadmap steering

Keep the project's direction stable across fresh sessions. Derive each part of the ROADMAP from the part before it: destination, then unknowns, then the cheapest evidence for each unknown, then milestones, then what to leave out and how to choose work. When a later part does not follow from an earlier one, fix the derivation instead of adding a rule.

What to propose and which task to pick are your judgment. When to stop and ask the owner is a rule. Follow the triggers below even when the next step looks reasonable, because drift is invisible one step at a time.

## Three documents, three jobs

| Document | Job | Who changes it |
| --- | --- | --- |
| `docs/roadmap/ROADMAP.md` | Where the project is going and how to choose work | The owner approves; you draft and propose changes |
| `docs/CURRENT.md` | One page: where the project is now | You overwrite it after every result |
| `docs/PROGRESS.md` | History of what happened | You append to it; never rewrite earlier entries |

Keep the ROADMAP in its own folder at `docs/roadmap/`, like `docs/memory/`. Create the folder if it is missing, and write its links relative to `docs/roadmap/`. Follow [the format examples](references/roadmap-example.md).

## Who decides what

- **The owner decides** the destination and constraints, the milestones with their order and exit criteria, the Not-now list, the task-selection rule and the escalation thresholds. An answer relayed by an authorized liaison counts as the owner's decision only within that liaison's recorded delegation. Silence, a pending question or your own recommendation is not approval.
- **You decide**, within an approved ROADMAP: which task comes next, how to scope and write it, whether evidence meets an exit criterion (state the evidence), and what to propose when a trigger fires.
- Existing authority boundaries still apply. Spec, architecture, spending, permissions and publication stay with whoever the project's owner direction names.

## Build the ROADMAP in this order

1. **Destination and constraints.** Who the project serves, the outcome they get, and the signal that shows it worked. List the fixed constraints: deadlines, contracted or approved scope, systems that must not change. Take these from the project's goal, spec and recorded owner decisions; do not invent them.
2. **Unknowns.** List what could make the destination wrong or unreachable. Common types include value, usability, feasibility, compatibility, delivery and schedule. There is no default order. Rank by the cost of being wrong: how much finished work would be wasted or redone if the assumption proved false.
3. **Cheapest evidence.** For each top unknown, name the cheapest step that produces real evidence about it: the actual product or system meeting actual users or conditions. A completed internal process is not evidence about an unknown.
4. **Milestones.** Make one milestone per top unknown, in rank order; when two rank equally, put the one with cheaper evidence first. For each milestone, record:
   - its question, about the product, its users or its operation, not about finishing a process;
   - its evidence path, starting from the cheapest evidence;
   - exit criteria: that evidence plus confirmation by whoever can judge it;
   - its status: `not started`, `active`, `exit claimed` or `done`.

   Delivery, verification and tooling work are tasks inside a milestone, not milestones of their own. If the unknown is itself about delivery, phrase the question about operation, such as whether the intended operators can install and run it. Detail the active milestone. Give the next one a question and exit criteria only. Give later ones a direction only. When a planned path waits longer or costs more than the cheapest evidence, state the difference and offer both paths to the owner as options.
5. **Not now.** Everything that produces no evidence for the active or next milestone's question. Name the milestone or decision that would revisit each item.
6. **Task selection and thresholds.** A task advances a milestone only if it is a step on that milestone's evidence path. A prerequisite counts only when the path cannot proceed without it. The owner approves the priority order for choosing among candidates and the threshold values: the maximum consecutive tasks that do not advance the active milestone, and the maximum days blocked.
7. **Reader test.** Could the person who decides act on this page alone? Replace internal codes, identifiers and ledger counts with plain descriptions and links. Cut disclaimers that change no decision. Apply the same test to CURRENT and to every owner question.

Record every approval in a **Review history**: the date, what changed and a reference to the owner's approval.

If the ROADMAP is missing or incomplete, draft it in this order from the existing documents. Mark each unresolved choice `OWNER DECISION NEEDED`, give 2–4 options with your recommendation, and escalate. Until the owner answers, choose only work that existing approved documents already require, and say so in CURRENT.

When a milestone's evidence arrives or a constraint changes, return to step 2, re-rank the unknowns and propose the resulting changes to the owner.

## CURRENT: one page, overwritten

Include:

- The latest accepted deliverable, and how the owner can see or try it.
- The active milestone, and what remains on its evidence path.
- Active tasks, each with the evidence-path step it serves.
- Blockers, with the date each started.
- The next 1–3 candidate tasks, in priority order.
- Pending owner decisions.
- The trigger counters: consecutive non-advancing tasks, and the longest current block.

Keep it to about one screen; move detail into PROGRESS or the task records.

## Choose the next task

1. Read ROADMAP, CURRENT, the owner direction and open tasks.
2. For each candidate, name the evidence-path step it serves. A candidate that serves none is not chosen. If it seems necessary anyway, the ROADMAP needs to change: escalate.
3. Rank the candidates with the approved priority order.
4. Check every escalation trigger before dispatching.
5. Open the task contract with a **Purpose** paragraph: the milestone, its question, the evidence this task helps produce, which trade-off matters most, and what is out of scope. Workers should need only their contract and the documents it names, not PROGRESS.

## Escalate to the owner: mandatory triggers

Stop starting new work in the affected direction and ask the owner when any of these is true:

- The active milestone's exit criteria are met, or you are about to claim they are. The owner confirms the claim and chooses what comes next.
- The next task is not on the active milestone's evidence path, or it would add, drop or reorder a milestone or a Not-now item.
- The consecutive-task threshold or the blocked threshold is reached.
- The work needs a change to the approved spec, architecture, scope or constraints.
- The ROADMAP is missing, or an `OWNER DECISION NEEDED` item blocks task selection.

Each owner question states the situation in 2–3 sentences and gives 2–4 options. For each option, say what it costs and how soon it produces the evidence the active milestone needs. Add your recommendation and what continues while waiting. Send the question through the project's owner-question channel; where `paperclip-hermes-notify` is installed, that skill is the channel. Record the pending decision in CURRENT. While waiting, finish in-flight work on the approved evidence path. Do not open a new direction.

## Maintenance rules

- After each task result is accepted or rejected: append a short PROGRESS entry, overwrite CURRENT and update the trigger counters.
- When a milestone's status changes or the owner answers: update the ROADMAP and its Review history.
- Never edit earlier PROGRESS entries. PROGRESS is history for tracing, not required reading for other roles. Preserve each file's existing line endings and encoding.

## Validate before finishing a planning turn

- Each milestone question is about the product, its users or its operation, and names its evidence path.
- Each active task names the evidence-path step it serves.
- CURRENT reflects the latest result and today's date.
- No trigger condition is met without a recorded pending owner question.
- Each in-force milestone has an owner-approval reference in the Review history.
- The ROADMAP, CURRENT and any owner question pass the reader test.

Report what you dispatched or proposed, and why, through the caller's existing reporting mechanism.
