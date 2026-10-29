"""The highest warning level among nearby incidents, from what DataQuoll publishes.

Since DataQuoll v1.105.0 an incident carries `warningLevel` only as the agency states it: `none` where the agency
states no level, and NO `warningLevel` at all where DataQuoll cannot confirm the agency's level (for example a QLD EMQ
or TasALERT warning whose level could have been derived from its CAP severity). A missing level is unknown, never
"none": reading it as none would say "no warning" beside a real one.

The rule mirrors DataQuoll's own /events maximum: per incident, the highest level any of its records states (the NSW
RFS GeoJSON record and its CAP twin, and the two ACT ESA records, are one incident); the maximum is known only when no
incident's level is unknown, or a stated one is already an Emergency Warning. Pure Python, no Home Assistant import,
so tests/test_levels.py runs on its own.
"""
from __future__ import annotations

WARNING_PRIORITY = {"none": 0, "advice": 1, "watch_and_act": 2, "emergency_warning": 3}
TOP = "emergency_warning"

# DataQuoll's SAME_INCIDENT_GROUPS (packages/api/src/lib/map-rules.ts): one incident from two feeds.
SAME_INCIDENT_GROUPS = (
    ("act", ("act-current-", "act-all-")),
    ("nsw-rfs", ("nsw-rfs-cap-", "nsw-rfs-")),
)


def incident_key(feature_id: str) -> str:
    for group, prefixes in SAME_INCIDENT_GROUPS:
        for prefix in prefixes:
            if feature_id.startswith(prefix):
                return f"{group}:{feature_id[len(prefix):]}"
    return feature_id


def max_warning_level(features: list[dict]) -> str | None:
    """The highest stated level, or None when there is none to report or it cannot be known."""
    if not features:
        return None
    incidents: dict[str, dict] = {}
    for i, f in enumerate(features):
        key = incident_key(str(f.get("id") or f"#{i}"))
        level = (f.get("properties") or {}).get("warningLevel")
        cur = incidents.setdefault(key, {"best": None, "missing": False})
        if level in WARNING_PRIORITY:
            if cur["best"] is None or WARNING_PRIORITY[level] > WARNING_PRIORITY[cur["best"]]:
                cur["best"] = level
        else:
            cur["missing"] = True
    stated = [c["best"] for c in incidents.values() if c["best"] is not None]
    unknown = any(c["best"] is None and c["missing"] for c in incidents.values())
    best = max(stated, key=lambda w: WARNING_PRIORITY[w]) if stated else None
    if unknown and best != TOP:
        return None
    return best
