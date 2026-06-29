---
name: app-super-bypass-untestable-by-design
description: "app-super isn't assignable on dev/local by design → the app-root bypass (FE NoAccessOverlay + backend is_app_root) is intentional forward-compat, untestable for now; don't remove it or chase the app-root case"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2bcaab4c-f54e-4421-99b8-45620febd941
---

App-super (`app_super_admin` — the `is_app_root` tier) is **not assignable** in the dev/local identity portal by design, so the "app-root bypasses everything" path of access control can't be exercised end-to-end. The bypass code is INTENTIONAL forward-compat and must stay:
- **FE:** `frontend/lca-platform-app/app/home/_components/NoAccessOverlay.tsx` gates on `enforcement.seats && !seated && !isAppRoot && capabilities.length > 0`; the `/home` 403-catch (`ClassifyRegion`/`DatapointsTable` → `PermissionDenied` overlay) also yields no banner for app-root (their data loads).
- **Backend:** `is_app_root` (super_admin OR app_super_admin) bypasses seat/feature/capability; `is_data_root` (app_super_admin only) bypasses scope+share.

The /home no-access overlay was validated on dev/local for the other four cases (no-seat/no-role, seated/no-role, no-seat+role(org-admin), seated+role); only the app-root case ("case 5") is unverifiable.

**Why:** if app-super ever becomes assignable, those users must bypass every axis (including the no-access banner). User confirmed 2026-06-26: "intended by design… keep existing code to cater for that possibility."
**How to apply:** don't flag `!isAppRoot` / the backend `is_app_root` bypass as dead or untested code and don't "simplify" it away; don't spend time trying to test the app-root case until app-super assignment exists. When it does, verify the no-access banner does NOT show for an app-root user and that seat/feature/capability/scope are all bypassed. Related: [[features-axis-monte-carlo-test-vehicle]].
