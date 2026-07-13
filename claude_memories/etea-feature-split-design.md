---
name: etea-feature-split-design
description: "LOCKED 4-feature split for etea (feat:{lca,tea,ai,monte_carlo}) — council-amended design + arming constraints (2026-07-13)"
metadata: 
  node_type: memory
  type: project
  originSessionId: ec95166d-3124-47d6-85b6-5552c4cfd7a7
---

Finalized 2026-07-13 (user-approved after 20-agent council: 1 affirm / 18 conditions / 1 objection — objection folded in).

**Keys:** `advise_etea:feat:{lca,tea,ai,monte_carlo}` (monte_carlo keeps existing underscore key — never rename).

**Decisions:**
- `feat:lca` = impact-assessment ONLY, **per-route split** inside `lcia_database.py`/`lcia_management.py`: datapoint lifecycle/browse (`/lcia_page`, `/lcia_databases`, `/lcia_database_sources`, `/lcia_detail_by_description_id`, datapoint create/copy) stays SEAT-ONLY substrate (TEA/AI pages render under the datapoint route tree and need it); LCIA data/results, classification, characterization, chart, calculation get the gate. Whole-mount gating of lcia_database would break TEA-only/AI-only users (council objection).
- `bulk_insert` + `bulk_collection` ARE gated under `feat:lca` (LCIA import; sole caller = FE data-submissions module; `/geographies/type` + `/units/type` ride along — split out only if a non-LCA consumer appears).
- `feat:ai` = ONE key for both `/ai` chatbot and `/rag` EF recommendations. Also gate FE ImpactTabsResults batch auto-tag button + EditSelect ai-chat/semantic modes.
- `feat:tea` = whole tea router incl `/forex/*` (master-data FX inspector deliberately requires TEA). geography_graph stays ungated.
- `monte_carlo` REQUIRES `lca` (dependency stacking: calculation mount gate + per-route MC dep). Portal has no dependency mechanism → grant-runbook rule; existing MC grantees must receive feat:lca in any backfill.

**Arming constraints (hard-won):**
- Features are data-driven `catalog_feature` rows; `requires_feature` is ALLOW no-op until row published → wire gates inert-first (on the TEA/AI branches BEFORE merge, else seated users get unmetered Bedrock).
- Portal `assertLiveFeature` blocks granting unpublished keys → grants-before-publish impossible via UI. Chosen path: **timed window** (publish → sync → grant sprint, off-hours, few users) with pre-scripted rollback = DELETE feature via admin API + forced ECS redeploy (per-worker lazy ACTIVE_FEATURE_KEYS refresh means deprecation alone leaves workers enforcing).
- **NEVER ship a feature row as a numbered migration** — apply.py's deploy gate forces arming before grants. Use the admin API.
- No reconcile drift-guard for features: a typo'd key = silent forever-ALLOW → verify each key granted=200/ungranted=403 with NON-app-root users (app-root bypasses).
- FEATURES_ENABLED verified LIVE on dev AND prod (2026-07-13, task def etea-prod-backend:9) — publishing a row is instantly load-bearing everywhere.

**Merge sequencing:** merge origin/dev INTO feat/admin-portal-integration first taking dev's `copilot/` wholesale (feat branch manifest lacks prod flag block + prod alias; merging the other way reverts prod config). TEA (57 behind) and AI (28 behind) sync with dev before gate wiring; both add `navRegistry.ts` + factory mounts → second merge must UNION.

**Progress (2026-07-13): P0–P2 LANDED** on feat/admin-portal-integration (committed, NOT pushed — deploy is from dev). Commits: 5119d411b (docs: prod-enforcement fixes + per-key lifecycle table), fde9f20e3 (PII-safe forbidden-feature telemetry), 45ca1f32a (inert feat:lca gates: 8 impact routes in lcia_database.py + 8 whole-impact router mounts; 51 substrate routes + lcia_management left ungated), c848c5f30 + fd3f4f107 (FE UserProvider loading/error/CLEAR state), 5f5698618 (FE featureKeys.ts), 9f9a77606 (backend auth/feature_keys.py single-source consts + telemetry test). Gates INERT (lca row unpublished). 2-agent independent critique = no bugs/security issues. FE nav/page gating deliberately NOT wired (user: lockout acceptable, lowest effort) → wire at arming. NEXT: P3/P4 = TEA/AI gate wiring, done DIRECTLY ON DEV after colleagues merge those branches (no branch-sync/merge-choreography needed then); then arming per §3 runbook. Deferred: conftest env-leak fixture promotion. Pre-existing broken test (NOT ours, intra-org-ACL workstream): test_auth_scope_services::test_source_relationships_classifies (tuple-vs-string assertion).

Plan doc: `claude-docs/admin-portal-integration/FEATURE-AXIS-SPLIT-PLAN.md` (platform repo). Related: [[features-axis-monte-carlo-test-vehicle]], [[etea-prod-golive]], [[feature-catalog-mgmt-ui]].
