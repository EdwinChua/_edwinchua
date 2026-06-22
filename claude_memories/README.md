# claude_memories

Version-controlled mirror of Claude Code's auto-memory directory, kept here so memories
sync across devices via this repo.

- **Canonical (live) location on this machine:**
  `C:\Users\chuache\.claude\projects\C--Users-chuache\memory\`
- **This folder** is an exact copy of that directory, including the `MEMORY.md` index.

`MEMORY.md` is the index (one line per memory). Each `*.md` file is a single memory with
YAML frontmatter (`name`, `description`, `metadata.type`).

## How it stays in sync

Per the `sync-memories-to-edwinchua-repo` memory, after any memory is added, edited, or
deleted in the live directory, the change is mirrored here and pushed to `main`
automatically.

### Pulling onto another device

This folder is the shared copy. To use it as the live memory on another machine, copy the
files into that device's memory directory (the path under `~/.claude/projects/.../memory/`),
or symlink the live directory to this folder.
