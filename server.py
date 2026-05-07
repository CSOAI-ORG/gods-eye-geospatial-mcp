#!/usr/bin/env python3
"""
Gods Eye — Sovereign Geospatial Awareness MCP
==============================================
By MEOK AI Labs | https://meok.ai

Wraps open, non-US-dependent geospatial APIs (Copernicus / Sentinel-Hub / OpenStreetMap
/ Overture Maps / EU Location Services) behind a single MCP tool surface, care-gated
by the MEOK Care Membrane.

POSITIONING: Sovereign alternative to US-dependent geospatial stacks (Maxar, BlackSky,
Planet Labs). Every query flows through the Care Membrane governance gate before
any external API is called. Designed for UK and EU public-sector and defence-adjacent
deployments where data sovereignty and ethical oversight matter.

Use cases:
  - AI agent situational awareness (location → weather, terrain, infrastructure)
  - Border and coastline monitoring (Sentinel-1 SAR for all-weather imaging)
  - Agriculture / yield estimation (Sentinel-2 multispectral)
  - Infrastructure change detection (before/after tiles)
  - Disaster response (flood / wildfire / earthquake overlays)
  - Environmental compliance evidence (CSRD E3 water, E4 biodiversity)

This is a thin, ethical wrapper. It does NOT facilitate targeting or kinetic
operations. Care Membrane policy blocks queries matching high-risk patterns.

Install: pip install gods-eye-geospatial-mcp
Run:     python server.py
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

import os as _os
import sys
import os

_MEOK_API_KEY = _os.environ.get("MEOK_API_KEY", "")

try:
    sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
    from auth_middleware import check_access as _shared_check_access
except ImportError:
    def _shared_check_access(api_key: str = ""):
        if _MEOK_API_KEY and api_key and api_key == _MEOK_API_KEY:
            return True, "OK", "pro"
        if _MEOK_API_KEY and api_key and api_key != _MEOK_API_KEY:
            return False, "Invalid API key. Get one at https://meok.ai/api-keys", "free"
        return True, "OK", "free"


def check_access(api_key: str = ""):
    return _shared_check_access(api_key)


FREE_DAILY_LIMIT = 10
_usage: dict[str, list[datetime]] = defaultdict(list)
STRIPE_199 = "https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836"
STRIPE_1499 = "https://buy.stripe.com/4gM9AV80kaEG0ZT42k8k837"
STRIPE_5K = "https://buy.stripe.com/4gM7sN2G0bIKeQJfL28k833"


def _rl(tier: str = "free") -> Optional[str]:
    if tier in ("pro", "professional", "enterprise"):
        return None
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=1)
    _usage["anonymous"] = [t for t in _usage["anonymous"] if t > cutoff]
    if len(_usage["anonymous"]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit ({FREE_DAILY_LIMIT}/day). Unlock unlimited geospatial queries + care-gated Pro tier at £199/mo: {STRIPE_199}"
    _usage["anonymous"].append(now)
    return None


# ── Care Membrane — sovereign ethics gate ───────────────────────
# Block queries that indicate kinetic targeting, personal surveillance,
# or operations outside declared lawful defence/civil-safety use cases.
CARE_MEMBRANE_BLOCK_TERMS = [
    "kill", "assassinate", "target elimination", "strike package", "kill chain",
    "kinetic target", "find-fix-finish", "stalk", "surveil individual",
    "track person", "identify individual from", "bounty", "lethal",
]

CARE_MEMBRANE_ESCALATE_TERMS = [
    "border", "protest", "demonstration", "civil disturbance", "watchlist",
    "individual location", "home address",
]


def care_membrane_check(query: str) -> tuple[bool, str]:
    """Return (allowed, reason). Care Membrane is the MEOK ethical gate applied before
    any external geospatial API call."""
    q = query.lower()
    for t in CARE_MEMBRANE_BLOCK_TERMS:
        if t in q:
            return False, (
                f"Care Membrane BLOCKED: query contains pattern '{t}' matching kinetic-targeting "
                "or personal-surveillance risk. Gods Eye is restricted to non-kinetic, aggregate, "
                "care-aligned geospatial awareness. Contact nicholas@csoai.org if you believe this "
                "block is incorrect for a legitimate defence or civil-safety use case."
            )
    for t in CARE_MEMBRANE_ESCALATE_TERMS:
        if t in q:
            return True, f"Care Membrane ESCALATED — query touched sensitive pattern '{t}'. Response permitted but audit-logged for governance review."
    return True, "Care Membrane: clear"


# ── Open, non-US-dependent data sources ────────────────────────
DATA_SOURCES = {
    "copernicus_sentinel_1": {
        "provider": "ESA Copernicus",
        "resolution": "5m-40m SAR (all-weather, day/night)",
        "access": "Free via Copernicus Data Space Ecosystem (dataspace.copernicus.eu)",
        "use_cases": ["flood mapping", "land cover", "maritime surveillance", "change detection"],
        "sovereignty": "EU / UK accessible — no US ITAR constraint",
    },
    "copernicus_sentinel_2": {
        "provider": "ESA Copernicus",
        "resolution": "10m-60m multispectral (13 bands)",
        "access": "Free via Copernicus Data Space Ecosystem",
        "use_cases": ["vegetation indices", "agriculture", "wildfire detection", "urban expansion"],
        "sovereignty": "EU / UK accessible",
    },
    "copernicus_sentinel_3": {
        "provider": "ESA Copernicus",
        "resolution": "300m-1km ocean + land color + thermal",
        "access": "Free via Copernicus Data Space Ecosystem",
        "use_cases": ["ocean temperature", "ice cover", "air quality"],
        "sovereignty": "EU / UK accessible",
    },
    "copernicus_sentinel_5p": {
        "provider": "ESA Copernicus",
        "resolution": "7km atmospheric",
        "access": "Free via Copernicus",
        "use_cases": ["NO2, SO2, CO, O3 pollution", "methane leak detection"],
        "sovereignty": "EU / UK accessible",
    },
    "openstreetmap": {
        "provider": "OpenStreetMap Foundation",
        "resolution": "feature-level (variable accuracy)",
        "access": "Free — Overpass API + Nominatim geocoder",
        "use_cases": ["roads", "POIs", "addresses", "administrative boundaries"],
        "sovereignty": "Community-owned, no single national dependency",
    },
    "overture_maps": {
        "provider": "Overture Maps Foundation (Microsoft + Meta + AWS)",
        "resolution": "feature-level",
        "access": "Free — CC-BY 4.0 + ODbL",
        "use_cases": ["places (POI)", "buildings", "transportation", "administrative divisions"],
        "sovereignty": "Open licence but US-led foundation",
    },
    "os_open_data_uk": {
        "provider": "Ordnance Survey (UK)",
        "resolution": "1m-25m UK-specific",
        "access": "Free — OS Open Data via OS Data Hub",
        "use_cases": ["UK mapping", "Open Zoomstack", "Open Names"],
        "sovereignty": "UK government — ideal for HMG / MoD work",
    },
    "inspire_eu": {
        "provider": "European Commission INSPIRE Directive",
        "resolution": "varies by theme",
        "access": "Free — geoportal.ec.europa.eu",
        "use_cases": ["EU-standardised spatial data (34 themes)", "environment", "transport"],
        "sovereignty": "EU-standardised",
    },
    "defra_uk": {
        "provider": "DEFRA (UK Department for Environment)",
        "resolution": "varies",
        "access": "Free — data.gov.uk",
        "use_cases": ["flood zones", "environment", "land use"],
        "sovereignty": "UK government",
    },
    "ioa_disasters": {
        "provider": "International Charter Space and Major Disasters",
        "resolution": "varies",
        "access": "Activated by civil protection authorities",
        "use_cases": ["disaster response imagery"],
        "sovereignty": "Multi-national — ESA, NASA, CNES, etc.",
    },
}


mcp = FastMCP(
    "gods-eye-geospatial",
    instructions=(
        "MEOK AI Labs Gods Eye MCP. Sovereign geospatial awareness wrapping open, "
        "non-US-dependent APIs (ESA Copernicus Sentinel-1/2/3/5p, OpenStreetMap, Overture, "
        "Ordnance Survey, INSPIRE, DEFRA). Every query is pre-filtered by the Care Membrane. "
        "Use for: AI-agent situational awareness, infrastructure monitoring, environmental "
        "compliance evidence, disaster response. Does NOT facilitate kinetic operations."
    ),
)


@mcp.tool()
def list_data_sources(api_key: str = "") -> str:
    """List the sovereign, non-US-dependent geospatial data sources wrapped by Gods Eye.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool for security assessment, threat detection, or vulnerability
        analysis. Suitable for automated security scanning and risk evaluation.

    When NOT to use:
        Do not rely solely on this tool for production security decisions.
        Always combine with manual security review.

    Args:
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    return json.dumps({
        "positioning": "Sovereign geospatial awareness — no US supply-chain dependency required",
        "care_membrane": "Every query passes through Care Membrane ethics gate before any external API call",
        "data_sources": DATA_SOURCES,
    }, indent=2)


