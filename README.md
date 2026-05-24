<div align="center">

# Gods Eye Geospatial MCP

**MCP server for gods eye geospatial mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-gods-eye-geospatial-mcp)](https://pypi.org/project/meok-gods-eye-geospatial-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Gods Eye Geospatial MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `list_data_sources` | List the open-licence geospatial data sources wrapped by Gods Eye. |
| `situational_query` | Plan a geospatial situational-awareness query. Pass natural-language 'query' plu |
| `check_data_provenance` | Given a geospatial stack description, flag proprietary / closed-licence dependen |
| `care_membrane_policy` | Return the Care Membrane policy governing what Gods Eye will and will not do. |
| `sign_data_provenance_attestation` | Generate a cryptographically signed data-provenance attestation for your geospat |

## Installation

```bash
pip install meok-gods-eye-geospatial-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gods-eye-geospatial-mcp": {
      "command": "python",
      "args": ["-m", "meok_gods_eye_geospatial_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

> **If this tool helps your compliance workflow, please [star this repo](https://github.com/CSOAI-ORG/gods-eye-geospatial-mcp/stargazers)** — it helps other teams find it.

## Wire it up — full stack

Pair this with the MEOK chain that turns one agent action into ONE signed compliance event:

1. **bft-progress-council-mcp** — anti-loop guardrail
2. **agent-token-budget-mcp** — hard spend cap
3. **agent-prompt-injection-firewall-mcp** — OWASP LLM01 scan
4. **agent-audit-logger-mcp** — hash-chained evidence
5. **a2a-governance-bridge-mcp** — fold N attestations → 1 signed event
6. **agent-incident-relay-mcp** — broadcast incidents to 5 regimes simultaneously

See [meok.ai/mcp-stack](https://meok.ai/mcp-stack) for the architecture and [meok.ai/mcp-stack/demo](https://meok.ai/mcp-stack/demo) for the live in-browser demo.

## License

MIT © [MEOK AI Labs](https://meok.ai)

<!-- meok-moat-footer-v1 -->
---

## Pairs with MEOK Governance Suite

Build something that touches users? You need compliance. MEOK ships 38 governance MCPs that drop in alongside this tool — EU AI Act, DORA, NIS2, CRA, GDPR, ISO 42001, FDA SaMD, MDR, Basel, MiFID II, MiCA, COPPA, and more.

```bash
# One-shot install of the governance pack
npx meok-setup --pack governance
```

Free tier: 10 calls/day per MCP. Pro tier (£79/mo): unlimited + cryptographically signed compliance attestations your auditor verifies independently.

→ Full catalogue: [councilof.ai/catalogue](https://councilof.ai/catalogue)
→ MEOK AI Labs: [meok.ai](https://meok.ai)

