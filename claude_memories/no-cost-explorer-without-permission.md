---
name: no-cost-explorer-without-permission
description: Never call AWS Cost Explorer (get-cost-and-usage etc.) without explicit permission — each request bills $0.01
metadata:
  node_type: memory
  type: feedback
---

Do not run AWS Cost Explorer queries — `aws ce get-cost-and-usage`, `get-cost-forecast`, or
anything else under the `ce` API — unless the user has explicitly asked for it in that turn.
Ask first.

**Why:** every Cost Explorer request bills **$0.01**, which sounds like nothing until you notice
the scale it sits against. The user set this on 2026-08-25 during neurasil work, after I ran four
of them while gathering numbers to write a free-tier section into a README. That was ~$0.04 of
introspection about an app whose entire monthly AWS bill is under $0.10 — the measuring cost more
than the thing measured. Their words: "these calls cost 1ct apiece, and while not significant I
would like you to stop doing that unless given explicit permission."

**How to apply:** to answer a cost question, reach first for what is free — `s3api
list-object-versions` and `list-objects-v2` for storage, `lambda list-functions` for code size,
CloudWatch metrics, the published price list, or simply arithmetic over object counts you already
have. If none of those can answer it and Cost Explorer genuinely can, say so and ask before
calling. The same caution applies to any other API that bills per request rather than per
resource. Relates to [[aws-free-tier-is-the-neurasil-design-constraint]].
