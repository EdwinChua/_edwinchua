---
name: mcp-response-vs-schema-change-cost
description: "On a live MCP connector, response-shape changes are free but tool descriptions and parameters are part of tools/list and cost a client refresh"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e1d53ee6-1b9e-42f9-96ad-2d178ba0cc90
  modified: 2026-08-06T08:06:45.351Z
---

Changing what an MCP tool RETURNS is invisible to a connected claude.ai client; changing
its **description or its parameters is not**. FastMCP generates `outputSchema` as
`{"type": "object", "additionalProperties": true}` for a `-> dict` tool, so new response
fields validate against the schema the client already cached. But `inputSchema` is
`{"additionalProperties": false, ...}` with an explicit `required` array, and the tool
DESCRIPTION is a `tools/list` field too — so editing a description, adding an optional
parameter, or making a required parameter optional all change `tools/list` and cost the
user a connector refresh/re-approval.

**Why:** I advised batching every change into one deploy because "any of this changes the
tool schema." That was wrong, and it inverts the risk ordering: a response-only change
ships to a live connector for free, while the deploy that touches a shared engine module
is the one that can break a second consumer (the web app). Sequence by *which artifacts a
change touches*, not by the tools/list seam.

**How to apply:** to add a capability to a live connector without a refresh — enrich the
response and teach it through a data channel the model already reads (in neurasil that is
`describe_vault`'s `guidance` dict), leaving the tool description byte-identical. Batch
genuine schema changes into one deliberate deploy. Verify before deploying by
introspecting the real registration rather than reasoning about it:

```python
mcp = FastMCP("probe"); tools.register(mcp)
for t in await mcp._list_tools():
    print(t.name, t.description, t.parameters, t.output_schema)
```

Assert the description string and the `required` array are unchanged. A comment-only diff
in the adapter is not sufficient proof — check the generated schema.

Related: [[neurasil-vault-mcp-server]], [[critique-code-mods-two-agents]].
