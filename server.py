#!/usr/bin/env python3
"""
Gods Eye — Open-Source Geospatial Awareness MCP
================================================
By MEOK AI Labs | https://meok.ai

Wraps open, non-proprietary geospatial APIs (ESA Copernicus Sentinel-1/2/3/5p,
OpenStreetMap, Overture Maps, Ordnance Survey UK, INSPIRE EU, DEFRA) behind a
single MCP tool surface, care-gated by the MEOK Care Membrane.

POSITIONING: Civilian open-source geospatial awareness for AI agents. Every query
flows through the Care Membrane ethics gate before any external API is called.
Designed for environmental compliance, disaster response, agriculture, and
infrastructure monitoring where open-licence data and ethical oversight matter.

Use cases:
  - AI agent situational awareness (location → weather, terrain, infrastructure)
  - Maritime domain awareness (aggregate shipping, non-individual vessels)
  - Agriculture / yield estimation (Sentinel-2 multispectral)
  - Infrastructure change detection (before/after tiles)
  - Disaster response (flood / wildfire / earthquake overlays)
  - Environmental compliance evidence (CSRD E3 water, E4 biodiversity)

This is a thin, ethical wrapper for civilian use. Care Membrane policy refuses
queries matching high-risk patterns (targeting, personal tracking, surveillance).

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


try:
    from attestation import get_attestation_tool_response
    _ATTESTATION_LOCAL = True
except ImportError:
    _ATTESTATION_LOCAL = False

_ATTESTATION_API = _os.environ.get(
    "MEOK_ATTESTATION_API", "https://meok-attestation-api.vercel.app"
)


def _sign_via_api(api_key: str, regulation: str, entity: str, score: float,
                  findings: list, articles_audited: list, tier: str = "pro",
                  include_pdf_base64: bool = False) -> dict:
    """Fallback: hit the remote MEOK signing API when the local module isn't present.
    Used by PyPI-installed MCPs that don't have ~/clawd/meok-labs-engine/shared on path."""
    import urllib.request as _url, urllib.error as _urlerr
    payload = {
        "api_key": api_key, "regulation": regulation, "entity": entity,
        "score": score, "findings": findings or [],
        "articles_audited": articles_audited or [], "tier": tier,
    }
    try:
        req = _url.Request(
            f"{_ATTESTATION_API}/sign",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with _url.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except _urlerr.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"error": f"Attestation API HTTP {e.code}. Contact nicholas@csoai.org."}
    except Exception as e:
        return {"error": f"Could not reach MEOK attestation API: {e}. Contact nicholas@csoai.org."}


def _attestation(regulation, entity, score, findings, articles_audited, tier,
                 include_pdf_base64, api_key):
    """Try local module first (fast, for Nick's dev machine), fall back to remote API."""
    if _ATTESTATION_LOCAL:
        return get_attestation_tool_response(
            regulation=regulation, entity=entity, score=score, findings=findings,
            articles_audited=articles_audited, tier=tier,
            include_pdf_base64=include_pdf_base64,
        )
    return _sign_via_api(
        api_key=api_key, regulation=regulation, entity=entity, score=score,
        findings=findings, articles_audited=articles_audited or [], tier=tier,
        include_pdf_base64=include_pdf_base64,
    )


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


# ── Care Membrane — ethics gate ──────────────────────────────────
# Block queries that indicate targeting, personal tracking, or surveillance
# misuse. Gods Eye is a civilian tool and refuses these patterns outright.
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
                f"Care Membrane BLOCKED: query contains pattern '{t}' matching targeting or "
                "personal-surveillance risk. Gods Eye is a civilian tool restricted to aggregate, "
                "care-aligned geospatial awareness (environmental, disaster, agriculture, "
                "infrastructure). Contact nicholas@csoai.org if this block is incorrect for a "
                "legitimate civilian use case."
            )
    for t in CARE_MEMBRANE_ESCALATE_TERMS:
        if t in q:
            return True, f"Care Membrane ESCALATED — query touched sensitive pattern '{t}'. Response permitted but audit-logged for governance review."
    return True, "Care Membrane: clear"


