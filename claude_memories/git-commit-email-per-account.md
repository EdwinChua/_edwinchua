---
name: git-commit-email-per-account
description: "git commit identity — personal email for github.com/EdwinChua repos, work email elsewhere"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7919cfe-71d6-49ec-8777-3f774729d690
---

Use the right commit email per account:
- **Personal** — repos under `https://github.com/EdwinChua` → `3dw1nchu4@gmail.com` (name: Edwin Chua).
- **Work** — everything else → work email `edwin_chua@a-star.edu.sg`.

**Why:** keeps personal and A*STAR work commit attribution cleanly separated across the same machine.

**How to apply:** this is wired in git, not just behavioral — `~/.gitconfig` has conditional includes (`includeIf "hasconfig:remote.*.url:https://github.com/EdwinChua/**"` and the `git@github.com:EdwinChua/**` SSH form) pointing to `~/.gitconfig-personal`, which sets the personal name/email. Any repo with an EdwinChua remote auto-resolves to the personal email; all other repos fall back to the global default (work). When creating a new personal repo, just add the EdwinChua remote and the email is correct automatically — no per-repo config needed.

Note: the global default is currently `edwin_chua@simtech.a-star.edu.sg` (a subdomain of the stated work address); left as-is. Relates to [[no-claude-coauthor-commits]].
