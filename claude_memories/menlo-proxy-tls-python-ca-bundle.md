---
name: menlo-proxy-tls-python-ca-bundle
description: Menlo corporate proxy MITM breaks Python httpx/requests TLS (CERTIFICATE_VERIFY_FAILED); fix with SSL_CERT_FILE = Windows CA bundle
metadata: 
  node_type: memory
  type: project
  originSessionId: db8897a4-f01d-4841-bdd1-cc07574a491d
---

On this work machine (behind the Menlo corporate TLS proxy), outbound HTTPS from Python to non-allowlisted hosts (e.g. the hosted dev identity portal `api.dev.identity.advise.technology`) fails with `httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`. The proxy re-signs TLS with a corporate root that isn't in Python's `certifi` bundle. `curl` works because it uses the Windows cert store; Python (httpx/requests) does not.

**Fix:** point Python's TLS at the Windows root store, exported once to `C:/Users/chuache/aws-ca-bundle.pem` (the same `.pem` used for `AWS_CA_BUNDLE`):
- `httpx` / stdlib `ssl` / `urllib` → `SSL_CERT_FILE=C:/Users/chuache/aws-ca-bundle.pem` (httpx honors it via `trust_env`; use forward slashes to avoid `.env` backslash-escape issues).
- `requests`-based libs → `REQUESTS_CA_BUNDLE=<same path>`.
- `boto3` → `AWS_CA_BUNDLE=<same path>`; `curl` → `--ssl-no-revoke`.

**etea local platform → hosted dev portal:** the symptom was `"portal unavailable and no in-grace last-good for <email> — failing closed"` (a `PortalUnavailable` 503 = transport error, NOT a token problem). Fix = add `SSL_CERT_FILE` to the root `.env` (the VS Code "Backend Python Debugger: FastAPI" config has no `envFile`, so the Python extension injects `${workspaceFolder}/.env` = the root `.env`), then **fully restart the debug session** — env + the httpx client are cached at launch, and `--reload` does not re-read `.env`. Verified 2026-06-25: with the bundle, the portal `/users/search` call returns 200. Local only — the deployed ECS task (acct 149536453305) isn't behind Menlo, so keep this OUT of the Copilot manifest. See [[platform-portal-enforcement-egress-chain]].