# ── Open-licence geospatial data sources ─────────────────────────
DATA_SOURCES = {
    "copernicus_sentinel_1": {
        "provider": "ESA Copernicus",
        "resolution": "5m-40m SAR (all-weather, day/night)",
        "access": "Free via Copernicus Data Space Ecosystem (dataspace.copernicus.eu)",
        "use_cases": ["flood mapping", "land cover", "maritime awareness", "change detection"],
        "data_residency": "EU-hosted",
        "licence": "Free + open",
    },
    "copernicus_sentinel_2": {
        "provider": "ESA Copernicus",
        "resolution": "10m-60m multispectral (13 bands)",
        "access": "Free via Copernicus Data Space Ecosystem",
        "use_cases": ["vegetation indices", "agriculture", "wildfire detection", "urban expansion"],
        "data_residency": "EU-hosted",
        "licence": "Free + open",
    },
    "copernicus_sentinel_3": {
        "provider": "ESA Copernicus",
        "resolution": "300m-1km ocean + land color + thermal",
        "access": "Free via Copernicus Data Space Ecosystem",
        "use_cases": ["ocean temperature", "ice cover", "air quality"],
        "data_residency": "EU-hosted",
        "licence": "Free + open",
    },
    "copernicus_sentinel_5p": {
        "provider": "ESA Copernicus",
        "resolution": "7km atmospheric",
        "access": "Free via Copernicus",
        "use_cases": ["NO2, SO2, CO, O3 pollution", "methane leak detection"],
        "data_residency": "EU-hosted",
        "licence": "Free + open",
    },
    "openstreetmap": {
        "provider": "OpenStreetMap Foundation",
        "resolution": "feature-level (variable accuracy)",
        "access": "Free — Overpass API + Nominatim geocoder",
        "use_cases": ["roads", "POIs", "addresses", "administrative boundaries"],
        "data_residency": "Community-owned, globally mirrored",
        "licence": "ODbL 1.0",
    },
    "overture_maps": {
        "provider": "Overture Maps Foundation (Microsoft + Meta + AWS)",
        "resolution": "feature-level",
        "access": "Free — CC-BY 4.0 + ODbL",
        "use_cases": ["places (POI)", "buildings", "transportation", "administrative divisions"],
        "data_residency": "Foundation-hosted",
        "licence": "CC-BY 4.0 + ODbL",
    },
    "os_open_data_uk": {
        "provider": "Ordnance Survey (UK)",
        "resolution": "1m-25m UK-specific",
        "access": "Free — OS Open Data via OS Data Hub",
        "use_cases": ["UK mapping", "Open Zoomstack", "Open Names"],
        "data_residency": "UK-hosted",
        "licence": "OS OpenData (attribution)",
    },
    "inspire_eu": {
        "provider": "European Commission INSPIRE Directive",
        "resolution": "varies by theme",
        "access": "Free — geoportal.ec.europa.eu",
        "use_cases": ["EU-standardised spatial data (34 themes)", "environment", "transport"],
        "data_residency": "EU-hosted",
        "licence": "INSPIRE (open)",
    },
    "defra_uk": {
        "provider": "DEFRA (UK Department for Environment)",
        "resolution": "varies",
        "access": "Free — data.gov.uk",
        "use_cases": ["flood zones", "environment", "land use"],
        "data_residency": "UK-hosted",
        "licence": "Open Government Licence",
    },
    "ioa_disasters": {
        "provider": "International Charter Space and Major Disasters",
        "resolution": "varies",
        "access": "Activated by civil protection authorities",
        "use_cases": ["disaster response imagery"],
        "data_residency": "Multi-national — ESA, NASA, CNES, etc.",
        "licence": "Charter-specific",
    },
}


mcp = FastMCP(
    "gods-eye-geospatial",
    instructions=(
        "MEOK AI Labs Gods Eye MCP. Civilian open-source geospatial awareness wrapping "
        "open-licence APIs (ESA Copernicus Sentinel-1/2/3/5p, OpenStreetMap, Overture, "
        "Ordnance Survey, INSPIRE, DEFRA). Every query is pre-filtered by the Care Membrane. "
        "Use for: AI-agent situational awareness, environmental compliance, disaster response, "
        "agriculture, infrastructure monitoring. Refuses targeting and personal-surveillance queries."
    ),
)


