#!/usr/bin/env python3
"""Render a publication figure comparing Atlas fabs with Epoch AI data centers.

The strict local replay joins Epoch's official CSV to ``lngLat`` pairs embedded
in its archived interactive-map page and fails closed if the two sources
disagree.  A public-safe mode reads the small derived coordinate CSV produced by
that replay, so a public checkout can render the figure without redistributing
or reading the archived webpage snapshot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from hashlib import sha256
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Iterable

MATPLOTLIB_CACHE = Path(tempfile.gettempdir()) / "fab_epoch_location_matplotlib_cache"
MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", MATPLOTLIB_CACHE.as_posix())

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = Path("data/atlas.json")
DEFAULT_EPOCH_CSV = Path(
    "data/fab-data-center-comparison/epoch-source.csv"
)
DEFAULT_EPOCH_MAP_HTML = Path(
    "data/fab-data-center-comparison/epoch-map-source.html"
)
DEFAULT_COUNTRIES = Path("data/geography/countries.geojson")
DEFAULT_OUTPUT_ROOT = Path("figures")
DEFAULT_DERIVED_ROOT = Path("data/fab-data-center-comparison")

FIGURE_STEM = "fab-data-center-comparison"
MANIFEST_NAME = "fab-data-center-comparison-manifest.json"
ATLAS_LOCATIONS_NAME = "atlas-campuses.csv"
EPOCH_LOCATIONS_NAME = "epoch-data-centers.csv"
DEFAULT_EPOCH_COORDINATES = DEFAULT_DERIVED_ROOT / EPOCH_LOCATIONS_NAME

EXPECTED_FAB_COUNT = 31
EXPECTED_EPOCH_COUNT = 83
EXPECTED_EPOCH_STATUS_COUNTS = {
    "operational": 67,
    "under_construction": 16,
}
FIGURE_RETRIEVAL_DATE = "2026-08-25"
FAB_LIFECYCLE_GROUPS = {
    "operating": "operating",
    "operating_with_expansion": "operating",
    "operating_ramp": "operating",
    "operating_with_7nm_tapeout": "operating",
    "operating_with_ramp": "operating",
    "under_construction": "under_construction",
    "under_construction_slowed": "under_construction",
    "under_construction_preoperational": "under_construction",
    "commissioning_or_initial_operations": "commissioning_or_pilot",
    "pilot_line": "commissioning_or_pilot",
    # Preserve an explicit fallback for a future record whose lifecycle cannot
    # be resolved.  Such a record should be described as uncertain, not folded
    # into either operating or construction.
    "operating_or_ramp_unresolved": "status_uncertain",
    "construction_or_ramp_unresolved": "status_uncertain",
}
EXPECTED_FAB_LIFECYCLE_GROUP_COUNTS = {
    "operating": 25,
    "under_construction": 4,
    "commissioning_or_pilot": 1,
    "status_uncertain": 1,
}
EPOCH_DATA_URL = "https://epoch.ai/data/ai-data-centers"
EPOCH_DOWNLOAD_URL = "https://epoch.ai/data/data_centers/data_centers.csv"
EPOCH_MAP_URL = "https://epoch.ai/data/ai-data-centers/map"
EPOCH_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
NATURAL_EARTH_URL = "https://www.naturalearthdata.com/"

GRAPHITE = "#33393F"
MUTED = "#5A6470"
LAND = "#D9DCE0"
OCEAN = "#FFFFFF"
FAB_COLOR = "#8C3B2E"
DATA_CENTER_COLOR = "#5A6470"

# Astro serializes map records as tagged arrays.  The exact-name join below is
# deliberately strict so a site can never inherit a neighboring record's point.
EPOCH_MAP_POSITION_PATTERN = re.compile(
    r'\[0,\{"id":\[0,"(?P<name>[^"]+)"\].*?'
    r'"operational":\[0,(?P<operational>true|false)\].*?'
    r'"lngLat":\[1,\[\[0,(?P<longitude>-?[0-9.]+)\],'
    r'\[0,(?P<latitude>-?[0-9.]+)\]\]\]',
    re.DOTALL,
)


class ComparisonFigureError(RuntimeError):
    """Raised when a source, join, coordinate, or expected count is invalid."""


def rooted(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative_or_absolute(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def validate_coordinate(name: str, longitude: float, latitude: float) -> None:
    if not (-180.0 <= longitude <= 180.0 and -90.0 <= latitude <= 90.0):
        raise ComparisonFigureError(
            f"{name}: coordinate outside WGS84 bounds ({longitude}, {latitude})"
        )


def load_atlas_fabs(atlas_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    physical = [
        site
        for site in atlas["sites"]
        if site["record_unit_type"] == "physical_front_end_campus"
    ]
    if len(physical) != EXPECTED_FAB_COUNT:
        raise ComparisonFigureError(
            f"expected {EXPECTED_FAB_COUNT} physical campuses, found {len(physical)}"
        )
    campus_ids = [site["campus_id"] for site in physical]
    duplicate_ids = sorted(
        campus_id
        for campus_id, count in Counter(campus_ids).items()
        if count > 1
    )
    if duplicate_ids:
        raise ComparisonFigureError(
            f"duplicate physical-campus IDs: {duplicate_ids}"
        )

    rows: list[dict[str, Any]] = []
    for site in physical:
        location = site["location"]
        longitude = location.get("longitude_wgs84")
        latitude = location.get("latitude_wgs84")
        if longitude is None or latitude is None:
            raise ComparisonFigureError(
                f"{site['campus_id']}: physical campus lacks a complete coordinate pair"
            )
        longitude = float(longitude)
        latitude = float(latitude)
        validate_coordinate(site["campus_name"], longitude, latitude)
        source = location.get("coordinate_source")
        if not source or not source.get("source_id") or not source.get("url"):
            raise ComparisonFigureError(
                f"{site['campus_id']}: plotted campus lacks coordinate provenance"
            )
        lifecycle_status = site.get("lifecycle_status")
        lifecycle_group = FAB_LIFECYCLE_GROUPS.get(lifecycle_status)
        if lifecycle_group is None:
            raise ComparisonFigureError(
                f"{site['campus_id']}: unmapped lifecycle status {lifecycle_status!r}"
            )
        rows.append(
            {
                "campus_id": site["campus_id"],
                "campus_name": site["campus_name"],
                "operator": site["operator"],
                "country_code": location["country_code"],
                "longitude_wgs84": longitude,
                "latitude_wgs84": latitude,
                "coordinate_precision": location["coordinate_precision"],
                "coordinate_source_id": source["source_id"],
                "coordinate_source_url": source["url"],
                "lifecycle_status": lifecycle_status,
                "lifecycle_display_group": lifecycle_group,
                "lifecycle_as_of_date": site.get("lifecycle_as_of_date", ""),
            }
        )
    lifecycle_counts = Counter(row["lifecycle_display_group"] for row in rows)
    if lifecycle_counts != Counter(EXPECTED_FAB_LIFECYCLE_GROUP_COUNTS):
        raise ComparisonFigureError(
            "unexpected fab lifecycle-group counts: "
            f"{dict(sorted(lifecycle_counts.items()))}"
        )
    return atlas, rows


def parse_epoch_map_positions(map_html_path: Path) -> dict[str, dict[str, Any]]:
    source = html.unescape(map_html_path.read_text(encoding="utf-8"))
    positions: dict[str, dict[str, Any]] = {}
    for match in EPOCH_MAP_POSITION_PATTERN.finditer(source):
        name = match.group("name")
        longitude = float(match.group("longitude"))
        latitude = float(match.group("latitude"))
        validate_coordinate(name, longitude, latitude)
        if name in positions:
            raise ComparisonFigureError(f"duplicate Epoch map record name: {name}")
        positions[name] = {
            "longitude_wgs84": longitude,
            "latitude_wgs84": latitude,
            "operational": match.group("operational") == "true",
        }
    if len(positions) != EXPECTED_EPOCH_COUNT:
        raise ComparisonFigureError(
            f"expected {EXPECTED_EPOCH_COUNT} Epoch map points, found {len(positions)}"
        )
    return positions


def load_epoch_data_centers(
    epoch_csv_path: Path, map_html_path: Path
) -> list[dict[str, Any]]:
    with epoch_csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "Name",
            "Country",
            "Address",
            "Owner",
            "Current H100 equivalents",
            "Current power (MW)",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ComparisonFigureError(
                f"Epoch CSV lacks required columns: {sorted(missing)}"
            )
        csv_rows = list(reader)
    if len(csv_rows) != EXPECTED_EPOCH_COUNT:
        raise ComparisonFigureError(
            f"expected {EXPECTED_EPOCH_COUNT} Epoch CSV records, found {len(csv_rows)}"
        )
    names = [row["Name"] for row in csv_rows]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise ComparisonFigureError(f"duplicate Epoch CSV names: {duplicates}")

    positions = parse_epoch_map_positions(map_html_path)
    csv_names = set(names)
    map_names = set(positions)
    if csv_names != map_names:
        raise ComparisonFigureError(
            "Epoch CSV/map name mismatch: "
            f"CSV-only={sorted(csv_names - map_names)}, "
            f"map-only={sorted(map_names - csv_names)}"
        )

    rows: list[dict[str, Any]] = []
    for row in csv_rows:
        map_record = positions[row["Name"]]
        longitude = map_record["longitude_wgs84"]
        latitude = map_record["latitude_wgs84"]
        rows.append(
            {
                "name": row["Name"],
                "country": row["Country"],
                "address": row["Address"],
                "owner_raw": row["Owner"],
                "current_h100_equivalents": float(row["Current H100 equivalents"]),
                "current_power_mw": float(row["Current power (MW)"]),
                "longitude_wgs84": longitude,
                "latitude_wgs84": latitude,
                "status_from_epoch_map": (
                    "operational" if map_record["operational"] else "under_construction"
                ),
                "coordinate_source": "Epoch AI official interactive map lngLat",
                "coordinate_source_url": EPOCH_MAP_URL,
            }
        )
    validate_epoch_data_center_rows(rows)
    return rows


def validate_epoch_data_center_rows(rows: list[dict[str, Any]]) -> None:
    """Validate the frozen plotted Epoch cohort independently of input mode."""
    if len(rows) != EXPECTED_EPOCH_COUNT:
        raise ComparisonFigureError(
            f"expected {EXPECTED_EPOCH_COUNT} Epoch records, found {len(rows)}"
        )
    names = [str(row.get("name", "")).strip() for row in rows]
    if any(not name for name in names):
        raise ComparisonFigureError("Epoch records contain a blank name")
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise ComparisonFigureError(f"duplicate Epoch record names: {duplicates}")

    for row in rows:
        validate_coordinate(
            str(row["name"]),
            float(row["longitude_wgs84"]),
            float(row["latitude_wgs84"]),
        )
    status_counts = Counter(str(row["status_from_epoch_map"]) for row in rows)
    if status_counts != Counter(EXPECTED_EPOCH_STATUS_COUNTS):
        raise ComparisonFigureError(
            "unexpected Epoch status counts: "
            f"{dict(sorted(status_counts.items()))}"
        )


def load_epoch_coordinate_csv(coordinate_csv_path: Path) -> list[dict[str, Any]]:
    """Load the public-safe coordinate table emitted by the strict local replay."""
    required = {
        "name",
        "country",
        "address",
        "owner_raw",
        "current_h100_equivalents",
        "current_power_mw",
        "longitude_wgs84",
        "latitude_wgs84",
        "status_from_epoch_map",
        "coordinate_source",
        "coordinate_source_url",
    }
    with coordinate_csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ComparisonFigureError(
                f"Epoch coordinate CSV lacks required columns: {sorted(missing)}"
            )
        source_rows = list(reader)

    rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        name = str(source_row["name"]).strip()
        try:
            current_h100_equivalents = float(source_row["current_h100_equivalents"])
            current_power_mw = float(source_row["current_power_mw"])
            longitude = float(source_row["longitude_wgs84"])
            latitude = float(source_row["latitude_wgs84"])
        except (TypeError, ValueError) as error:
            raise ComparisonFigureError(
                f"{name or '<blank>'}: invalid numeric field in Epoch coordinate CSV"
            ) from error
        coordinate_source = str(source_row["coordinate_source"]).strip()
        coordinate_source_url = str(source_row["coordinate_source_url"]).strip()
        if (
            coordinate_source != "Epoch AI official interactive map lngLat"
            or coordinate_source_url != EPOCH_MAP_URL
        ):
            raise ComparisonFigureError(
                f"{name or '<blank>'}: unrecognized Epoch coordinate provenance"
            )
        rows.append(
            {
                "name": name,
                "country": source_row["country"],
                "address": source_row["address"],
                "owner_raw": source_row["owner_raw"],
                "current_h100_equivalents": current_h100_equivalents,
                "current_power_mw": current_power_mw,
                "longitude_wgs84": longitude,
                "latitude_wgs84": latitude,
                "status_from_epoch_map": source_row["status_from_epoch_map"],
                "coordinate_source": coordinate_source,
                "coordinate_source_url": coordinate_source_url,
            }
        )
    validate_epoch_data_center_rows(rows)
    return rows


def rings(geometry: dict[str, Any]) -> Iterable[list[list[float]]]:
    if geometry.get("type") == "Polygon":
        coordinates = geometry.get("coordinates", [])
        if coordinates:
            yield coordinates[0]
    elif geometry.get("type") == "MultiPolygon":
        for polygon in geometry.get("coordinates", []):
            if polygon:
                yield polygon[0]


def portable_font_record(path: Path, role: str) -> dict[str, str | int]:
    """Describe a font without retaining its machine-local installation path."""
    return {
        "role": role,
        "filename": path.name,
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
    }


def register_source_sans() -> tuple[str, str, list[dict[str, str | int]]]:
    """Register the figure font (Source Sans Pro), with a portable fallback."""
    candidates: list[tuple[str, Path]] = []
    if shutil.which("kpsewhich"):
        for role, filename in (
            ("regular", "SourceSansPro-Regular.otf"),
            ("semibold", "SourceSansPro-Semibold.otf"),
        ):
            result = subprocess.run(
                ["kpsewhich", filename],
                check=False,
                capture_output=True,
                text=True,
            )
            candidate = Path(result.stdout.strip()) if result.stdout.strip() else None
            if candidate and candidate.is_file():
                candidates.append((role, candidate))
    if len(candidates) == 2:
        for _, candidate in candidates:
            font_manager.fontManager.addfont(candidate)
        return (
            "Source Sans Pro",
            "semibold",
            [portable_font_record(path, role) for role, path in candidates],
        )

    fallback_fonts: list[dict[str, str | int]] = []
    for role, weight in (("regular", "normal"), ("bold", "bold")):
        fallback_path = Path(
            font_manager.findfont(
                font_manager.FontProperties(family="DejaVu Sans", weight=weight),
                fallback_to_default=False,
            )
        )
        if not fallback_path.is_file():
            raise ComparisonFigureError(
                f"Matplotlib fallback font is unavailable: {fallback_path.name}"
            )
        fallback_fonts.append(portable_font_record(fallback_path, role))
    return "DejaVu Sans", "bold", fallback_fonts


def project_countries(
    countries: dict[str, Any], transformer: Transformer
) -> list[list[tuple[float, float]]]:
    projected: list[list[tuple[float, float]]] = []
    for feature in countries["features"]:
        if feature.get("properties", {}).get("ADMIN") == "Antarctica":
            continue
        for ring in rings(feature["geometry"]):
            longitudes = [float(point[0]) for point in ring]
            latitudes = [float(point[1]) for point in ring]
            xs, ys = transformer.transform(longitudes, latitudes)
            projected.append(list(zip(xs, ys)))
    return projected


def draw_map_base(
    ax: Any,
    projected_countries: list[list[tuple[float, float]]],
    x_limits: tuple[float, float],
    y_limits: tuple[float, float],
) -> None:
    ax.set_facecolor(OCEAN)
    for ring in projected_countries:
        ax.add_patch(
            Polygon(
                ring,
                closed=True,
                facecolor=LAND,
                edgecolor=OCEAN,
                linewidth=0.24,
                zorder=1,
            )
        )
    ax.set_xlim(*x_limits)
    ax.set_ylim(*y_limits)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")


def render_figure(
    atlas: dict[str, Any],
    fabs: list[dict[str, Any]],
    data_centers: list[dict[str, Any]],
    countries: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    family, title_weight, fonts = register_source_sans()
    matplotlib.rcParams.update(
        {
            "font.family": family,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "path",
            "svg.hashsalt": "fab-data-center-location-comparison",
        }
    )
    transformer = Transformer.from_crs("EPSG:4326", "ESRI:54035", always_xy=True)
    projected_countries = project_countries(countries, transformer)
    x_left, _ = transformer.transform(-180.0, 0.0)
    x_right, _ = transformer.transform(180.0, 0.0)
    _, y_bottom = transformer.transform(0.0, -58.0)
    _, y_top = transformer.transform(0.0, 85.0)
    x_limits = (x_left, x_right)
    y_limits = (y_bottom, y_top)

    fig = plt.figure(figsize=(7.10, 2.82), dpi=200, facecolor=OCEAN)
    left_ax = fig.add_axes([0.018, 0.205, 0.472, 0.560])
    right_ax = fig.add_axes([0.510, 0.205, 0.472, 0.560])
    for ax in (left_ax, right_ax):
        draw_map_base(ax, projected_countries, x_limits, y_limits)

    fab_x, fab_y = transformer.transform(
        [row["longitude_wgs84"] for row in fabs],
        [row["latitude_wgs84"] for row in fabs],
    )
    dc_x, dc_y = transformer.transform(
        [row["longitude_wgs84"] for row in data_centers],
        [row["latitude_wgs84"] for row in data_centers],
    )
    fab_status_counts = Counter(row["lifecycle_display_group"] for row in fabs)
    dc_status_counts = Counter(row["status_from_epoch_map"] for row in data_centers)
    left_ax.scatter(
        fab_x,
        fab_y,
        s=18,
        marker="D",
        c=FAB_COLOR,
        edgecolors=OCEAN,
        linewidths=0.45,
        alpha=0.94,
        zorder=4,
    )
    right_ax.scatter(
        dc_x,
        dc_y,
        s=18,
        marker="o",
        c=DATA_CENTER_COLOR,
        edgecolors=OCEAN,
        linewidths=0.45,
        alpha=0.90,
        zorder=4,
    )

    fig.text(
        0.022,
        0.925,
        f"AI Chip Fab Atlas (n={len(fabs)})",
        ha="left",
        va="top",
        fontsize=10.0,
        fontweight=title_weight,
        color=GRAPHITE,
    )
    fig.text(
        0.514,
        0.925,
        f"AI data centers in Epoch AI’s database (n={len(data_centers)})",
        ha="left",
        va="top",
        fontsize=10.0,
        fontweight=title_weight,
        color=GRAPHITE,
    )
    fig.text(
        0.022,
        0.855,
        f"{fab_status_counts['operating']} operating · "
        f"{fab_status_counts['under_construction']} under construction · "
        f"{fab_status_counts['commissioning_or_pilot']} commissioning/pilot · "
        f"{fab_status_counts['status_uncertain']} status uncertain",
        ha="left",
        va="top",
        fontsize=5.7,
        color=MUTED,
    )
    fig.text(
        0.514,
        0.855,
        f"{dc_status_counts['operational']} operational · "
        f"{dc_status_counts['under_construction']} under construction",
        ha="left",
        va="top",
        fontsize=7.2,
        color=MUTED,
    )
    fig.text(
        0.022,
        0.808,
        "Data reviewed 25 Aug 2026",
        ha="left",
        va="top",
        fontsize=6.7,
        color=MUTED,
    )
    fig.text(
        0.514,
        0.808,
        "Data reviewed 25 Aug 2026",
        ha="left",
        va="top",
        fontsize=6.7,
        color=MUTED,
    )
    fig.text(
        0.022,
        0.112,
        "Each marker denotes one database record; nearby records may overlap. Marker size does not encode facility size, output, compute, or status.",
        ha="left",
        va="top",
        fontsize=6.7,
        color=MUTED,
    )
    fig.text(
        0.022,
        0.055,
        "Sources: authors’ AI Chip Fab Atlas; Epoch AI, “AI Data Centers” (CC BY 4.0); Natural Earth 1:110m (public domain). Neither dataset is guaranteed to be exhaustive.",
        ha="left",
        va="top",
        fontsize=6.7,
        color=MUTED,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    pdf_path = output_root / f"{FIGURE_STEM}.pdf"
    svg_path = output_root / f"{FIGURE_STEM}.svg"
    png_path = output_root / f"{FIGURE_STEM}.png"
    jpeg_path = output_root / f"{FIGURE_STEM}.jpg"
    fig.savefig(
        pdf_path,
        facecolor=OCEAN,
        metadata={
            "Title": "Locations in the AI Chip Fab Atlas and Epoch AI data centers",
            "Author": "Berkeley AI Risk",
            "Subject": "Side-by-side geographic comparison of two public datasets",
            "Keywords": "chip fabs, AI data centers, Epoch AI, public evidence",
            "CreationDate": datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc),
            "ModDate": datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc),
        },
    )
    fig.savefig(
        svg_path,
        facecolor=OCEAN,
        metadata={
            "Title": "Locations in the AI Chip Fab Atlas and Epoch AI data centers",
            "Date": "2026-08-25",
            "Creator": "Berkeley AI Risk",
            "Description": "Side-by-side geographic comparison of two public datasets",
        },
    )
    fig.savefig(
        png_path,
        dpi=400,
        facecolor=OCEAN,
        metadata={"Software": "fab-data-center-location-comparison"},
    )
    plt.close(fig)

    with Image.open(png_path) as image:
        png_dimensions = [image.width, image.height]
        # JPEG has no alpha channel. Composite explicitly onto the same white
        # background used by the figure, and retain the 400-dpi pixel grid.
        rgba = image.convert("RGBA")
        jpeg_image = Image.new("RGB", rgba.size, OCEAN)
        jpeg_image.paste(rgba, mask=rgba.getchannel("A"))
        jpeg_image.save(
            jpeg_path,
            format="JPEG",
            quality=95,
            subsampling=0,
            optimize=True,
            dpi=(400, 400),
        )
    return {
        "projection": "Equal Earth (ESRI:54035)",
        "figure_inches": [7.10, 2.82],
        "png_dimensions_px": png_dimensions,
        "font_family": family,
        "font_fallback_used": family != "Source Sans Pro",
        "registered_fonts": fonts,
        "outputs": {
            "pdf": {
                "path": relative_or_absolute(pdf_path),
                "sha256": file_sha256(pdf_path),
                "bytes": pdf_path.stat().st_size,
            },
            "svg": {
                "path": relative_or_absolute(svg_path),
                "sha256": file_sha256(svg_path),
                "bytes": svg_path.stat().st_size,
            },
            "png": {
                "path": relative_or_absolute(png_path),
                "sha256": file_sha256(png_path),
                "bytes": png_path.stat().st_size,
            },
            "jpeg": {
                "path": relative_or_absolute(jpeg_path),
                "sha256": file_sha256(jpeg_path),
                "bytes": jpeg_path.stat().st_size,
                "dimensions_px": png_dimensions,
                "quality": 95,
                "chroma_subsampling": "4:4:4",
            },
        },
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build(
    atlas_path: Path = DEFAULT_ATLAS,
    epoch_csv_path: Path = DEFAULT_EPOCH_CSV,
    epoch_map_html_path: Path = DEFAULT_EPOCH_MAP_HTML,
    countries_path: Path = DEFAULT_COUNTRIES,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    derived_root: Path = DEFAULT_DERIVED_ROOT,
    epoch_coordinates_path: Path | None = DEFAULT_EPOCH_COORDINATES,
) -> dict[str, Any]:
    atlas_path = rooted(atlas_path)
    countries_path = rooted(countries_path)
    output_root = rooted(output_root)
    derived_root = rooted(derived_root)

    atlas, fabs = load_atlas_fabs(atlas_path)
    if epoch_coordinates_path is None:
        epoch_csv_path = rooted(epoch_csv_path)
        epoch_map_html_path = rooted(epoch_map_html_path)
        data_centers = load_epoch_data_centers(epoch_csv_path, epoch_map_html_path)
        epoch_input_mode = "official_csv_and_archived_map_replay"
        coordinate_method = (
            "exact-name join from the official Epoch AI CSV to the official "
            "interactive map's embedded lngLat pair; no third-party geocoding "
            "or country-centroid substitution"
        )
        epoch_inputs = {
            "epoch_csv": {
                "path": relative_or_absolute(epoch_csv_path),
                "sha256": file_sha256(epoch_csv_path),
            },
            "epoch_map_html": {
                "path": relative_or_absolute(epoch_map_html_path),
                "sha256": file_sha256(epoch_map_html_path),
            },
        }
    else:
        epoch_coordinates_path = rooted(epoch_coordinates_path)
        data_centers = load_epoch_coordinate_csv(epoch_coordinates_path)
        epoch_input_mode = "derived_coordinate_csv"
        coordinate_method = (
            "public-safe replay from the derived coordinate CSV produced by the "
            "strict official CSV/map exact-name join; no webpage snapshot is read "
            "at render time"
        )
        epoch_inputs = {
            "epoch_coordinate_csv": {
                "path": relative_or_absolute(epoch_coordinates_path),
                "sha256": file_sha256(epoch_coordinates_path),
                "upstream_data_url": EPOCH_DOWNLOAD_URL,
                "upstream_map_url": EPOCH_MAP_URL,
                "derivation": "strict exact-name join of the official Epoch AI CSV to official interactive-map lngLat records",
            }
        }
    countries = json.loads(countries_path.read_text(encoding="utf-8"))
    write_csv(derived_root / ATLAS_LOCATIONS_NAME, fabs)
    epoch_derived_path = derived_root / EPOCH_LOCATIONS_NAME
    if (
        epoch_coordinates_path is None
        or epoch_coordinates_path.resolve() != epoch_derived_path.resolve()
    ):
        write_csv(epoch_derived_path, data_centers)
    figure = render_figure(atlas, fabs, data_centers, countries, output_root)

    country_counts = dict(sorted(Counter(row["country"] for row in data_centers).items()))
    fab_lifecycle_counts = dict(
        sorted(Counter(row["lifecycle_display_group"] for row in fabs).items())
    )
    status_counts = dict(
        sorted(Counter(row["status_from_epoch_map"] for row in data_centers).items())
    )
    manifest = {
        "schema": "fab-data-center-location-comparison",
        "status": "PASS",
        "created_date": "2026-08-25",
        "cohorts": {
            "atlas_fabs": {
                "record_count": len(fabs),
                "rule": "record_unit_type equals physical_front_end_campus and a complete source-bound WGS84 coordinate pair is present",
                "source_snapshot_date": atlas["snapshot_date"],
                "figure_retrieval_date": FIGURE_RETRIEVAL_DATE,
                "lifecycle_display_group_counts": fab_lifecycle_counts,
                "lifecycle_display_group_method": "Aggregation of each physical campus's Atlas lifecycle_status after the August 25, 2026 evidence review. Operating includes operating/ramp and operating-with-expansion records; commissioning and pilot remain separate. Any future indeterminate record maps to status_uncertain rather than being forced into operating or construction.",
            },
            "epoch_ai_data_centers": {
                "record_count": len(data_centers),
                "country_counts": country_counts,
                "status_counts_from_epoch_map": status_counts,
                "blank_address_count": sum(not row["address"].strip() for row in data_centers),
                "coordinate_input_mode": epoch_input_mode,
                "coordinate_method": coordinate_method,
                "update_and_access_date": "2026-08-25",
                "data_url": EPOCH_DATA_URL,
                "download_url": EPOCH_DOWNLOAD_URL,
                "map_url": EPOCH_MAP_URL,
                "license": "Creative Commons Attribution 4.0",
                "license_url": EPOCH_LICENSE_URL,
            },
        },
        "inputs": {
            "atlas": {
                "path": relative_or_absolute(atlas_path),
                "sha256": file_sha256(atlas_path),
            },
            **epoch_inputs,
            "base_geography": {
                "path": relative_or_absolute(countries_path),
                "sha256": file_sha256(countries_path),
                "source": "Natural Earth 1:110m admin-0 countries",
                "source_url": NATURAL_EARTH_URL,
                "rights": "public domain",
            },
        },
        "derived_tables": {
            "atlas_fabs": {
                "path": relative_or_absolute(derived_root / ATLAS_LOCATIONS_NAME),
                "sha256": file_sha256(derived_root / ATLAS_LOCATIONS_NAME),
            },
            "epoch_ai_data_centers": {
                "path": relative_or_absolute(epoch_derived_path),
                "sha256": file_sha256(epoch_derived_path),
            },
        },
        "figure": figure,
        "interpretation_limits": [
            "Each marker represents one database record, not a surveyed footprint.",
            "Marker size does not encode fab output, campus area, data-center compute, power, or operating status.",
            "Neither dataset is guaranteed to provide a complete global census.",
            "Epoch AI states that its current coverage is predominantly United States-based and includes qualifying planned sites under construction.",
        ],
    }
    manifest_path = output_root / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "fab_count": len(fabs),
                "epoch_data_center_count": len(data_centers),
                "pdf": figure["outputs"]["pdf"]["path"],
            },
            sort_keys=True,
        )
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--epoch-csv", type=Path, default=DEFAULT_EPOCH_CSV)
    parser.add_argument("--epoch-map-html", type=Path, default=DEFAULT_EPOCH_MAP_HTML)
    parser.add_argument(
        "--epoch-coordinates",
        type=Path,
        default=DEFAULT_EPOCH_COORDINATES,
        help=(
            "public-safe derived Epoch coordinate CSV; when supplied, the official "
            "CSV and archived map HTML are not read"
        ),
    )
    parser.add_argument("--countries", type=Path, default=DEFAULT_COUNTRIES)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--derived-root", type=Path, default=DEFAULT_DERIVED_ROOT)
    args = parser.parse_args()
    build(
        atlas_path=args.atlas,
        epoch_csv_path=args.epoch_csv,
        epoch_map_html_path=args.epoch_map_html,
        countries_path=args.countries,
        output_root=args.output_root,
        derived_root=args.derived_root,
        epoch_coordinates_path=args.epoch_coordinates,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
