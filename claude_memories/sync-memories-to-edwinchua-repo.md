---
name: sync-memories-to-edwinchua-repo
description: "after adding/updating/deleting any memory, mirror the memory dir into the _edwinchua repo and push to main"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7919cfe-71d6-49ec-8777-3f774729d690
---

The canonical memory dir `C:\Users\chuache\.claude\projects\C--Users-chuache\memory\` is mirrored into the git repo at `C:\Users\chuache\Documents\repos\_edwinchua\claude_memories\` so memories sync across devices.

**Why:** the live memory dir is per-device and not version-controlled; the repo is the shared, pushed source of truth across machines.

**How to apply:** immediately after I write, edit, or delete ANY file in the memory dir (including `MEMORY.md`), without asking:
1. Copy the changed memory file(s) — and `MEMORY.md` — into `...\_edwinchua\claude_memories\` (mirror deletes too).
2. In `C:\Users\chuache\Documents\repos\_edwinchua`, `git add claude_memories`, commit with a plain message (no co-author trailer per [[no-claude-coauthor-commits]]), and `git push origin main`.
3. Commit directly to `main` and push — this repo is an Obsidian vault, not feature-branch work, so [[fanout-features-in-worktrees]] does not apply here.

Keep the mirror an exact copy of the live dir. If a memory is renamed/deleted, remove the stale file from the repo folder too.