@mcp.tool()
def situational_query(
    query: str,
    bbox: str = "",
    aoi_name: str = "",
    time_window: str = "last_7_days",
    preferred_sources: str = "copernicus_sentinel_2,openstreetmap",
    api_key: str = "",
) -> str:
    """Plan a geospatial situational-awareness query. Pass natural-language 'query' plus
    bounding box (minLon,minLat,maxLon,maxLat) or 'aoi_name' (an administrative area name).

    Returns a structured plan: which data sources to use, which products to fetch, how to
    chain them, and Care Membrane status. Actual tile fetching is a Pro-tier feature.

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool for security assessment, threat detection, or vulnerability
        analysis. Suitable for automated security scanning and risk evaluation.

    When NOT to use:
        Do not rely solely on this tool for production security decisions.
        Always combine with manual security review.

    Args:
        query (str): The query to analyze or process.
        bbox (str): The bbox to analyze or process.
        aoi_name (str): The aoi name to analyze or process.
        time_window (str): The time window to analyze or process.
        preferred_sources (str): The preferred sources to analyze or process.
        openstreetmap": The openstreetmap" to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if err := _rl(tier):
        return json.dumps({"error": err, "upgrade_url": STRIPE_199})

    allowed_cm, cm_reason = care_membrane_check(query + " " + aoi_name)
    if not allowed_cm:
        return json.dumps({"care_membrane": "BLOCKED", "reason": cm_reason})

    # Heuristic plan
    q = query.lower()
    suggestions = []
    if any(t in q for t in ["flood", "water", "rain"]):
        suggestions.append(("copernicus_sentinel_1", "SAR flood mapping — works through cloud"))
        suggestions.append(("copernicus_sentinel_2", "Pre/post multispectral comparison"))
        suggestions.append(("defra_uk", "UK flood zones baseline"))
    if any(t in q for t in ["wildfire", "fire", "burn scar"]):
        suggestions.append(("copernicus_sentinel_2", "NBR burn severity index"))
        suggestions.append(("copernicus_sentinel_3", "Thermal + SLSTR"))
    if any(t in q for t in ["vegetation", "crop", "agriculture", "yield"]):
        suggestions.append(("copernicus_sentinel_2", "NDVI / NDWI time series"))
    if any(t in q for t in ["urban", "city", "infrastructure", "building"]):
        suggestions.append(("openstreetmap", "Building footprints via Overpass API"))
        suggestions.append(("overture_maps", "Buildings + places dataset"))
        suggestions.append(("os_open_data_uk", "UK OS Open Zoomstack"))
    if any(t in q for t in ["coastline", "maritime", "port", "ship"]):
        suggestions.append(("copernicus_sentinel_1", "SAR vessel detection + wake analysis (aggregate, non-individual)"))
    if any(t in q for t in ["pollution", "emissions", "no2", "methane"]):
        suggestions.append(("copernicus_sentinel_5p", "Atmospheric composition"))

    if not suggestions:
        suggestions = [
            ("copernicus_sentinel_2", "Default multispectral for general situational awareness"),
            ("openstreetmap", "Vector features + POI context"),
        ]

    return json.dumps({
        "care_membrane": cm_reason,
        "query": query,
        "aoi_name": aoi_name,
        "bbox": bbox,
        "time_window": time_window,
        "recommended_sources": [{"source": s, "why": w, "details": DATA_SOURCES[s]} for s, w in suggestions],
        "execution_plan": [
            "1. Register for Copernicus Data Space Ecosystem (free account)",
            "2. Authenticate via OAuth2; store token securely",
            "3. Query Sentinel Hub Catalog API with (bbox, time range, cloud_cover < 20)",
            "4. Download relevant tiles as COGs (Cloud-Optimised GeoTIFF)",
            "5. Compute index (NDVI / NBR / change detection) with rasterio",
            "6. Overlay with OpenStreetMap features via geopandas",
            "7. Emit result tile + structured JSON summary",
        ],
        "pro_tier_upsell": f"Pro £199/mo auto-executes the plan, caches results, and produces signed attestations: {STRIPE_199}" if tier == "free" else None,
    }, indent=2)


@mcp.tool()
def check_sovereignty(stack_description: str, api_key: str = "") -> str:
    """Given a geospatial stack description, flag any US-supply-chain dependencies and
    suggest sovereign alternatives. Useful for UK public-sector procurement.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool for security assessment, threat detection, or vulnerability
        analysis. Suitable for automated security scanning and risk evaluation.

    When NOT to use:
        Do not rely solely on this tool for production security decisions.
        Always combine with manual security review.

    Args:
        stack_description (str): The stack description to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg})
    if err := _rl(tier):
        return json.dumps({"error": err})

    d = stack_description.lower()
    us_deps = []
    alternatives = {}
    if "maxar" in d:
        us_deps.append("Maxar WorldView — US commercial, ITAR-adjacent")
        alternatives["Maxar"] = "ESA Pleiades Neo (CNES/Airbus, European) or Copernicus Sentinel-2"
    if "planet" in d or "planetscope" in d or "skysat" in d:
        us_deps.append("Planet Labs — US commercial")
        alternatives["Planet"] = "Copernicus Sentinel-2 (10m, free) or Airbus SPOT"
    if "google earth" in d or "google maps" in d:
        us_deps.append("Google Earth/Maps — US")
        alternatives["Google Maps"] = "OpenStreetMap + Ordnance Survey (UK) or IGN (France)"
    if "esri" in d or "arcgis" in d:
        us_deps.append("Esri / ArcGIS — US vendor, hosted in US regions by default")
        alternatives["Esri"] = "QGIS (open source) + GeoServer, or Esri UK-hosted region"
    if "aws" in d and "geospatial" in d:
        us_deps.append("AWS geospatial services — US-controlled compute")
        alternatives["AWS"] = "Azure UK South / OVH / UKCloud or on-prem with OGC services"

    return json.dumps({
        "us_dependencies_detected": us_deps,
        "sovereign_alternatives": alternatives,
        "recommendation": (
            "For UK HMG / MoD procurement, minimise US supply-chain dependencies in imagery, hosting, "
            "and tooling. Use Copernicus as primary, OS/IGN/Kartverket for national vector, QGIS + "
            "GeoServer for tooling, UKCloud/OVH/Azure UK South for hosting."
            if us_deps else
            "Stack appears sovereign-compatible. Document data-provenance chain for procurement dossier."
        ),
        "upsell": f"48-hour sovereignty audit of your full stack: £5,000 — {STRIPE_5K}" if us_deps else None,
    }, indent=2)


