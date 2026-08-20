---
name: sonnet-subagents-by-default
description: Default subagent/workflow-agent model is Sonnet; reserve the session model (Opus) for the final synthesis or genuinely hard reasoning
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2126a919-7680-4910-b134-e0a6b0cfdf19
  modified: 2026-08-20T00:40:03.275Z
---

When fanning out subagents or writing Workflow scripts, **pass `model: 'sonnet'` on the
worker agents** rather than letting them inherit the session model. Reserve the stronger
model for the one stage that actually needs it — the final synthesis / judge / plan-author.

Stated by the user 2026-08-20 while resuming the identity-portal "Add user" work, right
after a 96-agent council run.

**Why:** the bulk of fan-out work — repo mapping, grepping, reading a file and reporting
what is in it, verifying one bounded claim against one cited location — is retrieval and
checking, not hard reasoning. Sonnet does it at a fraction of the cost, and the cost of a
wide fan-out is multiplied by the agent count, so the model choice on the *workers* is
what dominates the bill.

**How to apply:**
- `Agent` tool: `model: 'sonnet'` for Explore / mapping / verification agents.
- `Workflow` scripts: `opts.model = 'sonnet'` on every fan-out stage; omit it on the
  synthesis stage so it inherits. Pair with `effort: 'low'` for mechanical stages.
- Keep the session model for: final synthesis, adversarial judging where a wrong verdict
  is expensive, and anything writing the actual plan or code.

Related: [[always-council-and-fanout]], [[bound-the-verify-stage-in-councils]].
