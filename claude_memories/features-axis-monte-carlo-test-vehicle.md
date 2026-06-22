---
name: features-axis-monte-carlo-test-vehicle
description: monte_carlo is the only feature in the dev features catalog and is the deliberate test vehicle for the FEATURES axis — grant/revoke it at org+user level on the identity portal to flip the axis without a code change
metadata: 
  node_type: memory
  type: project
  originSessionId: 656a8dd1-af88-4c5a-a64f-765b6387ae5a
---

`FEATURES_ENABLED` is ON in dev (platform manifest, 2026-06-19). The Phase 2 feature
catalog seeds only **`monte_carlo`**, so it is the single lever for exercising the
FEATURES axis end-to-end on dev.

To toggle the axis WITHOUT a code change, grant or revoke `monte_carlo` for the
**advise_etea** application on the identity portal at BOTH levels:
- org level (`organization_features`)
- user level (`user_features`)

Effective feature = org ∩ user ∩ catalog. With no grant, non-app-root users get
**403 on all Monte Carlo routes** and the FE greys `MonteCarloControlsPanel`.

The user explicitly wants to flip this on/off repeatedly to test the axis — so the
`monte_carlo` portal grant is **NOT** a one-time go-live step, it's the toggle. Treat
"grant monte_carlo" as a test action, not a deploy blocker. Related: the broader
enforcement preconditions in [[platform-portal-enforcement-egress-chain]].