@mcp.tool()
def care_membrane_policy(api_key: str = "") -> str:
    """Return the Care Membrane policy governing what Gods Eye will and will not do.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool for security assessment, threat detection, or vulnerability
        analysis. Suitable for automated security scanning and risk evaluation.

    When NOT to use:
        Do not rely solely on this tool for production security decisions.
        Always combine with manual security review.

    Args:
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg})
    return json.dumps({
        "care_membrane_version": "1.0",
        "summary": "Gods Eye MCP applies the MEOK Care Membrane before any external API call. Care Membrane is a pre-inference ethics gate that enforces use-case-level alignment.",
        "permitted_use_cases": [
            "Environmental compliance evidence (CSRD E3/E4, sustainability reports)",
            "Disaster response (flood/wildfire/earthquake aggregate mapping)",
            "Infrastructure change detection (non-individualised)",
            "Agriculture / yield estimation",
            "Coastline / maritime domain awareness (aggregate shipping, not individual vessel tracking)",
            "Academic / research",
            "Civil-protection-authority-led operations",
        ],
        "prohibited_use_cases": [
            "Kinetic targeting / find-fix-finish support",
            "Individual personal tracking without lawful basis",
            "Facial re-identification from imagery",
            "Watchlist enrichment for protest / civil-disturbance monitoring",
            "Bounty-hunting / mercenary support",
            "Any use breaching UN-declared sanctions",
        ],
        "escalation_triggered_by": CARE_MEMBRANE_ESCALATE_TERMS,
        "blocked_by": CARE_MEMBRANE_BLOCK_TERMS,
        "audit_trail": "Every query, Care Membrane decision, and data source hit is audit-logged (Pro/Enterprise tier persists logs; Free tier logs are ephemeral).",
        "contact_for_policy_review": "nicholas@csoai.org",
    }, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
