# skills

A collection of working-method skills for coding agents (Claude Code / Codex CLI). Each skill lives
in its own folder.

| Skill | What it is |
|-------|------------|
| [think-like-fable](think-like-fable/) | A problem-solving working method: establish ground truth, decompose by uncertainty, route deliberately, change one thing at a time, never claim success without fresh evidence. Installable as a slash command via npm. |
| [code-review-spec](code-review-spec/) | A four-piece system that makes agent-written code reliable enough to skip manual QA: an intent-based spec, a coding role, and an independent review-gate that proves the tests actually catch bugs (break-testing). Includes cross-round regression protection. |
| [smoothing-3d-contours](smoothing-3d-contours/SKILL.md) | Refine Blender silhouettes, curves, and surfaces for smooth flow while preserving intended features and deformation behavior. |
| [refining-anime-eyes](refining-anime-eyes/SKILL.md) | Refine anime eye shapes, eyelash linework, double-eyelid creases, iris shading, and highlights against a visual reference, with saved-model verification. |
| [refining-3d-hair](refining-3d-hair/SKILL.md) | Refine Blender hair surface quality, clump hierarchy, and smooth flow while preserving the character's hairstyle. |
| [project-memory-curation](project-memory-curation/SKILL.md) | Curate durable project knowledge into a thin index and focused topics, with authority checks, safe edits and a fictional format example. Role-neutral; no scheduling or agent setup. |

Each folder is self-contained — see its own `README.md` / `SKILL.md` for details.
