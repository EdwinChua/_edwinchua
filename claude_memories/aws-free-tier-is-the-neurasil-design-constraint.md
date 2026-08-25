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

**Why:** it decides architecture — SSE-S3 over a KMS CMK, DuckDB in the Lambda over a
database, no NAT gateway or ALB. But the mechanism is a STEP CHANGE, not accumulation: below a
small monthly total AWS does not charge the card at all (the balance carries forward), so
fractions of a cent are invisible however many there are. 61 MB of dead S3 versions never
appeared on a bill. What appears is one always-on service, and adding it costs its own price
PLUS every fraction that was previously below the line. The user observed this on 2026-08-25.

**How to apply:** the account has resources dating to 2023-02, so the **12-month** free tier
expired around 2024-02 — S3's 5 GB and API Gateway's 1M calls are billed from the first
byte/request now. What still applies is the **always-free** tier: Lambda (1M requests and 400k
GB-seconds a month) and CloudFront (1 TB egress, 10M requests). Those two carry the traffic, which
is why actual spend is under $0.10/month and dominated by unrelated legacy Amplify resources. So
the constraint is mostly about *shape*: keep work in Lambda and CloudFront, and refuse anything
that bills for EXISTING rather than for being used. Bounding unbounded growth (S3 versions, an
app trash nothing empties) is worth doing as hygiene, but it is not cost control. Do not measure this with Cost
Explorer: see [[no-cost-explorer-without-permission]].
