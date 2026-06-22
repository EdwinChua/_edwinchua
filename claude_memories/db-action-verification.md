---
name: db-action-verification
description: "DB actions must be verified — low-risk by 1 subagent, high-risk by a 5-agent council; the LCA dev DB is read-only"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: de770237-f545-47ff-b275-5854ea77d29a
---

For ANY database action the user asks for:
- **LOW-RISK** actions (reads, schema introspection, `SELECT`) — verified by a **single subagent**.
- **HIGH-RISK** actions (`CREATE`/`ALTER`/`UPDATE`/`DELETE`/`DROP`/`INSERT`, migrations, any mutation) — validated by a **5-subagent council** BEFORE execution.

**The LCA platform DEV database is READ-ONLY / source-of-truth:** NEVER run any mutating statement (CREATE/UPDATE/DELETE/DROP/ALTER/INSERT) on dev. Only `localhost` (or the explicitly targeted non-dev DB) may receive schema changes — and those are the high-risk path requiring the 5-agent council.

**Why:** standing preference set 2026-06-09. **How to apply:** route DB work through subagents per the risk tier above; treat dev connections as read-only introspection only. Pairs with [[always-council-and-fanout]].
