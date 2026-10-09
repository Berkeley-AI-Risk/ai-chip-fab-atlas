#!/usr/bin/env python3
"""Render overview and per-campus world locator maps for the concise Atlas."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = Path("data/atlas.json")
DEFAULT_COUNTRIES = Path("data/geography/countries.geojson")
DEFAULT_OUTPUT_ROOT = Path("figures/campus-locators")
MANIFEST_NAME = "manifest.json"
OVERVIEW_NAME = "all-located-fabs-world-map.png"


class LocatorMapError(RuntimeError):
    """Raised when the locator-map cohort or coordinates are not defensible."""


def rooted(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def rings(geometry: dict[str, Any]) -> Iterable[list[list[float]]]:
    if geometry.get("type") == "Polygon":
        coordinates = geometry.get("coordinates", [])
        if coordinates:
            yield coordinates[0]
    elif geometry.get("type") == "MultiPolygon":
        for polygon in geometry.get("coordinates", []):
            if polygon:
                yield polygon[0]


def located_physical_sites(atlas: dict[str, Any]) -> list[dict[str, Any]]:
    physical = [
        site
        for site in atlas["sites"]
        if site["record_unit_type"] == "physical_front_end_campus"
    ]
    if len(physical) != 31:
        raise LocatorMapError(f"expected 31 physical campuses, found {len(physical)}")
    located: list[dict[str, Any]] = []
    for site in physical:
        location = site["location"]
        latitude = location.get("latitude_wgs84")
        longitude = location.get("longitude_wgs84")
        if latitude is None or longitude is None:
            if latitude is not None or longitude is not None:
                raise LocatorMapError(f"{site['campus_id']}: partial coordinate pair")
            continue
        latitude = float(latitude)
        longitude = float(longitude)
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            raise LocatorMapError(f"{site['campus_id']}: coordinate outside WGS84 bounds")
        if not location.get("coordinate_source"):
            raise LocatorMapError(f"{site['campus_id']}: located site lacks coordinate source")
        located.append(site)
    return located


def unlocated_physical_campus_ids(atlas: dict[str, Any]) -> list[str]:
    """Return unresolved physical campuses after validating all coordinate pairs."""
    located_ids = {site["campus_id"] for site in located_physical_sites(atlas)}
    return sorted(
        site["campus_id"]
        for site in atlas["sites"]
        if site["record_unit_type"] == "physical_front_end_campus"
        and site["campus_id"] not in located_ids
    )


def draw_countries(ax: Any, countries: dict[str, Any]) -> None:
    ax.set_facecolor("#F8FAFB")
    for feature in countries["features"]:
        for ring in rings(feature["geometry"]):
            ax.add_patch(
                Polygon(
                    ring,
                    closed=True,
                    facecolor="#C9D0D5",
                    edgecolor="#FFFFFF",
                    linewidth=0.35,
                    zorder=1,
                )
            )


def cluster_coordinates(
    coordinates: list[tuple[float, float]],
    longitude_threshold: float,
    latitude_threshold: float,
) -> list[dict[str, Any]]:
    parents = list(range(len(coordinates)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    for left, (left_lon, left_lat) in enumerate(coordinates):
        for right in range(left + 1, len(coordinates)):
            right_lon, right_lat = coordinates[right]
            if (
                abs(left_lon - right_lon) <= longitude_threshold
                and abs(left_lat - right_lat) <= latitude_threshold
            ):
                union(left, right)

    groups: dict[int, list[tuple[float, float]]] = {}
    for index, coordinate in enumerate(coordinates):
        groups.setdefault(find(index), []).append(coordinate)
    clusters = []
    for root in sorted(groups):
        members = groups[root]
        clusters.append(
            {
                "longitude": sum(point[0] for point in members) / len(members),
                "latitude": sum(point[1] for point in members) / len(members),
                "count": len(members),
                "member_coordinates_lon_lat": [list(point) for point in members],
            }
        )
    return clusters


def draw_clustered_markers(
    ax: Any,
    coordinates: list[tuple[float, float]],
    longitude_threshold: float,
    latitude_threshold: float,
) -> list[dict[str, Any]]:
    clusters = cluster_coordinates(
        coordinates,
        longitude_threshold=longitude_threshold,
        latitude_threshold=latitude_threshold,
    )
    for cluster in clusters:
        longitude = cluster["longitude"]
        latitude = cluster["latitude"]
        multiple = cluster["count"] > 1
        ax.scatter(
            [longitude],
            [latitude],
            s=112 if multiple else 62,
            marker="o",
            c="#FFFFFF",
            edgecolors="#FFFFFF",
            linewidths=1.1,
            zorder=4,
        )
        ax.scatter(
            [longitude],
            [latitude],
            s=66 if multiple else 28,
            marker="o",
            c="#B13A2F",
            edgecolors="#5B1D18",
            linewidths=0.55,
            zorder=5,
        )
        if multiple:
            ax.text(
                longitude,
                latitude,
                str(cluster["count"]),
                ha="center",
                va="center",
                color="#FFFFFF",
                fontsize=6.5,
                fontweight="bold",
                zorder=6,
            )
    return clusters


def render_locator(
    site: dict[str, Any], countries: dict[str, Any], output_path: Path
) -> dict[str, Any]:
    location = site["location"]
    latitude = float(location["latitude_wgs84"])
    longitude = float(location["longitude_wgs84"])

    fig, ax = plt.subplots(figsize=(3.2, 1.45), dpi=240)
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.03, top=0.97)
    draw_countries(ax, countries)
    ax.scatter(
        [longitude],
        [latitude],
        s=96,
        marker="o",
        c="#FFFFFF",
        edgecolors="#FFFFFF",
        linewidths=1.2,
        zorder=4,
    )
    marker = ax.scatter(
        [longitude],
        [latitude],
        s=45,
        marker="o",
        c="#B13A2F",
        edgecolors="#5B1D18",
        linewidths=0.65,
        zorder=5,
    )
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=240,
        facecolor="#F8FAFB",
        metadata={"Software": "AI-chip fab Atlas locator renderer"},
    )
    width, height = fig.canvas.get_width_height()
    marker_offsets = marker.get_offsets().tolist()
    plt.close(fig)
    return {
        "campus_id": site["campus_id"],
        "campus_name": site["campus_name"],
        "latitude_wgs84": latitude,
        "longitude_wgs84": longitude,
        "coordinate_precision": location["coordinate_precision"],
        "coordinate_source_id": location["coordinate_source"]["source_id"],
        "marker_offsets_lon_lat": marker_offsets,
        "output_path": output_path.relative_to(ROOT).as_posix()
        if output_path.is_relative_to(ROOT)
        else output_path.as_posix(),
        "width_px": width,
        "height_px": height,
        "sha256": file_sha256(output_path),
    }


def render_overview(
    sites: list[dict[str, Any]], countries: dict[str, Any], output_path: Path
) -> dict[str, Any]:
    coordinates = [
        (
            float(site["location"]["longitude_wgs84"]),
            float(site["location"]["latitude_wgs84"]),
        )
        for site in sites
    ]
    fig = plt.figure(figsize=(9.4, 4.75), dpi=240, facecolor="#F8FAFB")
    ax = fig.add_axes([0.015, 0.035, 0.97, 0.93])
    draw_countries(ax, countries)
    main_clusters = draw_clustered_markers(
        ax,
        coordinates,
        longitude_threshold=3.0,
        latitude_threshold=1.8,
    )
    ax.add_patch(
        Rectangle(
            (95, 18),
            50,
            28,
            facecolor="none",
            edgecolor="#8A8F94",
            linewidth=0.8,
            zorder=3,
        )
    )
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    inset = fig.add_axes([0.055, 0.075, 0.39, 0.39], facecolor="#F8FAFB")
    draw_countries(inset, countries)
    east_asia_coordinates = [
        point
        for point in coordinates
        if 95 <= point[0] <= 145 and 18 <= point[1] <= 46
    ]
    inset_clusters = draw_clustered_markers(
        inset,
        east_asia_coordinates,
        longitude_threshold=0.75,
        latitude_threshold=0.55,
    )
    inset.set_xlim(95, 145)
    inset.set_ylim(18, 46)
    inset.set_aspect("equal", adjustable="box")
    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_color("#8A8F94")
        spine.set_linewidth(0.8)
    inset.set_title(
        f"East Asia detail — {len(east_asia_coordinates)} mapped campuses",
        loc="left",
        fontsize=8.5,
        fontweight="bold",
        color="#33383D",
        pad=3,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=240,
        facecolor="#F8FAFB",
        metadata={"Software": "AI-chip fab Atlas locator renderer"},
    )
    width, height = fig.canvas.get_width_height()
    plt.close(fig)
    return {
        "mapped_physical_campus_count": len(sites),
        "marker_offsets_lon_lat": [list(point) for point in coordinates],
        "main_map_clusters": main_clusters,
        "east_asia_inset_clusters": inset_clusters,
        "output_path": output_path.relative_to(ROOT).as_posix()
        if output_path.is_relative_to(ROOT)
        else output_path.as_posix(),
        "width_px": width,
        "height_px": height,
        "sha256": file_sha256(output_path),
        "east_asia_inset_bounds_lon_lat": [95, 18, 145, 46],
    }


def render_all(
    atlas_path: Path = DEFAULT_ATLAS,
    countries_path: Path = DEFAULT_COUNTRIES,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    atlas_path = rooted(Path(atlas_path))
    countries_path = rooted(Path(countries_path))
    output_root = rooted(Path(output_root))
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    countries = json.loads(countries_path.read_text(encoding="utf-8"))
    located_sites = located_physical_sites(atlas)
    rows = []
    for site in located_sites:
        output_path = output_root / f"{site['campus_id'].lower()}-world-locator.png"
        rows.append(render_locator(site, countries, output_path))
    overview = render_overview(located_sites, countries, output_root / OVERVIEW_NAME)
    manifest = {
        "schema": "chip-fab-atlas-world-locators",
        "status": "PASS",
        "atlas_snapshot_date": atlas["snapshot_date"],
        "located_physical_campus_count": len(rows),
        "unlocated_physical_campus_ids": unlocated_physical_campus_ids(atlas),
        "inputs": {
            "atlas": {
                "path": atlas_path.relative_to(ROOT).as_posix(),
                "sha256": file_sha256(atlas_path),
            },
            "base_geography": {
                "path": countries_path.relative_to(ROOT).as_posix(),
                "sha256": file_sha256(countries_path),
                "attribution": "Natural Earth 1:110m, public domain",
            },
        },
        "overview_map": overview,
        "maps": rows,
    }
    manifest_path = output_root / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--countries", type=Path, default=DEFAULT_COUNTRIES)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    manifest = render_all(args.atlas, args.countries, args.output_root)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "located_physical_campus_count": manifest[
                    "located_physical_campus_count"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