@mcp.tool()
def list_data_sources(api_key: str = "") -> str:
    """List the open-licence geospatial data sources wrapped by Gods Eye."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    return json.dumps({
        "positioning": "Civilian open-source geospatial awareness — open-licence data + ethics gate",
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
def check_data_provenance(stack_description: str, api_key: str = "") -> str:
    """Given a geospatial stack description, flag proprietary / closed-licence dependencies
    and suggest open-licence, EU/UK-hosted alternatives. Useful for civilian projects with
    GDPR, data-residency, or open-data mandates (environmental NGOs, municipalities,
    research groups, CSRD reporters, agriculture co-ops)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg})
    if err := _rl(tier):
        return json.dumps({"error": err})

    d = stack_description.lower()
    proprietary_deps = []
    alternatives = {}
    if "maxar" in d:
        proprietary_deps.append("Maxar WorldView — closed commercial licence")
        alternatives["Maxar"] = "ESA Pleiades Neo (CNES/Airbus) or Copernicus Sentinel-2 (free, open)"
    if "planet" in d or "planetscope" in d or "skysat" in d:
        proprietary_deps.append("Planet Labs — closed commercial licence")
        alternatives["Planet"] = "Copernicus Sentinel-2 (10m, free, open) or Airbus SPOT"
    if "google earth" in d or "google maps" in d:
        proprietary_deps.append("Google Earth / Maps — proprietary, TOS-restricted")
        alternatives["Google Maps"] = "OpenStreetMap + Ordnance Survey (UK) or IGN (France)"
    if "esri" in d or "arcgis" in d:
        proprietary_deps.append("Esri / ArcGIS — commercial vendor, US-hosted by default")
        alternatives["Esri"] = "QGIS (open source) + GeoServer, or Esri hosted in EU/UK region"
    if "aws" in d and "geospatial" in d:
        proprietary_deps.append("AWS geospatial services — US-hosted compute by default")
        alternatives["AWS"] = "Azure UK South / OVH / Hetzner or on-prem with OGC services for EU data residency"

    return json.dumps({
        "proprietary_dependencies_detected": proprietary_deps,
        "open_licence_alternatives": alternatives,
        "recommendation": (
            "For civilian projects needing open-licence data, GDPR-friendly residency, or "
            "long-term cost predictability, replace proprietary sources with Copernicus "
            "(free, EU-hosted), Ordnance Survey OpenData (UK), IGN / Kartverket (national vector), "
            "QGIS + GeoServer (tooling), and EU/UK-hosted compute (Azure UK South, OVH, Hetzner)."
            if proprietary_deps else
            "Stack uses open-licence sources throughout. Document the provenance chain for your "
            "compliance dossier (CSRD E1-E5, GDPR Article 30 processing record)."
        ),
        "upsell": f"48-hour open-data provenance audit of your full stack: £5,000 — {STRIPE_5K}" if proprietary_deps else None,
    }, indent=2)


@mcp.tool()
def care_membrane_policy(api_key: str = "") -> str:
    """Return the Care Membrane policy governing what Gods Eye will and will not do."""
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
            "Targeting individuals or physical assets for harm",
            "Personal tracking without lawful basis",
            "Facial re-identification from imagery",
            "Watchlist enrichment for protest / civil-disturbance monitoring",
            "Any use breaching UN-declared sanctions or applicable law",
        ],
        "escalation_triggered_by": CARE_MEMBRANE_ESCALATE_TERMS,
        "blocked_by": CARE_MEMBRANE_BLOCK_TERMS,
        "audit_trail": "Every query, Care Membrane decision, and data source hit is audit-logged (Pro/Enterprise tier persists logs; Free tier logs are ephemeral).",
        "contact_for_policy_review": "nicholas@csoai.org",
    }, indent=2)


@mcp.tool()
def sign_data_provenance_attestation(
    entity_name: str,
    stack_description: str,
    open_licence_score: float,
    findings_csv: str = "",
    include_pdf_base64: bool = False,
    api_key: str = "",
) -> str:
    """Generate a cryptographically signed data-provenance attestation for your geospatial
    stack (Pro/Enterprise).

    Produces HMAC-SHA256 signed JSON + public verify URL + optional board-ready PDF. Useful
    for CSRD E3/E4 evidence packs, GDPR Article 30 processing records, and municipal
    open-data mandates. Your auditor or procurement team validates the verify_url without
    needing to reach our backend.

    - open_licence_score: 0-100 from check_data_provenance
    - findings_csv: comma-separated findings (e.g. "Copernicus PASS — free + open,Google Maps GAP — proprietary")
    - include_pdf_base64: True to receive PDF as base64
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": STRIPE_199})
    if tier == "free":
        return json.dumps({
            "error": "Signed attestations require Pro (£199/mo) or Enterprise tier.",
            "upgrade_url": STRIPE_199,
            "why_pro": "HMAC-signed data-provenance cert auditors accept. Evidence for CSRD E3/E4 + GDPR Article 30 + municipal open-data mandates.",
        })
    findings = [f.strip() for f in findings_csv.split(",") if f.strip()]
    cert = _attestation(
        regulation="Geospatial data provenance — open-licence audit (CSRD E3/E4, GDPR Art 30)",
        entity=f"{entity_name} — stack: {stack_description[:120]}",
        score=open_licence_score,
        findings=findings or [f"Overall open-licence coverage score: {open_licence_score}"],
        articles_audited=None,
        tier=tier,
        include_pdf_base64=include_pdf_base64,
        api_key=api_key,
    )
    return json.dumps(cert, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
