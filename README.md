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

## License

MIT © [MEOK AI Labs](https://meok.ai)
