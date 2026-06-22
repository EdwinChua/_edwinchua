---
name: copilot-secret-must-use-secret-init
description: "AWS Copilot service secrets MUST be created via `copilot secret init` (tags them), not raw aws ssm put-parameter, or the task can't start"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ba6d4fe5-89ca-4206-86d5-f0adf2384f5a
---

When adding an SSM SecureString secret for an AWS Copilot service (the `secrets:` block in a
service manifest), create it with **`copilot secret init --app <app> --name <NAME> --values <env>=<value>`**,
NOT raw `aws ssm put-parameter`.

WHY: Copilot generates the ECS **execution role's** SecretsPolicy granting `ssm:GetParameters` on
`parameter/*` but **conditioned** on the parameter carrying the tags
`copilot-application=<app>` AND `copilot-environment=<env>`. A param created with plain
`aws ssm put-parameter` is **untagged**, so the execution role is denied → the task fails at launch
with `ResourceInitializationError: unable to retrieve secrets from ssm: AccessDeniedException ...
ssm:GetParameters`, the deploy circuit-breaks and rolls back. The container itself starts fine if it
ever launches — this is a *task-placement* failure, not an app crash (check ECS service EVENTS, not
just container logs).

The KMS key is NOT the issue — Copilot dev secrets use `alias/aws/ssm` (the default), and the
execution role can decrypt those via SSM; the policy's explicit `kms:Decrypt` on the env CMK +
tagged-key condition is belt-and-suspenders. So the fix is purely the **tags**:
`copilot secret init --overwrite` re-tags an existing param (it keeps the existing KeyId, which is
fine). Verify with `aws ssm list-tags-for-resource --resource-type Parameter --resource-id <name>`.

Hit during the etea dev domain-rename deploy (2026-06-18): AUTH_COGNITO_SECRET was put via
`aws ssm put-parameter` → frontend deploy failed the circuit breaker → fixed via `copilot secret init
--overwrite`. Relates to [[acm-validation-deterministic-copilot-tls]].
