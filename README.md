# skills

A collection of working-method skills for coding agents (Claude Code / Codex CLI). Each skill lives
in its own folder.

| Skill | What it is |
|-------|------------|
| [think-like-fable](think-like-fable/) | A problem-solving working method: establish ground truth, decompose by uncertainty, route deliberately, change one thing at a time, never claim success without fresh evidence. Installable as a slash command via npm. |
| [code-review-spec](code-review-spec/) | A four-piece system that makes agent-written code reliable enough to skip manual QA: an intent-based spec, a coding role, and an independent review-gate that proves the tests actually catch bugs (break-testing). Includes cross-round regression protection. |

Each folder is self-contained — see its own `README.md` / `SKILL.md` for details.
