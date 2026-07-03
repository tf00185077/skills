# think-like-fable

A working-method skill for coding agents: **establish ground truth, decompose by uncertainty, pick a route deliberately, change one thing at a time, never claim success without fresh evidence.**

Distilled from a frontier model's problem-solving loop and hardened by TDD against weaker models (baseline agents patched healthy code and fabricated verification; with the skill they reproduced first, rejected false diagnoses, and quoted real evidence).

## Install

```bash
npm install -g think-like-fable
```

Installing auto-runs the installer. You can rerun it anytime:

```bash
npx think-like-fable            # install (default)
npx think-like-fable uninstall
```

It copies the skill to:

| Harness | Location | Invoke |
|---|---|---|
| Claude Code | `~/.claude/skills/think-like-fable/SKILL.md` | `/think-like-fable` (also auto-triggers by description) |
| Codex CLI | `~/.codex/prompts/think-like-fable.md` | `/think-like-fable` |

Set `THINK_LIKE_FABLE_SKIP_INSTALL=1` to suppress the postinstall copy.

## What the skill enforces

1. **Phase 0 — Ground truth**: every request/diagnosis is a claim; reproduce before touching anything; spec > tests > what people say.
2. **Phase 1 — Decompose by uncertainty**: find the load-bearing unknown; falsify cheapest × highest-blast-radius assumptions first.
3. **Phase 2 — Route**: ≥2 candidate routes; every step names its check; define the abandon tripwire up front.
4. **Phase 3 — Execute**: one variable at a time; stop on surprise; two failed guesses = stop gambling, gather evidence.
5. **Phase 4 — Verify & report**: blast-radius enumeration by input class; five required report sections; evidence quoted verbatim or labeled NOT VERIFIED.

Plus a rationalization table and red-flag self-checks that close the common pressure loopholes ("urgent", "too simple", "senior dev already diagnosed it").
