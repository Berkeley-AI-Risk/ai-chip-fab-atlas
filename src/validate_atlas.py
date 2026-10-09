#!/usr/bin/env python3
"""Validate the canonical public Atlas data and its local build assets."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "data/atlas.json"


class ValidationError(RuntimeError):
    pass


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def validate(path: Path = ATLAS, require_assets: bool = False) -> dict[str, int]:
    atlas = json.loads(path.read_text(encoding="utf-8"))
    sites = atlas["sites"]
    physical = [site for site in sites if site["record_unit_type"] == "physical_front_end_campus"]
    sources = atlas["source_registry"]
    source_ids = [source["source_id"] for source in sources]
    if len(sites) != 32 or len(physical) != 31:
        raise ValidationError("expected 32 records representing 31 physical campuses")
    if len(source_ids) != len(set(source_ids)):
        raise ValidationError("duplicate source IDs in the source registry")
    known = set(source_ids)
    declared: list[str] = []
    for item in walk(atlas):
        if isinstance(item.get("source_ids"), list):
            declared.extend(item["source_ids"])
        elif isinstance(item.get("source_ids"), str):
            declared.extend(part for part in item["source_ids"].split(";") if part)
        if item.get("source_id") and str(item["source_id"]).startswith("AISRC-"):
            declared.append(item["source_id"])
    unknown = set(declared) - known
    if unknown:
        raise ValidationError(f"unknown source references: {sorted(unknown)}")
    campus_ids = [site["campus_id"] for site in physical]
    if len(campus_ids) != len(set(campus_ids)):
        raise ValidationError("duplicate physical campus IDs")
    for site in physical:
        location = site["location"]
        if location.get("latitude_wgs84") is None or location.get("longitude_wgs84") is None:
            raise ValidationError(f"{site['campus_id']}: missing coordinate")
        if not location.get("coordinate_source", {}).get("url"):
            raise ValidationError(f"{site['campus_id']}: missing coordinate source")
        if len(site.get("imagery", [])) != 1:
            raise ValidationError(f"{site['campus_id']}: expected one selected image")
        asset = ROOT / site["imagery"][0]["render_path"]
        if require_assets and not asset.is_file():
            raise ValidationError(f"{site['campus_id']}: missing local image asset")
    lifecycle = Counter(site["lifecycle_status"] for site in sites)
    if dict(sorted(lifecycle.items())) != atlas["summary"]["lifecycle_status_counts"]:
        raise ValidationError("lifecycle summary does not recompute")
    if atlas["summary"]["source_count"] != len(sources):
        raise ValidationError("source summary does not recompute")
    recomputed = {
        "record_count": len(sites),
        "physical_campus_count": len(physical),
        "product_count": len(atlas["products"]),
        "component_count": len(atlas["product_components"]),
        "unresolved_product_count": len(atlas["unresolved_products"]),
        "review_decision_count": len(atlas["review_decisions"]),
        "imagery_record_count": sum(len(site.get("imagery", [])) for site in sites),
    }
    for key, actual in recomputed.items():
        if atlas["summary"][key] != actual:
            raise ValidationError(f"{key} summary does not recompute")
    return {
        "record_count": len(sites),
        "physical_campus_count": len(physical),
        "source_count": len(sources),
    }


if __name__ == "__main__":
    result = validate(require_assets=False)
    print(json.dumps({"status": "PASS", **result}, sort_keys=True))
