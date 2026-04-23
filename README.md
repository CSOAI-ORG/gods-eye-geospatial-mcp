# Gods Eye — Sovereign Geospatial Awareness MCP

**Sovereign geospatial awareness for AI agents**, wrapping open, non-US-dependent APIs behind the MEOK Care Membrane ethics gate.

By [MEOK AI Labs](https://meok.ai).

## What it does

- Wraps **ESA Copernicus Sentinel-1/2/3/5p** (SAR, multispectral, ocean/land/thermal, atmospheric)
- Wraps **OpenStreetMap** + **Overture Maps** + **Ordnance Survey UK** + **INSPIRE EU** + **DEFRA UK**
- Every query passes through the **Care Membrane** — a pre-inference ethics gate that blocks kinetic-targeting, personal surveillance, and other high-risk patterns
- Provides **sovereignty checks** — flag US supply-chain dependencies in an existing stack and suggest alternatives

## Why sovereign?

- **UK HMG / MoD procurement** frequently requires minimising US supply-chain exposure (ITAR, CLOUD Act, EO 14117)
- Copernicus is **EU-accessible, free, all-weather SAR + 13-band multispectral** — you don't need Maxar or Planet to answer 80% of public-sector questions
- Care Membrane provides **governance-auditable decisions** for any defence-adjacent buyer
- Designed to complement our `dora-compliance-mcp`, `nis2-compliance-mcp`, `cra-compliance-mcp`

## What it is NOT

- **Not for kinetic targeting.** Care Membrane blocks patterns like "strike package", "find-fix-finish", "target elimination", "bounty", "lethal" and similar.
- **Not a replacement for Maxar/Planet** where sub-metre commercial imagery is genuinely required.
- **Not a face-recognition or individual-tracking tool.** Any such query is blocked.

## Install

```bash
pip install gods-eye-geospatial-mcp
```

## Claude Desktop

```json
{
  "mcpServers": {
    "gods-eye": { "command": "gods-eye-geospatial-mcp" }
  }
}
```

## Use cases

- AI agent situational awareness (location → weather, terrain, infrastructure)
- Coastline / maritime domain awareness (aggregate shipping, non-individual)
- Agriculture / yield estimation (NDVI / NDWI time series)
- Infrastructure change detection (before / after)
- Disaster response (flood / wildfire / earthquake overlays)
- Environmental compliance evidence (CSRD E3 water, E4 biodiversity)

## Tiers

- **Free** — 10 situational queries/day, sovereignty checks
- **Pro £199/mo** — unlimited + auto-fetches tiles + caches + signed attestations
- **Enterprise £1,499/mo** — multi-tenant, on-prem deployment option, custom Care Membrane policies
- **48h audit £5,000** — sovereignty review of your entire geospatial stack

## Care Membrane

The Care Membrane is MEOK's pre-inference ethics gate. Every query is evaluated for high-risk patterns before an external API is called. Policy is visible via the `care_membrane_policy` tool and reviewable by auditors.

## License

MIT — MEOK AI Labs, 2026.
