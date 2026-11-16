<!-- mcp-name: io.github.CSOAI-ORG/gods-eye-geospatial-mcp -->
[![MCP Scorecard: 78/100](https://img.shields.io/badge/proofof.ai-78%2F100-5b21b6)](https://proofof.ai/scorecard/gods-eye-geospatial-mcp.html)

# Gods Eye Geospatial MCP

[![MEOK AI Labs](https://img.shields.io/badge/MEOK-AI%20Labs-667eea)](https://meok.ai)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Install-3775a9)](https://pypi.org/project/gods_eye_geospatial_mcp/)

> Gods Eye — sovereign geospatial awareness MCP

Gods Eye — sovereign geospatial awareness MCP. Wraps open, non-US-dependent APIs (ESA Copernicus Sentinel-1/2/3/5p, OpenStreetMap, Overture, Ordnance Survey UK, INSPIRE EU, DEFRA) behind the MEOK Care Membrane ethics gate. For AI-agent situational awareness, environmental compliance, disaster response. Not for kinetic operations. By MEOK AI Labs.

---

## 🚀 Quick Start

```bash
# Install via pip
pip install gods_eye_geospatial_mcp

# Or install via Smithery
npx -y @smithery/cli@latest install gods-eye-geospatial-mcp --client claude
```

## ✨ Features

- MCP protocol compliant
- Easy installation
- Well-documented API
- Production-ready
- Active maintenance

## 📖 Documentation

- [Full Documentation](https://docs.meok.ai/gods-eye-geospatial-mcp)
- [API Reference](https://api.meok.ai)
- [EU AI Act Compliance Guide](https://councilof.ai/compliance)

## 🛡️ Compliance

This MCP server is built with **EU AI Act compliance** built-in:

- ✅ Article 9 — Risk Management System
- ✅ Article 13 — Transparency & Instructions for Use
- ✅ Article 15 — Bias Detection & Testing
- ✅ Article 26 — FRIA Support (where applicable)
- ✅ Article 50 — AI Content Watermarking (where applicable)

Need help getting compliant? **[Book a free 15-min diagnostic →](https://cal.com/csoai/august-audit)**

## How MEOK charges

MEOK has no subscriptions and no tiers. You pay per job, and only when the agreed artifact has been delivered to you. There is no public price list. See <https://meok.ai/pricing>.

This repository's source is MIT-licensed and free to self-host.

## 🤝 Part of the MEOK Ecosystem

This server is part of the **[MEOK AI Labs](https://meok.ai)** ecosystem — 300+ MCP servers for sovereign AI governance.

| Domain | Purpose |
|--------|---------|
| [councilof.ai](https://councilof.ai) | EU AI Act compliance marketplace |
| [safetyof.ai](https://safetyof.ai) | AI safety & monitoring |
| [meok.ai](https://meok.ai) | Sovereign AI platform |
| [cobolbridge.ai](https://cobolbridge.ai) | Legacy modernization |

## 📜 License

MIT © [CSOAI-ORG](https://github.com/CSOAI-ORG)

---

<p align="center">
  <sub>Built with 💜 by <a href="https://meok.ai">MEOK AI Labs</a> · UK Companies House 16939677</sub>
</p>



## Configuration

Add to your `claude_desktop_config.json` (Claude Desktop) or your MCP client config:

```json
{
  "mcpServers": {
    "gods-eye-geospatial-mcp": {
      "command": "uvx",
      "args": ["gods-eye-geospatial-mcp"]
    }
  }
}
```

Or: `pip install gods-eye-geospatial-mcp` then run the `gods-eye-geospatial-mcp` command (stdio transport).

## Examples

Once configured, ask your assistant, for example:
- "Use `list_data_sources` to …"
- "Use `situational_query` to …"
- "Use `check_data_provenance` to …"
