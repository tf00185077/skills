# Handoff contracts: spec shape & claims manifest

These are the interchange formats between the three roles (reviewspec-converge → coding → reviewspec-review).
They are as important as any role's internal logic: they're what let independently-run agents line
up on the same intents without talking to each other.

Guiding principle (from the core): the spec describes **intent and observable outcomes** and must
NOT dictate implementation or test method. Its only extra duty is to make each intent's **risk
attributes** determinable, so the risk-tier rule can derive the required scrutiny.

## Spec shape

A spec is a list of **intents**. Each intent:

| Field | Meaning |
|-------|---------|
| `id` | Stable handle, e.g. `INT-1`. The coding agent's manifest references it and the reviewer's findings cite it, so it must not change once assigned. |
| `intent` | What should be true, in outcome terms — not how it's implemented. |
| `observable` | How you'd observe it from outside (a user-visible result, an API response, a stored value). This is what a test asserts on and what break-testing targets. |
| `user_visible` | Does the end user directly see/experience this? (risk attribute) |
| `sensitivity` | Does it touch money / data-loss / security / a core promise? (risk attribute) |

`user_visible` and `sensitivity` exist **only** so the tier can be derived. The spec never states a
test level.

### Artifacts: one folder per round

Each user request is **one round**, and one round gets **its own folder** under `docs/reviewspec/` in
the target project (version-controlled next to the code). Inside that folder live the round's three
artifacts, distinguished by suffix:

```
docs/reviewspec/<build>/
├── <build>.md            ← the spec (this round's request)          — written by reviewspec-converge
├── <build>.manifest.md   ← the claims manifest                      — written by reviewspec-build
└── <build>.review.md     ← the reviewspec-review verdict + coverage map   — written by reviewspec-review
```

