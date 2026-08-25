---
name: aws-free-tier-is-the-neurasil-design-constraint
description: neurasil is designed to stay inside AWS free limits; the account is past its 12-month tier, so only the always-free allowances count
metadata:
  node_type: memory
  type: project
---

Staying inside AWS free limits is a stated **design constraint** for neurasil, not an
afterthought — the user asked for it in the README on 2026-08-25. Weigh it when choosing storage
retention, request patterns, and anything that runs per-request.

**Why:** it is the reason to prefer a short lifecycle window over a long one, to avoid
per-request-billed APIs, and to notice monotonic growth (versioned buckets, an application trash
that nothing empties) before it becomes a bill.

**How to apply:** the account has resources dating to 2023-02, so the **12-month** free tier
expired around 2024-02 — S3's 5 GB and API Gateway's 1M calls are billed from the first
byte/request now. What still applies is the **always-free** tier: Lambda (1M requests and 400k
GB-seconds a month) and CloudFront (1 TB egress, 10M requests). Those two carry the traffic, which
is why actual spend is under $0.10/month and dominated by unrelated legacy Amplify resources. So
the constraint is mostly about *shape* — keep work in Lambda and CloudFront, keep S3 small and
its versions short-lived — rather than about pennies of storage. Do not measure this with Cost
Explorer: see [[no-cost-explorer-without-permission]].
