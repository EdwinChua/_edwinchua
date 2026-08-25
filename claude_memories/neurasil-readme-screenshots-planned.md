---
name: neurasil-readme-screenshots-planned
description: Planned for 2026-08-26 - generate mock data in neurasil, screenshot the UI, add the shots to README
metadata:
  node_type: memory
  type: project
---

Planned for **2026-08-26**, deliberately not started on 2026-08-25: generate mock data in
neurasil, then have Claude take screenshots of the web app and add them to `README.md`.

**Why:** the README became the public front page on 2026-08-25 (trimmed 167 -> 41 lines, deep
rationale moved to `docs/DESIGN.md` and `docs/ACCOUNTS.md`) and it has no images of the thing it
describes. Mock data first because the live vault holds the owner's real finance, alcohol and
Japanese-study data, which should not be in screenshots on a public repo.

**How to apply:** the **work** Cognito account
(`19eaf5ac-7091-704d-35a4-e061773459f2`, edwin_chua@a-star.edu.sg) is an ideal clean room for
this. As of 2026-08-25 it owns nothing at all, and the per-account filter shipped the same day
means anything created under it is invisible to the personal account and vice versa - so mock
data can be built, shot, and deleted without touching real data or needing a separate
deployment. See [[neurasil-vault-mcp-server]].

Screenshots worth having, roughly: the vault tree with a populated sidebar, a table grid, the
SQL query view, and a note with blocks. The brand assets already in `ui/public/brand/` are the
source for any framing.
