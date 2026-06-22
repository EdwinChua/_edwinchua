---
name: acm-validation-deterministic-copilot-tls
description: "ACM DNS-validation records are deterministic per (domain, account) across regions; Copilot terminate_tls forces a 3-round deploy"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ba6d4fe5-89ca-4206-86d5-f0adf2384f5a
---

Two hard-won infra facts from the etea dev domain rename (`*.etea.leaf.advise.technology` → `*.etea.advise.technology`):

**1. ACM DNS-validation records are deterministic per (domain + account), even across regions.**
Requesting a second ACM cert (e.g. ap-southeast-1 for an ALB) covering the SAME SANs as an
existing cert (e.g. us-east-1 superset for CloudFront) produces **byte-identical** validation
CNAME name AND value. So the second cert validates off the records ALREADY in the Route 53 zone
— no new DNS, no collision, both certs share one validation record set and both auto-renew off it.
Verified empirically (proven identical, then the 6-SAN regional cert went ISSUED in ~30s off
existing records). The earlier "per-request endpoint quirk" (cert#1 vs superset getting different
pact values) did NOT recur — treat divergence as the exception, not the rule. Validation records
for a sub-zone live in the MOST-SPECIFIC hosted zone (e.g. `*.dev.etea.leaf...` records are in the
`dev.etea.leaf.advise.technology` zone Z09342231F0IFS8KB82A2, not the parent `etea.leaf` zone).

**2. AWS Copilot: switching env `cdn: true` → BYO `cdn.certificate` is NOT a plain cert swap.**
It forces a TLS-termination choice. `cdn.terminate_tls: true` (CloudFront terminates, HTTP to ALB)
requires `redirect_to_https: false` on EVERY CDN-fronted service, because Copilot's ALB HTTP→HTTPS
redirect (`HTTPListenerRuleWithDomain`) is a **blanket 301 with no X-Forwarded-Proto condition**,
and `copilot env deploy` validates the **LIVE deployed ALB rules** (DescribeRule), not local
manifests — so you must svc-deploy redirect:false FIRST, making it a fragile 3-round deploy.
The clean alternative: set env `http.public.certificates` to a regional BYO ALB cert + keep
`terminate_tls` OFF → TLS pass-through (CloudFront→ALB over HTTPS), identical to prior `cdn: true`,
zero service-manifest changes, single-pass deploy. Chosen for etea dev (Option B). Source-verified
by a 14-agent council reading copilot-cli source (`https-listener.yml`, `cdn-resources.yml`, `env.go`).
See `claude-docs/domain-rename-etea-advise.md` in the advise_lca_platform repo. Relates to
[[always-council-and-fanout]].
