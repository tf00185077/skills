# code-review-spec

A four-piece skill system so that, after an agent writes code, the tests are trustworthy enough that
— within the covered scope — a human doesn't need to test it by hand.

**Core insight:** the goal is not "more tests" but **proving the tests don't lie** (green ≠ correct).
Trust is bought by *break-testing* (deliberately breaking a behavior and confirming a test screams),
not by climbing the test pyramid.

## The pieces

| Folder | Role |
|--------|------|
| [reliable-testing-core](reliable-testing-core/) | Shared foundation the other three import: principles, the "trustworthy test" definition, the risk-tier rule, the handoff contracts (spec / manifest shapes), and the scripts. |
| [spec-authoring](spec-authoring/) | Turns a request into a minimal, intent-based spec; confirms only genuine ambiguities with the human. |
| [reliable-coding](reliable-coding/) | The coding agent: implements + tests against the spec (tiered test-first), keeps real boundaries un-mocked, emits an honest claims manifest. |
| [review-gate](review-gate/) | An **independent** reviewer (different agent from the author): re-derives intents from the spec, break-tests, and issues a three-state verdict. |

## Flow

```
user request
   │  spec-authoring  → docs/specs/<slug>/<slug>.md
   ▼
reliable-coding      → code + tests + docs/specs/<slug>/<slug>.manifest.md
   │
   ▼  review-gate     → docs/specs/<slug>/<slug>.review.md   (PASS / FAIL / SPEC-AMBIGUITY + coverage map)
```

- **Author ≠ judge:** coding and review must be run by different agents, or the gate proves nothing.
- **Internal vs external correctness:** the gate certifies the code matches the spec and the tests
  genuinely verify it; whether the *spec itself* is right is the human's call, discovered by use.
- **One folder per round** under `docs/specs/<slug>/`, holding the spec, the manifest, and the review.

## Scripts (in `reliable-testing-core/scripts/`)

| Script | Purpose |
|--------|---------|
| `validate_spec.py` | Enforce the hard spec format (`docs/specs/<slug>/<slug>.md`). Run before handoff / in CI. |
| `build_registry.py` | Generate `docs/specs/REGISTRY.md` from the per-round review files — the cross-round list of certified intents whose tests must stay green (regression guard). |

## Docs

- [docs/2026-07-27-reliable-testing-review-gate-design.md](docs/2026-07-27-reliable-testing-review-gate-design.md) — the design spec.

## Using it

Each of the four folders is a skill. Point your agent at the relevant `SKILL.md`; the role skills all
begin by loading `reliable-testing-core`. Run the coding and review roles as **separate** agents.