Why a folder per round: the spec (an *input*), the manifest (the coding agent's *claims*), and the
review (the gate's *verdict*) are three different kinds of thing produced by three different roles.
Grouping them under one `<build>/` keeps everything about one round together and traceable, while the
`.manifest` / `.review` suffixes keep the *kinds* unambiguous. The base file `<build>.md` (no suffix)
is always the spec.

The rest of this section describes the **spec** file (`<build>.md`); the manifest and review shapes
are defined later in this file and in the reviewspec-review skill respectively.

**This format is a hard contract, not a suggestion.** Everything *inside* the fields is free prose
(the spec's content stays minimal and un-pinned — that's a separate principle). But the *structure*
— field names, the `sensitivity` value set, the `id` scheme, the file location — must not vary,
because three independent agents parse and cross-reference this artifact without talking to each
other. If one writes `sensitivity: 金錢` and another expects `money`, or ids drift between `INT-1`
and `#1`, the coordination the whole system depends on silently breaks. Rigid interface, free
content.

It's **Markdown** — a human reviews and confirms it ("checks the answer"), and the fixed structure
lets the agents parse it reliably. Exactly one block per intent, using these exact keys:

```markdown
# Spec: <feature name>
Context: <1–2 lines of what this is>

## INT-1: <short intent title>
- intent: <the outcome>
- observable: <how it's observed from outside>
- user_visible: yes | no
- sensitivity: money | data-loss | security | core-promise | none

## INT-2: ...
```

Hard rules:
- **`id`** matches `INT-<n>`, assigned once and never renumbered (downstream references depend on it).
- **Field keys** are exactly `intent`, `observable`, `user_visible`, `sensitivity` — lowercase, as
  shown.
- **`user_visible`** is exactly `yes` or `no`.
- **`sensitivity`** is exactly one of `money` | `data-loss` | `security` | `core-promise` | `none`
  (pick the highest-risk one that applies).
- No extra fields, no `test_layer`/`tier` here — the spec never states a test level (that's derived
  downstream).

These rules are machine-checkable. Run the validator to enforce them:

```
python <reviewspec-core>/scripts/validate_spec.py docs/reviewspec/<build>/spec.md
```

With no arguments it checks every spec under `docs/reviewspec/*/` (the `<build>.md` files, skipping
`.manifest.md` / `.review.md`); pass a file or a round folder to target specific ones. Exit code
0 = structurally valid, 1 = errors (warnings, e.g. a missing title, don't fail). It checks
*structure* only — never whether the content is good or complete, which stays a deliberately
un-pinned judgement. The reviewspec-converge agent runs this before handoff, and it can gate CI.

**Good intent:** "A negative transfer amount is rejected and no funds move."
(outcome + observable; `user_visible: yes`; `sensitivity: money`)

**Bad intent:** "Call `validateAmount()` before `doTransfer()` and unit-test it with Jest."
(pins implementation + test method — not the spec's job)

## Claims manifest shape

Handed from the coding agent to the reviewer, written to `docs/reviewspec/<build>/manifest.md`. For
each behavior it implemented + tested:

| Field | Meaning |
|-------|---------|
| `behavior` | Which spec intent this covers (must reference an intent **by its `id`**, e.g. `INT-1`). |
| `test_layer` | unit / integration / E2E. |
| `real_environment` | What real thing it runs against (real API? real DB? real browser? or "mocked X"). The reviewer audits this claim. |
| `self_tier` | The coding agent's own risk-tier assignment, derived via the shared rule. |

The manifest is a set of **claims, not proof**. The reviewer never takes it at face value — it's the
list of things to independently verify.

## How a disagreement resolves

Because both coding and review derive the tier from the same rule and the same spec, a disagreement
about "does this need E2E?" reduces to a disagreement about a risk attribute (`user_visible` /
`sensitivity`). That resolves one of two ways:

1. **The spec text settles it** → whoever misread the attribute is objectively wrong.
2. **The spec is genuinely unclear about the attribute** → this is a *spec-ambiguity*: escalate to
   spec clarification (a human "checks the answer"). It is **not** bounced back and forth between
   coding and review — that's what would create an unpassable loop.

## Cross-round rules (regression)

Each user request is a round; rounds accumulate. A later round must not silently break an earlier
round's certified behavior. The rules:

1. **Prior specs persist and stay in force.** Every `docs/reviewspec/<build>/` remains; its intents stay
   binding unless *formally superseded* (below).
2. **The full accumulated test suite must stay green, every round.** The coding agent runs the whole
   suite (all rounds), not just this round's tests; the reviewspec-review's PASS condition includes the
   entire suite being green.
3. **Every previously-certified intent must keep a passing guarding test.** Losing one (test
   deleted, weakened, or now failing) is a **regression → FAIL**. This is the cheap, reliable
   regression guard: you don't re-break-test old intents every round — you rely on their tests,
   which were *proven sentinels* when they were break-tested at certification. (A merely-green old
   test is not enough; the reason we can trust old green as "no regression" is that it survived
   break-testing once.)
4. **Never weaken or delete an old test to make new code pass** — that's gaming. If an old intent
   genuinely must change, that is a **spec amendment**: edit the prior spec's intent (human confirms
   — it's external correctness), mark it `superseded` in the amending round's review, and update its
   tests deliberately. An old test going red is therefore either an unintended regression (fix the
   code) or an unamended behavior change (escalate as spec-ambiguity) — never "just edit the old
   test green."

### The intent registry (the cross-round collection point)

To enforce rule 3, there is one collection point listing every certified intent and the test that
guards it. It is **generated, not hand-maintained** — `scripts/build_registry.py` derives
`docs/reviewspec/REGISTRY.md` from the per-round `*.review.md` files (which stay the single source of
truth, so nothing drifts). Keyed by `<build>/<id>` (intent ids are per-round, so the slug qualifies
them). Rebuild it each round; the reviewspec-review uses its "active intents" list as the checklist of
tests that must still pass.

```
python <reviewspec-core>/scripts/build_registry.py        # writes docs/reviewspec/REGISTRY.md
```

For the registry to be buildable, each `*.review.md` must carry a machine-readable coverage table —
that format is defined in the reviewspec-review skill.
