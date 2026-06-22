---
name: critique-code-mods-two-agents
description: "After code modifications (in worktrees), always run a separate critique step — 2 agents that review and improve the changes"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de770237-f545-47ff-b275-5854ea77d29a
---

After any **code modification** (which happens in a worktree per [[fanout-features-in-worktrees]]), ALWAYS run a **separate review step**: spawn **2 agents** to critique the changes and **make improvements where applicable**, operating on the worktree (not the main tree).

**Why:** standing preference set 2026-06-09 — code changes are never considered done until independently critiqued.

**How to apply:** once a coding subagent produces changes in a worktree, spawn critique agents that independently review for correctness, security, convention-fit, and simplicity, and apply warranted improvements in that worktree before any merge/apply. Re-validate after improvements. Pairs with [[always-council-and-fanout]] for larger design reviews.
