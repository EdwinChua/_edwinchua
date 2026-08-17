---
name: db-query-means-report-rows
description: "When asked to query a DB and state what's there, report the rows only — don't go read application code to interpret or explain them"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6c3b7b7d-0912-4425-9199-90239b911397
  modified: 2026-08-17T07:18:43.581Z
---

When Edwin asks to **query a database and state what is there**, the deliverable is the rows.
Do not follow up by reading application/platform code to explain *why* a value is what it is, what a
flag enforces, or what a missing grant implies — and do not spawn a subagent to do that either.
Surfacing a notable field value in one line is fine; going and researching it is not.

**Why:** he asks these questions when he already knows the system and just needs the current state.
Code-reading to interpret the result adds latency and answers a question he didn't ask. (Observed
2026-08-17 on an Identity Portal prod feature-grant query: he interrupted a verification subagent
that had been sent to read `features.service.ts` / platform `access_control.py` to explain why the
org lacked the AI feature.)

**How to apply:** schema lookup *before* writing the query is fine and often necessary (finding the
real table/column names). After the rows come back, stop — present them and let him ask. Note that
the "low-risk DB read → verify with a single subagent" rule in CLAUDE.md means sanity-checking the
query, not researching the domain meaning of the result.

Query recipe: [[portal-prod-db-query-recipe]]. Related: [[always-council-and-fanout]],
[[etea-feature-split-design]].
