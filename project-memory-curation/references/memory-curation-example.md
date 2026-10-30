# Format example

Use this exact shape for the index and every topic file. The content and evidence path are fictional; `curated_on` illustrates the curation date, not the event date.

## `docs/memory/MEMORY.md`

```markdown
# Project Memory

- [Local API dev certificate setup](local-api-dev-certificate.md) — diagnose the recorded Windows dev-certificate trust error before applying the approved fix.
```

## `docs/memory/local-api-dev-certificate.md`

```markdown
---
name: local-api-dev-certificate
description: "Diagnose the recorded Windows local-API certificate trust error and apply the approved development-only setup."
metadata:
  type: project
  curated_on: "2026-10-30"
---

## Context

Local HTTPS calls to the API failed with a certificate error until the project dev certificate was trusted. Observed on Windows 11 with the API run from `scripts/dev-api.ps1`.

## Why

This setup issue can recur in a new development environment where the project dev certificate is not trusted.

## How to apply

For the recorded Windows development setup, first confirm that the error is caused by the untrusted project dev certificate, then follow the approved setup using `scripts/trust-dev-cert.ps1` and retry. Applies only to this error in local development.

## Evidence

- [Setup decision](../decisions/local-https-setup.md) — approves the dev certificate approach.
```
