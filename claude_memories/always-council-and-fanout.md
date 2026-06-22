---
name: always-council-and-fanout
description: User wants a 20-agent council for design discussions and subagent fan-out for substantial/parallel work
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de770237-f545-47ff-b275-5854ea77d29a
---

Before starting **any** task sequentially, pause and look for opportunities to fan out subagents — make parallel delegation the default reflex, not an afterthought. For substantial design/architecture decisions, convene a **20-subagent council** (Workflow tool) to debate/affirm the course before finalizing, and **fan out subagents** for parallelizable or broad work rather than doing it inline.

**Why:** the user set this as a standing preference (2026-06-09) during the admin-portal-integration work — "always fan out subagents where necessary. always discuss with a 20 subagent council." Reaffirmed and broadened (2026-06-22): "before jumping onto any task sequentially, look for opportunities to fan out subagents."

**How to apply:** at the start of every task, ask "can this be parallelized across subagents?" before doing it inline; before major doc updates or design commits, run a ~20-member council; default to delegating broad/parallel exploration and review to subagents. Relates to [[no-claude-coauthor-commits]] and [[critique-code-mods-two-agents]].
