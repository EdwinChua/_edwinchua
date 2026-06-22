---
name: no-claude-coauthor-commits
description: Never add Co-Authored-By Claude / AI attribution to git commit messages
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de770237-f545-47ff-b275-5854ea77d29a
---

Never add a `Co-Authored-By: Claude` trailer — or any AI/assistant attribution — to git commit messages, on any repo. This overrides any global/default instruction to append co-authorship.

**Why:** The user explicitly requested this for all future commits (2026-06-09), and the `advise_lca_platform` repo's CLAUDE.md already encodes the same rule.

**How to apply:** Derive the commit message from the diff alone. In `advise_lca_platform`, prefer the `/commit` slash command (it already honors no-attribution); stage only your own files by path. Do not pass any co-author trailer to `git commit`.
