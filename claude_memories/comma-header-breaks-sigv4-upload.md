---
name: comma-header-breaks-sigv4-upload
description: On this machine a comma-separated header value (e.g. Cache-Control) makes S3 PutObject fail with SignatureDoesNotMatch — add a space after each comma
metadata: 
  node_type: memory
  type: reference
  originSessionId: d9922606-3966-4692-a6ce-a6a8718da3d2
  modified: 2026-08-07T03:26:53.634Z
---

Uploading to S3 from this machine with a **comma-separated header value and no space after
the comma** fails with `SignatureDoesNotMatch`. `Cache-Control: public,max-age=31536000,immutable`
fails; `public, max-age=31536000, immutable` succeeds. Bisected 2026-08-07 against
`neurasil-web-548045679450`:

| value | result |
|---|---|
| `no-cache`, `max-age=31536000` (single token) | ok |
| `public,immutable` | **SignatureDoesNotMatch** |
| `public,max-age=31536000,immutable` | **SignatureDoesNotMatch** |
| `public, max-age=31536000, immutable` | ok |

Something after SigV4 signing rewrites `a,b` to `a, b`, so S3 hashes a header the client
never signed. The Menlo TLS proxy is the suspect (see [[menlo-proxy-tls-python-ca-bundle]]),
but it was not proven — the same failure appears on **AWS CLI v2 and boto3 alike**, so it is
below both. GETs, list and head are unaffected: it only shows up on upload.

**How to apply:** always write a space after each comma in any header value passed to an AWS
write call. If an upload fails `SignatureDoesNotMatch` while reads work, check the headers
for commas BEFORE chasing credentials, clock skew or `AWS_REQUEST_CHECKSUM_CALCULATION` —
none of those are the cause, and the error message points at all three. A tiny-payload probe
will pass and mislead you; reproduce with the actual headers.

Related: [[neurasil-vault-mcp-server]], [[menlo-proxy-tls-python-ca-bundle]].
