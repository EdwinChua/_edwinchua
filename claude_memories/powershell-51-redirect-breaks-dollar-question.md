---
name: powershell-51-redirect-breaks-dollar-question
description: In Windows PowerShell 5.1, 2>&1 on a native exe sets $? to false despite exit code 0, so an if ($?) gate silently skips the next step
metadata:
  node_type: memory
  type: reference
---

In **Windows PowerShell 5.1**, redirecting a native executable's stderr with `2>&1` wraps each
stderr line in a `NativeCommandError` ErrorRecord and sets **`$?` to `$false` even when the exe
exited 0**. Any `if ($?) { ... }` gate after such a pipeline therefore skips its body on a
perfectly successful command — and reports success, because the pipeline itself did not fail.

**Why:** it is a silently-green *skip*, which is worse than a failure. Observed 2026-08-25
deploying neurasil: `aws cloudformation package ... 2>&1 | Select-Object -Last 1` followed by
`if ($?) { aws cloudformation deploy ... }` printed `exit=0` in 12 seconds and never deployed.
Nothing in the output said so — the package step's own progress line was the last thing printed,
so it read like a complete run. Same family as [[pipenv-run-swallows-exit-codes]]: a green
result from a step that never executed.

**How to apply:** do not `2>&1` a native exe in PowerShell 5.1 — the harness captures stderr
anyway. Gate on `$LASTEXITCODE -eq 0`, never on `$?`, for anything that is not a cmdlet. Better
still, run each step unconditionally in its own call. And **verify deploys from the target, not
from the exit code**: `aws lambda get-function-configuration --query LastModified` is what caught
this. A deploy that claims success in a fraction of the usual time has not run.
