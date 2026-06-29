---
name: feature-catalog-mgmt-ui
description: "Next task (raised 2026-06-29) — build a UI to AUTHOR/manage platform feature-catalog entries, not just grant them"
metadata: 
  node_type: memory
  type: project
  originSessionId: e053f220-5ffc-4754-92e8-ab75e1fde111
---

Next thing to look at: a **UI to manage features on the platform** (advise_lca_platform / eTEA).

**Current state (the gap):**
- Features are data-driven rows in the **platform** DB table `lca.catalog_feature` (key like `advise_etea:feat:monte_carlo`, label, group, deprecated). The platform OWNS the catalog (SoD).
- The ONLY way to create/edit/deprecate a catalog feature today is the API: `POST /access-catalog/admin/features` + `PATCH /access-catalog/admin/features/{key}` (app_super_admin; `backend/api/app/routers/access_catalog.py`). **No authoring UI exists.** monte_carlo was added via `bootstrap`.
- The **portal** has a GRANT UI only: the application Features tab (`FeatureAdmin.tsx`) does enable-for-org + assign-to-user + a "Sync catalog" button. It cannot CREATE/edit the catalog feature itself — it just lists `application_permissions` (kind='feature') projected from the platform's `GET /access-catalog`.

**So the missing piece = a feature-catalog AUTHORING UI** (create / relabel / deprecate `catalog_feature` rows).

**Open design question to resolve first:** where it lives —
(a) platform-side admin screen (it owns the catalog), or
(b) a portal superadmin screen that calls the platform's `/access-catalog/admin/features` endpoints (cross-service, needs the catalog token + app_super_admin). After authoring, the portal still needs a **Sync catalog** to project the new row.

Remember: adding a catalog row only makes a feature grantable; the feature's functionality AND its `requires_feature("<key>")` check must already exist in platform code (e.g. monte_carlo in `routers/calculation.py`). Authoring UI ≠ building the feature.

Related: [[features-axis-monte-carlo-test-vehicle]]
