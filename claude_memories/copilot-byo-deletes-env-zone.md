---
name: copilot-byo-deletes-env-zone
description: Copilot cdn:true->BYO env deploy deletes the entire env-managed Route53 subzone (not just records); re-verify zone IDs before time-critical writes
metadata: 
  node_type: memory
  type: project
  originSessionId: 5db32173-ff2c-45d5-9f32-bb84b09938d2
---

Switching an AWS Copilot environment from managed `cdn: true` to a BYO `cdn.certificate` (+
`http.public.certificates`) does NOT just delete the Copilot-managed alias **A-records** — for an
app-domain env it **DELETES THE ENTIRE env-managed delegated hosted zone** AND its NS delegation
in the parent zone. Confirmed live on the etea **prod** rename (2026-06-19): the prod `env deploy`
deleted the `prod.etea.leaf.advise.technology` zone (`Z0960213…`) + the parent `etea.leaf`
delegation, so the external pact-api `api.prod.etea.leaf` went NXDOMAIN with **no zone to recreate
the record in** — the documented zone ID returned `NoSuchHostedZone`.

**Recovery that worked:** once the delegated subzone is gone, the **parent zone becomes
authoritative** for the whole subtree — so add the kept host's A-ALIAS (→ the same CloudFront,
alias HZ `Z2FDTNDATAQYW2`, EvaluateTargetHealth false) **directly in the parent zone**
(`etea.leaf` = `Z05355601…`), plus re-add its ACM DNS-validation CNAME there for renewal.

**Hard lessons:** (1) **Re-resolve EVERY Route53 zone ID with `list-hosted-zones` immediately
before a time-critical write** — never trust a doc/earlier-read ID across an `env deploy`; a stale
ID (`NoSuchHostedZone`) failed the first restore and lengthened a live external outage. (2) For a
BYO cutover, plan to serve ALL kept leaf hosts from the PARENT zone, not a per-env subzone. (3) The
external gap = env-deploy duration + DNS propagation + negative-cache clear — budget generously.
(4) Verify a restored host END-TO-END through CloudFront, not just DNS: pact-api ALB rules only
forward `/pact/*` to the service; other paths (`/`, `/health`) hit an empty default TG → ALB 503
by design (pre-existing, not a regression). Builds on [[acm-validation-deterministic-copilot-tls]].
