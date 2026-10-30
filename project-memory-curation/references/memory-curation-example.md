# Format example

Use this exact shape for the index and every topic file. The content is fictional.

## `docs/memory/MEMORY.md`

```markdown
# Project Memory

- [Local API requires dev certificate](local-api-dev-certificate.md) — why local HTTPS calls fail; open before running the API locally.
```

## `docs/memory/local-api-dev-certificate.md`

```markdown
---
name: local-api-dev-certificate
description: "Why local HTTPS calls to the API fail without the dev certificate, and how to fix it."
metadata:
  type: project
---

## Context

On 2026-03-12, local HTTPS calls to the API failed with a certificate error until the project dev certificate was trusted. Observed on Windows 11 with the API run from `scripts/dev-api.ps1`.

## Why

The failure looks like an API bug but is an environment setup step, so it recurs on every new machine.

## How to apply

When local calls fail with a certificate error, trust the dev certificate with `scripts/trust-dev-cert.ps1`, then retry. Applies to local development only, not to staging or production.

## Evidence

- [Setup decision](../decisions/local-https-setup.md) — approves the dev certificate approach.
```
