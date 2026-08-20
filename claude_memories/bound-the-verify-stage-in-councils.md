---
name: bound-the-verify-stage-in-councils
description: "In council workflows, cap the per-finding verify fan-out — N lenses x M concerns each explodes; batch concerns per verifier instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2126a919-7680-4910-b134-e0a6b0cfdf19
  modified: 2026-08-20T00:40:09.503Z
---

In a council/review Workflow, bounding the **council** is not enough — bound what the
council *produces*. A verify stage written as one refuter per concern multiplies:
12 lenses raising ~7 blocking/important concerns each = 83 verifiers, so a run intended
to be ~20 agents became 96 (12 council + 83 verify + 1 synthesis).

Happened 2026-08-19 on the identity-portal "Add user" design council; the user noticed
the agent count before the run finished, and it had to be killed mid-verify.

**Why:** the fan-out width of stage 2 is data-dependent — it is a function of how much
stage 1 found, which is exactly the number you cannot predict when writing the script.
An unbounded `parallel(concerns.map(...))` is a runaway multiplier, not a fan-out.

**How to apply:**
- De-duplicate and cluster findings across lenses *before* verifying (normalize the title,
  group by cited file) — cross-lens duplicates are the bulk of the volume.
- **Batch**: one verifier per ~10 concerns, returning an array of verdicts, so the verify
  stage is ~5-8 agents regardless of what the council found.
- Add an explicit cap and `log()` what was dropped, so silent truncation never reads as
  full coverage.
- Verifiers are per-claim checking work → `model: 'sonnet'`, see
  [[sonnet-subagents-by-default]].

Also: **`resumeFromRunId` is same-session only.** If a long workflow may outlive the
session, salvage completed agents' structured output to a durable file before stopping —
the transcripts under the workflow dir hold the `StructuredOutput` tool inputs and can be
extracted programmatically without reading them into context.

Related: [[always-council-and-fanout]].
