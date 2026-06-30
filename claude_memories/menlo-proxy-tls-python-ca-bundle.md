---
name: menlo-proxy-tls-python-ca-bundle
description: Menlo corporate proxy MITM breaks Python httpx/requests/AWS-CLI TLS (CERTIFICATE_VERIFY_FAILED); PERMANENTLY FIXED 2026-06-30 via persistent user env vars -> C:\Users\chuache\.certs\corp-ca-bundle.pem
metadata: 
  node_type: memory
  type: project
  originSessionId: db8897a4-f01d-4841-bdd1-cc07574a491d
---

On this work machine (behind the Menlo corporate TLS proxy, an installed agent so it bites at home AND in the office), outbound HTTPS from Python-based CLIs/libs fails with `[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`. The proxy re-signs TLS with a corporate root (`Menlo Security Root CA` / `Menlo Security Root H1`) that lives in the **Windows trust store** but NOT in Python's bundled `certifi`. Browsers, .NET, and `curl`/git on the schannel backend work (Windows store); AWS CLI v2, `httpx`, `requests`, `boto3` do not (their own certifi bundle). AWS CLI v2 is a frozen build — you can't `pip install python-certifi-win32` into it, so the bundle-env-var route is the only universal fix.

**PERMANENT FIX (installed 2026-06-30, this session):**
- Canonical bundle: `C:\Users\chuache\.certs\corp-ca-bundle.pem` = full export of the Windows trust store (LocalMachine+CurrentUser Root/CA, ~219 certs), so it contains both public roots and the Menlo roots. Self-contained — works for everything.
- Regenerate it (if a root ever rotates and TLS breaks again): `powershell -ExecutionPolicy Bypass -File "$HOME\.certs\Update-CaBundle.ps1"`. Chose a static bundle, NOT a scheduled auto-refresh task.
- Persistent **User**-scope env vars, all pointing at that bundle (set via `[Environment]::SetEnvironmentVariable(...,'User')`): `AWS_CA_BUNDLE`, `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, `CURL_CA_BUNDLE`, `NODE_EXTRA_CA_CERTS`, `PIP_CERT`. New terminals inherit them; already-open shells/VS Code need a restart to pick them up.
- git: `git config --global http.sslBackend schannel` — uses the Windows store directly, so git stays fresh with no bundle dependency.
- Verified: live `ssl.create_default_context(cafile=bundle)` TLS handshakes to `sts`/`cognito-idp.ap-southeast-1` both succeed (TLSv1.3); AWS CLI `sts get-caller-identity` + cognito-idp calls work.

**etea local platform -> hosted dev portal:** old symptom was `"portal unavailable and no in-grace last-good for <email> — failing closed"` (a `PortalUnavailable` 503 = transport/TLS error, NOT a token problem). Previously needed `SSL_CERT_FILE` added to the root `.env` (the VS Code "Backend Python Debugger: FastAPI" config has no `envFile`, so the Python extension injects `${workspaceFolder}/.env`) + a full debug-session restart (env + httpx client cached at launch; `--reload` doesn't re-read `.env`). Now that `SSL_CERT_FILE` is a persistent user env var, a freshly-relaunched VS Code should inherit it automatically and the manual `.env` line is likely redundant — but keep it as a fallback if the debugger ever doesn't see the user env. Local only — the deployed ECS task (acct 149536453305) isn't behind Menlo, so keep this OUT of the Copilot manifest. See [[platform-portal-enforcement-egress-chain]].
