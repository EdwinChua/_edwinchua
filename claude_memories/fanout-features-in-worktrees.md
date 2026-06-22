---
name: fanout-features-in-worktrees
description: "Coding work lands on the ACTIVE BRANCH of each project; worktrees are transient-only, not where work is left"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de770237-f545-47ff-b275-5854ea77d29a
---

For coding work on the codebase, the user prefers the result **committed to the ACTIVE BRANCH** of each project — **not** left on separate worktree branches.

**Clarified 2026-06-09** ("I prefer to have all work done on the active branch of each project instead of the worktree"), superseding the earlier "always use worktrees" instruction.

**How to apply:** work directly on the active branch. If isolated/parallel subagent worktrees are used transiently (e.g. for fan-out), **merge the result back onto the active branch** when done and remove the worktree. When another session has uncommitted changes on the active branch (e.g. portal `main`), stage only your own files by path and don't disturb theirs. Pairs with [[critique-code-mods-two-agents]] and [[db-action-verification]].
