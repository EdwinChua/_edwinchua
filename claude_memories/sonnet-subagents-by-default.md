---
name: sonnet-subagents-by-default
description: Use cheaper subagent models — Haiku 5.5 for trivial/mechanical tasks, Sonnet 5.x for straightforward work; reserve the session model (Opus) for synthesis or hard reasoning
metadata:
  type: feedback
  modified: 2026-10-15
---

When fanning out subagents or writing Workflow scripts, **pick the cheapest model that can
do the job** rather than letting workers inherit the session model. Reserve the stronger
model for the one stage that actually needs it — the final synthesis / judge / plan-author.

Tiers:
- **Haiku 5.5 (`model: 'haiku'`)** — trivial, mechanical tasks: file/keyword lookups,
  listing, reading a file and reporting what is in it, simple formatting/extraction,
  checking one bounded fact at one cited location.
- **Sonnet 5.x (`model: 'sonnet'`)** — straightforward but non-trivial work: repo mapping,
  Explore sweeps, verification of claims needing some judgement, routine code changes
  with a clear spec, test runs + reporting.
- **Session model (Opus, omit `model`)** — final synthesis, adversarial judging where a
  wrong verdict is expensive, design decisions, writing the actual plan or tricky code.

Stated by the user 2026-08-20 (Sonnet by default, after a 96-agent council run); extended
2026-10-15 to add Haiku 5.5 for the simplest tasks ("use cheaper subagents for
straightforward tasks, sonnet 5 and haiku 5.5 where appropriate").

**Why:** most fan-out work is retrieval and checking, not hard reasoning, and the cost of
a wide fan-out is multiplied by the agent count — the model choice on the *workers*
dominates the bill.

**How to apply:**
- `Agent` tool: set `model` per the tiers above on every spawn (forks always inherit —
  use a fresh agent type when a cheaper model is wanted).
- `Workflow` scripts: `opts.model = 'haiku' | 'sonnet'` on fan-out stages; omit it on the
  synthesis stage so it inherits. Pair with `effort: 'low'` for mechanical stages.
- When unsure between tiers, go one tier up rather than risk a wrong result being trusted.

Related: [[always-council-and-fanout]], [[bound-the-verify-stage-in-councils]].
