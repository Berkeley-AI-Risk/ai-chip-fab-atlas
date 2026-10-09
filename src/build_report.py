#!/usr/bin/env python3
"""Build the one-page-per-campus AI Chip Fab Atlas report source."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = Path("data/atlas.json")
DEFAULT_CATALOGUE_CONCORDANCE = Path("data/catalogue-concordance.json")
DEFAULT_FRAGMENT = Path("report/campus-profiles.tex")
LOCATOR_ROOT = Path("figures/campus-locators")
OVERVIEW_MAP = LOCATOR_ROOT / "all-located-fabs-world-map.png"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import report_helpers as detailed


# A release build must include every campus plate. ``--preview`` allows an
# image-free draft from a public checkout, which does not include the plates.
ALLOW_MISSING_PLATES = False

# (path prefix, bottom trim, top trim). Current publication plates have no
# embedded header or footer that must be trimmed.
IMAGERY_TRIMS = (
    ("assets/campus-imagery/", "0bp", "0bp"),
)


# Reader order is deliberately geographic rather than inherited from the
# internal record IDs.  Within each country, operators stay together and
# operating campuses precede planned campuses where possible.
PUBLICATION_ORDER = (
    # Taiwan
    "AIFAB-025", "AIFAB-010", "AIFAB-001", "AIFAB-002", "AIFAB-004", "AIFAB-005",
    # South Korea
    "AIFAB-012", "AIFAB-008", "AIFAB-007",
    # Japan
    "AIFAB-018", "AIFAB-022",
    # China
    "AIFAB-023", "AIFAB-009", "AIFAB-029", "AIFAB-028", "AIFAB-030", "AIFAB-031",
    "AIFAB-021", "AIFAB-032",
    # United States
    "AIFAB-006", "AIFAB-013", "AIFAB-014", "AIFAB-027", "AIFAB-011", "AIFAB-019",
    "AIFAB-003",
    # Europe and Israel
    "AIFAB-026", "AIFAB-024", "AIFAB-015", "AIFAB-016",
    # India
    "AIFAB-033",
)


# Campuses whose opening sentence attributes a statement to the operator: cite
# only the operator's own sources there.  Independent reporting stays cited on
# the capability line, where the independently reported claim appears.
FIRST_PARTY_RATIONALE = {"AIFAB-007", "AIFAB-008"}


RATIONALE_OVERRIDES = {
    "AIFAB-003": (
        "TSMC identifies the Phoenix campus, where Fab 1 is in N4 high-volume "
        "production and additional fabs are being built for N3, N2, and A16."
    ),
    "AIFAB-006": (
        "GlobalFoundries identifies Malta/Fab 8 as an operating manufacturing site "
        "with current production and an expansion under way."
    ),
    "AIFAB-001": (
        "TSMC identifies Fab 15B as an operating manufacturing campus."
    ),
    "AIFAB-002": (
        "TSMC identifies Fab 18 and its history of N5, N4, and N3 production. These "
        "processes are suitable for advanced AI chips."
    ),
    "AIFAB-004": (
        "TSMC identifies Fab 20 as an operating N2 campus whose commercial "
        "production began in 2025. TSMC also describes a multi-phase ramp and "
        "expansion at Hsinchu supported by smartphone, high-performance-computing, "
        "and AI demand."
    ),
    "AIFAB-005": (
        "TSMC identifies Fab 22 as an operating N2 campus whose commercial "
        "production began in 2025. Official sources support Phases 1--5 "
        "planned and a multi-phase production ramp, with expansion continuing."
    ),
    "AIFAB-007": "Samsung identifies Pyeongtaek as an advanced foundry campus.",
    "AIFAB-008": (
        "Samsung's site materials identify Hwaseong and its 10 nm through 3 nm processes."
    ),
    "AIFAB-009": (
        "A planning record places SN1/SN2 on the Zhangjiang Road block that also holds "
        "SMIC's Shanghai 200 mm and 300 mm fabs."
    ),
    "AIFAB-010": (
        "TSMC identifies Fab 14B as a distinct manufacturing site and documented "
        "12/16 nm wafer production there."
    ),
    "AIFAB-011": (
        "Samsung identifies Austin as an operating campus with processes from 65 nm "
        "through 14 nm."
    ),
    "AIFAB-012": (
        "Samsung identifies Giheung as a manufacturing campus with processes through 8 nm."
    ),
    "AIFAB-013": (
        "Intel identifies Intel 7 and Intel 18A high-volume manufacturing at Ocotillo; "
        "Fab 52 is operating while Fab 62 and other expansion work continue."
    ),
    "AIFAB-014": (
        "Intel identifies Intel 18A high-volume manufacturing and next-node research "
        "and development at Gordon Moore Park."
    ),
    "AIFAB-015": (
        "Intel identifies Fab 24 and Fab 34 on one Leixlip campus, with Intel 4 and "
        "Intel 3 high-volume manufacturing and a capacity expansion under way."
    ),
    "AIFAB-016": (
        "Intel identifies Fab 28 as the operating Intel 7 facility at Kiryat Gat. "
        "Intel lists its Israel expansion as delayed or cancelled; that Kiryat Gat "
        "expansion, reported as Fab 38 and paused since mid-2024, is not counted "
        "separately."
    ),
    "AIFAB-018": (
        "TSMC describes Fab 1 and Fab 2 as parts of one Kumamoto campus; its 20-F "
        "names JASM's manufacturing entity Fab 23."
    ),
    "AIFAB-019": (
        "Samsung describes Taylor Fab 1 as preparing to begin operations in 2026, "
        "with 2 nm mass production targeted for 2027; Fab 2 is a later construction phase."
    ),
    "AIFAB-021": "Huali identifies Fab 6 as an operating manufacturing campus.",
    "AIFAB-022": (
        "Rapidus identifies IIM-1 as an operating 2 nm GAA pilot and prototyping "
        "site. Commercial mass production remains planned for 2027."
    ),
    "AIFAB-023": (
        "TSMC identifies Fab 16 as an operating campus whose most advanced "
        "volume-production technology is 16 nm. TSMC has also announced a 28 nm "
        "capacity expansion at the campus."
    ),
    "AIFAB-024": (
        "TSMC and ESMC identify this separate campus as under construction and planned "
        "for 16/12 nm production, primarily for automotive and industrial customers."
    ),
    "AIFAB-025": (
        "TSMC identifies Fab 12B as an operating 300 mm manufacturing site."
    ),
    "AIFAB-026": (
        "GlobalFoundries identifies Dresden as an operating high-volume manufacturing "
        "campus that makes 22FDX chips; an expansion is under construction."
    ),
    "AIFAB-027": (
        "Intel identifies this as a leading-edge campus with two fab modules under "
        "construction. It set 2030--2032 module dates in February 2025, then slowed "
        "work further. The Columbus Dispatch reported that Intel gave a firmer "
        "timeline in a 2026 state report; June 2026 reporting still listed "
        "2030--2032 operations."
    ),
    "AIFAB-028": (
        "Exact-campus environmental records identify 12-inch fabrication at 28 nm and "
        "larger process nodes and report production on all 365 days of 2024."
    ),
    "AIFAB-029": (
        "Public sources identify the Pingshan campus as an operating mature-node "
        "production site."
    ),
    "AIFAB-030": (
        "A government inspection records commissioning in December 2023; SMIC's 2024 "
        "interim report counts this Lingang fab among its operating fabs."
    ),
    "AIFAB-031": (
        "SMIC filings separately identify the Xiqing entity and support production "
        "capability, but the reviewed evidence does not establish current production at "
        "this campus."
    ),
    "AIFAB-032": (
        "Government and regulatory records describe Fab 7 and Fab 9 as operating "
        "phases within one continuous Wuxi production base."
    ),
    "AIFAB-033": (
        "Official Tata sources identify the fab as under construction and name "
        "high-performance computing and AI among its intended markets. It is included "
        "because of that stated market focus, even though its most advanced planned "
        "process is 28 nm."
    ),
}


CAPABILITY_OVERRIDES = {
    "AIFAB-007": (
        "Advanced-node S5 and S6 lines; Samsung's 2020 release planned EUV "
        "5 nm-and-below production; 4 nm output on S5 is independently reported"
    ),
    "AIFAB-018": (
        "Fab 1 (TSMC's Fab 23) is operating, with 28 nm its most advanced volume "
        "node at end-2025; TSMC says the two-fab site plans to offer 40, 22/28, "
        "12/16, 6/7, and 3 nm, with 3 nm for Fab 2"
    ),
    "AIFAB-019": "Fab 1 planned for 2 nm",
    "AIFAB-021": "28/22 nm production; independently reported 7 nm development",
    "AIFAB-004": (
        "Operating 12-inch fab; N2 is its most advanced volume-production technology; "
        "multi-phase ramp and expansion continue"
    ),
    "AIFAB-005": (
        "Operating 12-inch fab; N2 is its most advanced volume-production technology; "
        "Phases 1--5 are planned and a multi-phase production ramp is under way"
    ),
    "AIFAB-009": "14 nm at SN1; 7 nm-class (N+2) at SN2",
    "AIFAB-022": (
        "Operating 2 nm GAA pilot/prototyping line; commercial mass production planned "
        "for 2027"
    ),
    "AIFAB-023": (
        "Operating campus whose most advanced volume-production technology is 16 nm; "
        "28 nm capacity expansion also announced"
    ),
    "AIFAB-027": (
        "Two leading-edge fabs under slowed construction; the CHIPS award record lists "
        "Intel 14A and future nodes for the campus."
    ),
    "AIFAB-033": (
        "Planned 300 mm fab with a 28/40/55/90/110 nm portfolio; 50,000 wafers/month "
        "is the planned ultimate maximum, while an environmental-clearance record "
        "lists 32,000 IC wafers/month"
    ),
    "AIFAB-025": (
        "Operating 300 mm manufacturing; 40 nm was the most advanced volume-production "
        "technology reported for Fab 12 at year-end 2025"
    ),
    "AIFAB-028": "Operating 12-inch manufacturing at 28 nm and larger process nodes",
    "AIFAB-030": "Operating 12-inch line planned for 28 nm and larger processes",
    "AIFAB-031": (
        "Planned 28--180 nm line; the reviewed evidence supports capability but does not "
        "establish current production"
    ),
    "AIFAB-032": (
        "One continuous campus containing operating Fab 7 and Fab 9; 90 nm through "
        "65/55 nm specialty capability, with 40 nm also documented for Fab 9"
    ),
}


STATUS_LABELS = {
    "operating": "Operating",
    "operating_with_expansion": "Operating; expansion under construction",
    "operating_ramp": "Beginning production",
    "commissioning_or_initial_operations": "Preparing to open or beginning operations",
    "operating_with_7nm_tapeout": (
        "Operating; a single source reports a 7 nm tapeout on Huali's line"
    ),
    "pilot_line": "Pilot production",
    "under_construction": "Under construction",
    "under_construction_preoperational": "Under construction; pre-operational",
    "under_construction_slowed": "Under construction; schedule delayed",
    "operating_with_ramp": "Operating; production increasing",
    "operating_or_ramp_unresolved": (
        "Status uncertain: operating or in initial production"
    ),
    "construction_or_ramp_unresolved": (
        "Status uncertain: construction or production"
    ),
    "status_uncertain": "Status uncertain in the public sources reviewed",
}


STATUS_LABEL_OVERRIDES = {
    "AIFAB-004": "Operating; production ramp and phased expansion continuing",
    "AIFAB-005": "Operating; production ramp and phased expansion continuing",
    "AIFAB-022": "Pilot and prototyping line operating",
}


RELATIONSHIP_OVERRIDES = {
    ("AIFAB-003", "Blackwell"): {
        "claim": "NVIDIA states that TSMC is producing Blackwell chips at its Arizona campus.",
        "status": "Officially confirmed production",
        "limits": (
            "The source confirms some Blackwell production in Arizona but does not state "
            "what share is made there or whether every Blackwell version is included."
        ),
    },
    ("AIFAB-003", "AI5"): {
        "claim": (
            "In July 2025, Tesla's CEO said TSMC would make AI5 first in Taiwan and then "
            "in Arizona."
        ),
        "status": "Announced production plan",
        "limits": (
            "A stated plan; the sources reviewed report no process, start date, share, or "
            "output for Arizona. Musk said in April 2026 that AI5 would first serve Optimus "
            "and Tesla's supercomputer clusters."
        ),
    },
    ("AIFAB-019", "AI6"): {
        "claim": (
            "Tesla's CEO said in January 2026 that AI6 is for Optimus and data centers and "
            "in April 2026 that it would use Samsung's 2 nm fab in Texas."
        ),
        "status": "Announced production plan",
        "limits": "A plan: a July 2026 report put mass production no earlier than late 2027.",
    },
    ("AIFAB-019", "AI5"): {
        "claim": (
            "In October 2025, Tesla's CEO said Samsung would make AI5 in Texas; in July "
            "2026, a Samsung Foundry engineer's post placed it at Taylor on 2 nm."
        ),
        "status": "Announced production plan; tape-out reported",
        "limits": (
            "A plan: the post was later deleted, and Musk has pointed to mass production "
            "by mid-2027."
        ),
    },
    ("AIFAB-006", "CloudBlazer T10"): {
        "claim": (
            "GlobalFoundries scheduled CloudBlazer production at Fab 8 for early 2020, "
            "and Enflame later confirmed 12 nm production and commercial use."
        ),
        "status": "Announced production plan; later production confirmed without a named campus",
        "limits": "No reviewed source names the campus where that production took place.",
    },
    ("AIFAB-007", "Groq 3 LPU"): {
        "claim": (
            "NVIDIA states that Groq 3 LPX is in full production, and Samsung identifies "
            "itself as the LPU's manufacturing partner. Independent reporting places 4 nm "
            "production on the S5 line at Pyeongtaek P2."
        ),
        "status": "Full production; exact campus independently reported",
        "limits": (
            "The first-party sources reviewed do not name the node or campus or state "
            "what share is made at Pyeongtaek."
        ),
    },
    ("AIFAB-009", "Ascend 910B"): {
        "claim": (
            "April 2025 congressional testimony reports SMIC producing Ascend 910B dies "
            "and calls SN2 China's only active 7 nm line."
        ),
        "status": "Independently reported production",
        "limits": (
            "The testimony links the dies to SN2 only by combining these statements; it "
            "also cites officials as saying TSMC made over 2 million 910B dies. The "
            "sources reviewed do not confirm production after April 2025."
        ),
    },
    ("AIFAB-013", "Archer accelerator in Atlas system"): {
        "claim": (
            "EE Times reports that Positron's Atlas system is built on Altera Agilex-7M "
            "FPGAs made by Intel in Chandler, Arizona; Business Insider also places "
            "Positron's chips in Chandler."
        ),
        "status": "Current production independently reported (city-level)",
        "limits": (
            "The campus is inferred: Intel's high-volume Chandler fabs are on Ocotillo. "
            "Intel and Altera do not name the fab or give a node or share. The chip is "
            "Altera's general-purpose FPGA, not a Positron design."
        ),
    },
    ("AIFAB-021", "unnamed 7 nm GPU tapeout design"): {
        "claim": (
            "Reuters reports (one source) that Biren is using Huali's 7 nm line for "
            "tapeout and, separately, places Huali's 7 nm work at Fab 6."
        ),
        "status": "Reported tapeout (single source)",
        "limits": (
            "Reuters does not name the chip or its market, and this stage precedes mass "
            "production."
        ),
    },
}


# A handful of legacy coordinate records carried hostnames or internal labels
# rather than publication-ready citation metadata.  The registry values remain
# unchanged; these display-only corrections are grounded in the linked records.
SOURCE_DISPLAY_OVERRIDES = {
    "AISRC-0179": {
        "publisher": "Google Maps",
        "title": "TSMC Arizona campus",
    },
    "AISRC-0180": {
        "publisher": "Hsinchu Science Park Bureau",
        "title": "Baoshan Phase 2 expansion project: second tender",
    },
    "AICOORD-20260823-002": {
        "title": (
            "Public report reproducing the four-road description for Tianjin "
            "land parcel G2022-03"
        ),
    },
    # Headlines pdfLaTeX cannot typeset (Korean, Chinese): print an English
    # rendering or a romanization with a bracketed gloss. The registry keeps the
    # original-language titles.
    "AISRC-0234": {
        "title": (
            "[Samsung Electronics' bold gamble: Can the new Galaxy take Apple down a peg?]"
        ),
        "title_note": "In Korean.",
    },
    "AISRC-0213": {
        "title": "Quanguo shoupi! Ruxuan!",
        "title_note": "[First national batch! Selected!] In Chinese.",
    },
    "AISRC-0242": {
        "title": (
            "[Enflame Technology releases second-generation AI chip, volume production "
            "by year-end]"
        ),
        "title_note": "In Chinese.",
    },
}


class ConciseAtlasError(RuntimeError):
    """Raised when the fixed concise-page evidence contract cannot be met."""


def rooted(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def image_trims(render_path: str) -> tuple[str, str]:
    normalized = Path(render_path).as_posix()
    matches = [
        (bottom, top)
        for prefix, bottom, top in IMAGERY_TRIMS
        if normalized.startswith(prefix)
    ]
    if len(matches) != 1:
        raise ConciseAtlasError(f"unknown or ambiguous imagery layout: {render_path}")
    return matches[0]


def physical_sites(release: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    sites = [
        site
        for site in release["sites"]
        if site["record_unit_type"] == "physical_front_end_campus"
    ]
    if len(sites) != 31:
        raise ConciseAtlasError(f"expected 31 physical campuses, found {len(sites)}")
    ids = [site["campus_id"] for site in sites]
    if len(set(ids)) != len(ids):
        raise ConciseAtlasError("duplicate physical-campus identifier")
    if set(ids) != set(PUBLICATION_ORDER):
        raise ConciseAtlasError("publication order does not match the physical-campus set")
    by_id = {site["campus_id"]: site for site in sites}
    return [by_id[site_id] for site_id in PUBLICATION_ORDER]


def load_catalogue_concordance(
    path: Path,
    atlas_path: Path,
    sites: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    path = rooted(path)
    if not path.is_file():
        raise ConciseAtlasError(f"missing catalogue concordance: {path}")
    concordance = json.loads(path.read_text(encoding="utf-8"))
    bound_hash = concordance.get("atlas", {}).get("sha256")
    actual_hash = sha256(atlas_path.read_bytes()).hexdigest()
    if bound_hash != actual_hash:
        raise ConciseAtlasError(
            "catalogue concordance is not bound to the canonical Atlas hash"
        )

    campus_ids = {site["campus_id"] for site in sites}
    campus_matches = concordance.get("campus_matches", {})
    if set(campus_matches) != campus_ids:
        raise ConciseAtlasError(
            "catalogue concordance does not cover the complete physical-campus set"
        )
    catalogues = concordance.get("catalogues", {})
    if set(concordance.get("display_order", [])) != set(catalogues):
        raise ConciseAtlasError("catalogue display order does not match catalogue set")

    exact_classes = {"same_complex", "module_within_complex"}
    exact_campuses: dict[str, set[str]] = {key: set() for key in catalogues}
    coarse_campuses: dict[str, set[str]] = {key: set() for key in catalogues}
    exact_records: dict[str, int] = {key: 0 for key in catalogues}
    for campus_id, matches in campus_matches.items():
        for match in matches:
            catalogue_id = match.get("catalogue_id")
            if catalogue_id not in catalogues:
                raise ConciseAtlasError(
                    f"{campus_id}: unknown catalogue {catalogue_id!r}"
                )
            if not match.get("url") or not match.get("external_id"):
                raise ConciseAtlasError(
                    f"{campus_id}: incomplete catalogue-match provenance"
                )
            match_class = match.get("match_class")
            if match.get("display_on_profile") and match_class not in exact_classes:
                raise ConciseAtlasError(
                    f"{campus_id}: non-exact catalogue match marked for display"
                )
            if match_class in exact_classes:
                exact_campuses[catalogue_id].add(campus_id)
                exact_records[catalogue_id] += 1
            elif match_class == "coarse_locality":
                coarse_campuses[catalogue_id].add(campus_id)

    for catalogue_id, catalogue in catalogues.items():
        expected = catalogue["audit_result"]
        if len(exact_campuses[catalogue_id]) != expected["exact_campus_count"]:
            raise ConciseAtlasError(
                f"{catalogue_id}: exact-campus count does not match audit result"
            )
        if len(coarse_campuses[catalogue_id]) != expected["coarse_locality_count"]:
            raise ConciseAtlasError(
                f"{catalogue_id}: coarse-match count does not match audit result"
            )
        expected_records = expected.get("exact_external_record_count")
        if expected_records is not None and exact_records[catalogue_id] != expected_records:
            raise ConciseAtlasError(
                f"{catalogue_id}: external-record count does not match audit result"
            )
    return concordance


def place_label(location: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for value in (location.get("city"), location.get("admin1"), location.get("country_code")):
        if value and value not in parts:
            parts.append(str(value))
    return ", ".join(parts) or "campus-level location unresolved"


def locator_path(
    site: Mapping[str, Any], locator_root: Path = LOCATOR_ROOT
) -> Path | None:
    location = site["location"]
    if location.get("latitude_wgs84") is None or location.get("longitude_wgs84") is None:
        return None
    path = Path(locator_root) / f"{site['campus_id'].lower()}-world-locator.png"
    if not rooted(path).exists():
        raise ConciseAtlasError(
            f"missing locator for {site['campus_id']}; run the locator renderer"
        )
    return path


def first_seen_sources(
    groups: Iterable[Iterable[Mapping[str, str]]],
) -> list[Mapping[str, str]]:
    result: list[Mapping[str, str]] = []
    seen: set[str] = set()
    for group in groups:
        for source in group:
            source_id = source["source_id"]
            if source_id not in seen:
                seen.add(source_id)
                result.append(source)
    return result


def relationship_sources(relationship: Mapping[str, Any]) -> list[Mapping[str, str]]:
    return first_seen_sources(relationship["citations"].values())


def compact_sources(site: Mapping[str, Any]) -> list[Mapping[str, str]]:
    groups: list[Iterable[Mapping[str, str]]] = []
    coordinate = site["location"].get("coordinate_source")
    if coordinate:
        groups.append([coordinate])
    groups.extend(
        [
            site["citations"]["site_identity"],
            site["citations"]["site_capability"],
        ]
    )
    for relationship in site["exact_campus_allocations"]:
        groups.extend(relationship["citations"].values())
    imagery_sources = site.get("imagery_citation_sources", [])
    if imagery_sources:
        groups.append(imagery_sources)
    return first_seen_sources(groups)


def citation_numbers(sources: Sequence[Mapping[str, str]]) -> dict[str, int]:
    return {source["source_id"]: index for index, source in enumerate(sources, start=1)}


def citation_url_arg(url: str) -> str:
    """Make a URL safe in a TeX macro argument, including percent and hash signs."""
    if "}" in url:
        raise ConciseAtlasError("unsupported closing brace in citation URL")
    # A literal percent begins a TeX comment and a literal hash is a parameter
    # marker even inside ``\detokenize`` while TeX is collecting a macro
    # argument. Split around both characters and insert escaped forms between
    # safe detokenized spans.
    pieces = re.split(r"([%#])", url)
    result = r"\detokenize{" + pieces[0] + "}"
    for marker, part in zip(pieces[1::2], pieces[2::2]):
        result += (r"\%" if marker == "%" else r"\#") + r"\detokenize{" + part + "}"
    return result


def citation_marks(
    citations: Sequence[Mapping[str, str]], numbers: Mapping[str, int]
) -> str:
    marks: list[str] = []
    ordered = sorted(
        first_seen_sources([citations]), key=lambda source: numbers[source["source_id"]]
    )
    for source in ordered:
        source_id = source["source_id"]
        if source_id not in numbers:
            raise ConciseAtlasError(f"source {source_id} is missing from the page source list")
        marks.append(
            rf"\href{{{citation_url_arg(source['url'])}}}"
            rf"{{\textcolor{{accent}}{{{numbers[source_id]}}}}}"
        )
    # Chicago-style superscript note marks follow the punctuation directly.
    # ``\nobreak`` keeps the mark with the preceding text without inserting
    # the conspicuous extra space produced by the former leading ``~``.
    return r"\nobreak\textsuperscript{" + ",".join(marks) + "}"


MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def chicago_date(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d{4}", value):
        return value
    match = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", value)
    if match is None:
        raise ConciseAtlasError(f"unsupported citation date: {value!r}")
    year, month_text, day_text = match.groups()
    month = int(month_text)
    if month < 1 or month > 12:
        raise ConciseAtlasError(f"invalid citation month: {value!r}")
    if day_text is None:
        return f"{MONTHS[month - 1]} {year}"
    day = int(day_text)
    if day < 1 or day > 31:
        raise ConciseAtlasError(f"invalid citation day: {value!r}")
    return f"{MONTHS[month - 1]} {day}, {year}"


def source_display(source: Mapping[str, str]) -> dict[str, str]:
    result = dict(source)
    result.update(SOURCE_DISPLAY_OVERRIDES.get(source["source_id"], {}))
    return result


def chicago_source(source: Mapping[str, str], number: int) -> str:
    display = source_display(source)
    publisher = display["publisher"].strip().rstrip(". ")
    title = display["title"].strip().rstrip(". ")
    publication_date = display.get("publication_date", "").strip()
    archive_date = display.get("archive_date", "").strip()
    if publication_date:
        date_text = chicago_date(publication_date)
    elif archive_date:
        # An undated page cited through a web-archive capture: the capture
        # date, not the later access date, dates the evidence.
        date_text = "Archived " + chicago_date(archive_date)
    else:
        access_date = display.get("access_date", "").strip()
        if not access_date:
            raise ConciseAtlasError(f"source {source['source_id']} has no usable date")
        date_text = "Accessed " + chicago_date(access_date)
    # Translated or romanized titles carry a language note after the title.
    title_note = display.get("title_note", "").strip()
    title_end = "" if title.endswith(("?", "!")) else "."
    note_text = f" {detailed.tex(title_note)}" if title_note else ""
    return (
        # The thin space is nonbreaking, so a source number can move to the
        # next line with its publisher but can never be stranded by itself.
        rf"\textsuperscript{{{number}}}\,{detailed.tex(publisher)}. "
        rf"\href{{{citation_url_arg(display['url'])}}}"
        rf"{{\enquote{{{detailed.tex(title)}{title_end}}}}}{note_text} {detailed.tex(date_text)}"
    )


def satellite_panel(
    site: Mapping[str, Any],
    numbers: Mapping[str, int],
    side_evidence: Sequence[str] | None = None,
) -> list[str]:
    imagery = site.get("imagery", [])
    row = imagery[0] if imagery else None
    render_path = str(row.get("render_path") or "") if row else ""
    display = site.get("imagery_display", {})
    imagery_sources = site.get("imagery_citation_sources", [])
    native_resolution = row.get("native_resolution_m") if row else None
    high_resolution = (
        isinstance(native_resolution, (int, float))
        and float(native_resolution) < 5.0
    )
    image_width = r"0.68\textwidth" if high_resolution else r"0.56\textwidth"
    image_height = r"0.42\textheight" if high_resolution else r"0.32\textheight"
    lines = [
        r"\begin{minipage}[t]{\textwidth}",
        r"\raggedright",
    ]
    if row and render_path and rooted(Path(render_path)).exists():
        bottom_trim, top_trim = image_trims(render_path)
        figure_path = "../" + Path(render_path).as_posix()
        acquisition = str(row.get("acquisition_datetime_utc") or "not stated").split("T")[0]
        if display.get("caption"):
            caption = detailed.tex(str(display["caption"]))
        else:
            caption = (
                f"{row['sensor']}; {acquisition}; "
                f"{row.get('output_resolution_m') or 'unknown'} m grid; "
                f"{row.get('crop_side_km') or 'unknown'} km view."
            )
            caption = detailed.tex(caption)
        if imagery_sources:
            caption += citation_marks(imagery_sources, numbers)
        caption += r" Yellow cross: cited location point."
        if side_evidence is not None:
            # Use the same image-left, evidence-right composition on every rendered
            # campus profile.  The image-height cap controls the common printed plate
            # size; the right-only offset separates the caption and opening evidence
            # from the locator panel above without moving the image down.
            lines.extend(
                [
                    r"% Image-left evidence-right profile row",
                    r"\begin{minipage}[t]{0.64\textwidth}",
                    r"\vspace{0pt}\raggedright",
                    rf"\includegraphics[width=\linewidth,height={image_height},keepaspectratio,"
                    rf"trim=0 {bottom_trim} 0 {top_trim},clip]{{{figure_path}}}",
                    r"\end{minipage}",
                    r"\hfill",
                    r"\begin{minipage}[t]{0.32\textwidth}",
                    r"\vspace{0pt}\vspace{1.0em}\raggedright",
                    rf"{{\sffamily\scriptsize {caption}\par}}",
                    r"\medskip",
                    *side_evidence,
                    r"\end{minipage}",
                ]
            )
        else:
            lines.extend(
                [
                    r"\begin{center}",
                    rf"\begin{{minipage}}{{{image_width}}}",
                    r"\centering",
                    rf"\includegraphics[width=\linewidth,height={image_height},keepaspectratio,"
                    rf"trim=0 {bottom_trim} 0 {top_trim},clip]{{{figure_path}}}",
                    r"\par\smallskip",
                    rf"{{\raggedright\sffamily\scriptsize {caption}\par}}",
                    r"\end{minipage}",
                    r"\end{center}",
                ]
            )
    else:
        if side_evidence is not None:
            raise ConciseAtlasError("side-evidence layout requires a rendered image")
        if row and render_path and not ALLOW_MISSING_PLATES:
            raise ConciseAtlasError(
                f"missing campus plate {render_path}; add the plates or pass --preview"
            )
        if row:
            message = "Image omitted from this preview build; see the released Atlas PDF."
        else:
            message = (
                "We did not identify precise campus coordinates in the public sources "
                "reviewed, so this page does not show a satellite image."
            )
        lines.extend(
            [
                r"\begin{center}",
                rf"\begin{{minipage}}{{{image_width}}}",
                r"\centering",
                r"\fcolorbox{hairline}{softbg}{%",
                r"\parbox[c][0.20\textheight][c]{0.91\linewidth}{\centering",
                r"\sffamily\small\color{black!62} " + detailed.tex(message) + "}}",
                r"\end{minipage}",
                r"\end{center}",
            ]
        )
    lines.append(r"\end{minipage}")
    return lines


def summary_evidence(
    site: Mapping[str, Any],
    numbers: Mapping[str, int],
    rationale_sources: Sequence[Mapping[str, str]],
    capability: str,
) -> list[str]:
    return [
        rf"{{\footnotesize {detailed.tex(RATIONALE_OVERRIDES.get(site['campus_id'], site['inclusion_rationale']))}"
        rf"{citation_marks(rationale_sources, numbers)}\par}}",
        r"\medskip",
        rf"{{\footnotesize\textbf{{Documented wafer-fabrication capability:}} "
        rf"{detailed.tex(capability)}"
        rf"{citation_marks(site['citations']['site_capability'], numbers)}\par}}",
    ]


def coordinate_provenance(site: Mapping[str, Any]) -> str:
    location = site["location"]
    source = location["coordinate_source"]
    publisher = str(source.get("publisher") or "")
    precision = str(location.get("coordinate_precision") or "")
    if publisher == "U.S. Environmental Protection Agency":
        if precision == "epa_frs_representative_point_air_release_stack":
            return "Coordinates from an air-stack point in the cited U.S. EPA facility record."
        if precision == "epa_frs_representative_process_unit_point":
            return "Coordinates from a process-unit point in the cited U.S. EPA facility record."
        if precision == "epa_frs_address_matched_point_at_campus_edge":
            return "Coordinates from a cited U.S. EPA address-matched point on the road at the campus edge."
        return "Coordinates from a facility-center point in the cited U.S. EPA record."
    if publisher == "OpenStreetMap contributors":
        if precision == "approximate_planning_area_center":
            return (
                "Coordinates estimated from the cited OpenStreetMap "
                "planning-area feature."
            )
        return "Coordinates are the representative point returned for the cited OpenStreetMap feature."
    if publisher == "TSMC":
        return "Coordinates from TSMC's cited facilities listing."
    if publisher == "Executive Yuan, Republic of China (Taiwan)":
        return "Coordinates from the official site/event point in the cited government record."
    if publisher == "Hsinchu Science Park Bureau":
        return "Coordinates derived from the cited science-park project record."
    if publisher == "maps.app.goo.gl":
        return "Coordinates from the cited public map."
    if publisher == "pavo.sipa.gov.tw":
        return "Coordinates derived from the cited science-park source."
    url = str(source.get("url") or "")
    if url.startswith("https://epawebapp.epa.ie/"):
        return "Coordinates from the cited Irish EPA facility record."
    if url.startswith("https://www.gov.il/apps/sviva/"):
        return "Coordinates from the cited Israeli government facility record."
    if precision == "operator_reported_campus_center":
        return "Coordinates from the campus center in the cited operator document."
    if precision == "operator_linked_building_inside_official_campus":
        return (
            "Coordinates derived from a building point in the cited government "
            "planning record."
        )
    if precision == "official_four_road_parcel_center_estimate":
        return "Coordinates estimated from the parcel described in the cited source."
    if precision == "official_project_polygon_computed_centroid":
        return (
            "Coordinates computed from the project polygon in the cited government "
            "record."
        )
    if precision == "eia_project_center_converted_campus_link_unverified":
        return (
            "Converted (GCJ-02 assumed) from an SMIC Lingang project's environmental "
            "record, which does not tie the point to this campus."
        )
    if precision == "operator_linked_auxiliary_building_inside_official_campus":
        return (
            "Coordinates were converted from a public environmental record for an "
            "auxiliary building inside the officially documented campus."
        )
    if precision == "analyst_estimated_four_road_parcel_center":
        return "Coordinates estimate the center of the four-road parcel described in the cited sources."
    raise ConciseAtlasError(
        f"missing coordinate-provenance copy for {site['campus_id']}: "
        f"{publisher!r} / {precision!r}"
    )


def locator_panel(
    site: Mapping[str, Any],
    numbers: Mapping[str, int],
    locator_root: Path = LOCATOR_ROOT,
    width: str = r"0.27\textwidth",
) -> list[str]:
    location = site["location"]
    path = locator_path(site, locator_root)
    lines = [
        rf"\begin{{minipage}}[t]{{{width}}}",
        r"\raggedright",
        r"{\sffamily\bfseries\footnotesize World location}\par\smallskip",
    ]
    if path:
        source = location["coordinate_source"]
        lines.extend(
            [
                rf"\includegraphics[width=\linewidth,keepaspectratio]{{../{path.as_posix()}}}",
                r"\par\smallskip",
                rf"{{\sffamily\scriptsize Coordinates: "
                rf"{float(location['latitude_wgs84']):.3f}, "
                rf"{float(location['longitude_wgs84']):.3f}.\par}}",
                rf"{{\sffamily\scriptsize\color{{black!68}} "
                rf"{detailed.tex(coordinate_provenance(site))}"
                rf"{citation_marks([source], numbers)}\par}}",
            ]
        )
    else:
        lines.extend(
            [
                r"\fcolorbox{hairline}{softbg}{%",
                r"\parbox[c][0.10\textheight][c]{0.84\linewidth}{\centering",
                r"\sffamily\scriptsize\color{black!62} We did not identify precise "
                r"campus coordinates in the public sources reviewed, so no locator dot "
                r"is shown.}}",
            ]
        )
    lines.append(r"\end{minipage}")
    return lines


def exact_evidence(site: Mapping[str, Any], numbers: Mapping[str, int]) -> list[str]:
    allocations = site["exact_campus_allocations"]
    lines = [r"\medskip"]
    if not allocations:
        lines.extend(
            [
                r"{\footnotesize\textbf{Named data-center AI accelerators or programs:} None "
                r"identified in the sources reviewed.\par}",
            ]
        )
        return lines
    lines.extend(
        [
            r"{\footnotesize\textbf{Named data-center AI accelerators or programs:}\par}",
            r"\begin{itemize}[leftmargin=1.25em,itemsep=0.35em,topsep=0.15em,parsep=0pt]",
        ]
    )
    for relationship in allocations:
        product = relationship["product"]
        copy = RELATIONSHIP_OVERRIDES.get(
            (site["campus_id"], product["product_family"])
        )
        if copy is None:
            raise ConciseAtlasError(
                f"missing concise relationship copy for {site['campus_id']} / "
                f"{product['product_family']}"
            )
        citations = relationship_sources(relationship)
        lines.append(
            rf"\item {{\footnotesize\textbf{{{detailed.tex(product['vendor'])} --- "
            rf"{detailed.tex(product['product_family'])}.}} "
            rf"{detailed.tex(copy['claim'])}"
            rf"{citation_marks(citations, numbers)}\par "
            rf"{{\scriptsize\color{{black!62}}\textbf{{Limits of the evidence:}} "
            rf"{detailed.tex(copy['limits'])}\par}}}}"
        )
    lines.append(r"\end{itemize}")
    return lines


def sources_block(sources: Sequence[Mapping[str, str]]) -> list[str]:
    entries = [chicago_source(source, index) for index, source in enumerate(sources, start=1)]
    return [
        r"\medskip",
        r"{\sffamily\scriptsize\setlength{\emergencystretch}{1.5em}\textbf{Sources.} "
        + "; ".join(entries)
        + r".\par}",
    ]


def catalogue_note(
    site: Mapping[str, Any], concordance: Mapping[str, Any]
) -> list[str]:
    matches = concordance["campus_matches"][site["campus_id"]]
    displayed: dict[str, Mapping[str, Any]] = {}
    for match in matches:
        if match.get("display_on_profile"):
            displayed.setdefault(match["catalogue_id"], match)
    if not displayed:
        return []

    links: list[str] = []
    for catalogue_id in concordance["display_order"]:
        match = displayed.get(catalogue_id)
        if match is None:
            continue
        label = concordance["catalogues"][catalogue_id]["display_name"]
        links.append(
            rf"\href{{{citation_url_arg(match['url'])}}}"
            rf"{{{detailed.tex(label)}}}"
        )
    reviewed = detailed.tex(chicago_date(concordance["review_date"]))
    return [
        r"\smallskip",
        r"{\sffamily\scriptsize\color{black!62}\textbf{Other public catalogues "
        rf"(same campus; reviewed {reviewed}):}} "
        + "; ".join(links)
        + r".\par}",
    ]


def date_footer(
    evidence_cutoff_date: str,
    update_date: str | None = None,
    update_scope: str = "Location and imagery",
) -> str:
    evidence_text = detailed.tex(chicago_date(evidence_cutoff_date))
    if update_date and update_date != evidence_cutoff_date:
        update_text = detailed.tex(chicago_date(update_date))
        return (
            rf"{{\sffamily\scriptsize\color{{black!58}} Facility and product evidence "
            rf"reviewed through {evidence_text}. {detailed.tex(update_scope)} updated "
            rf"{update_text}.\par}}"
        )
    return (
        rf"{{\sffamily\scriptsize\color{{black!58}} Evidence reviewed through "
        rf"{evidence_text}.\par}}"
    )


def intro_page(
    sites: Sequence[Mapping[str, Any]],
    evidence_cutoff_date: str,
    concordance: Mapping[str, Any],
    locator_root: Path = LOCATOR_ROOT,
    update_date: str | None = None,
    update_scope: str = "Location and imagery",
    version: str | None = None,
    version_date: str | None = None,
) -> list[str]:
    mapped = [
        site
        for site in sites
        if site["location"].get("latitude_wgs84") is not None
        and site["location"].get("longitude_wgs84") is not None
    ]
    unresolved = [site for site in sites if site not in mapped]
    if (len(sites), len(mapped), len(unresolved)) not in {(31, 29, 2), (31, 31, 0)}:
        raise ConciseAtlasError("overview-page location coverage changed")
    overview_map = Path(locator_root) / OVERVIEW_MAP.name
    if not rooted(overview_map).exists():
        raise ConciseAtlasError("missing all-campus overview map; run the locator renderer")
    concordance_date = detailed.tex(chicago_date(concordance["review_date"]))
    lines = [
        r"\clearpage",
        r"% Atlas overview page",
        r"\markright{Atlas overview}",
        r"\noindent\begin{minipage}[t][0.90\textheight][t]{\textwidth}",
        r"{\raggedright\sffamily\bfseries\LARGE\color{accent} AI Chip Fab Atlas\par}",
        r"\smallskip",
        r"{\raggedright\sffamily\large\color{accent} Public-Evidence Atlas of "
        r"AI-Relevant Chip-Fabrication Campuses\par}",
    ]
    if version:
        version_text = f"Version {version}"
        if version_date:
            version_text += f" \u00b7 {chicago_date(version_date)}"
        lines.append(
            rf"{{\sffamily\small\color{{black!62}} {detailed.tex(version_text)}\par}}"
        )
    lines += [
        r"\medskip",
        r"{\small This atlas presents publicly available evidence about 31 "
        r"physical wafer-fabrication campuses that may matter for advanced AI chips. "
        r"We used two routes to identify campuses. First, we traced publicly documented "
        r"data-center AI processors and related manufacturing programs to plausible "
        r"production campuses. Second, to reduce omissions, we reviewed every publicly "
        r"identified operating logic campus at 16 nm or more advanced operated by a "
        r"foundry identified in the first step. We also included 11 older-node or "
        r"under-construction sites whose documented capabilities may matter for older or "
        r"future AI chips. Each continuous campus is counted once, even when it contains several "
        r"fab buildings or phases. "
        r"Campus profiles are ordered by region and country, then by operator; "
        r"operating campuses precede planned campuses within each group. The inventory "
        r"is not presented as exhaustive.\par}",
        r"\medskip",
        r"{\sffamily\footnotesize\textbf{Image marker.} The yellow cross marks the "
        r"cited location point listed on each profile. The image may be shifted to "
        r"show more of the campus, so the cross is not always centered.\par}",
        r"\smallskip",
        r"{\sffamily\scriptsize\color{black!62}\textbf{Other catalogues.} Some "
        r"profiles link to same-campus entries in four selected open catalogues "
        rf"reviewed {concordance_date}; this includes a named fab or module within "
        r"the same physical complex. These cross-references do not independently "
        r"establish capability or products, and a profile without a note may still "
        r"appear elsewhere.\par}",
        r"\bigskip",
        rf"\includegraphics[width=\linewidth,keepaspectratio]{{../{overview_map.as_posix()}}}",
    ]
    lines.extend(
        [
            r"\vfill",
            date_footer(evidence_cutoff_date, update_date, update_scope),
            r"\end{minipage}",
        ]
    )
    return lines


def site_page(
    site: Mapping[str, Any],
    evidence_cutoff_date: str,
    concordance: Mapping[str, Any],
    locator_root: Path = LOCATOR_ROOT,
    update_date: str | None = None,
    update_scope: str = "Location and imagery",
) -> list[str]:
    location = site["location"]
    sources = compact_sources(site)
    numbers = citation_numbers(sources)
    capability_sources = site["citations"]["site_capability"]
    if site["campus_id"] in FIRST_PARTY_RATIONALE:
        capability_sources = [
            source
            for source in capability_sources
            if source.get("source_class") != "credible_independent_reporting"
        ]
    rationale_sources = first_seen_sources(
        [site["citations"]["site_identity"], capability_sources]
    )
    capability = CAPABILITY_OVERRIDES.get(
        site["campus_id"],
        site["public_front_end_capability"] or "Not resolved in the public sources reviewed",
    )
    opening_evidence = summary_evidence(
        site, numbers, rationale_sources, capability
    )
    imagery = site.get("imagery", [])
    row = imagery[0] if imagery else None
    render_path = str(row.get("render_path") or "") if row else ""
    rendered_plate = bool(
        row and render_path and rooted(Path(render_path)).exists()
    )
    lines = [
        r"\clearpage",
        rf"% Campus profile {site['campus_id']}",
        rf"\markright{{{detailed.tex(site['campus_name'])}}}",
        r"\noindent\begin{minipage}[t][0.90\textheight][t]{\textwidth}",
        r"\noindent\begin{minipage}[t]{0.69\textwidth}",
        r"\raggedright",
        rf"{{\sffamily\bfseries\Large\color{{accent}} "
        rf"{detailed.tex(site['campus_name'])}\par}}",
        r"\smallskip",
        rf"{{\sffamily\small\textbf{{Operator:}} {detailed.tex(site['operator'])}\quad "
        rf"\textbf{{Location:}} {detailed.tex(place_label(location))}\par}}",
        rf"{{\sffamily\footnotesize\color{{black!68}}\textbf{{Facility status:}} "
        rf"{detailed.tex(STATUS_LABEL_OVERRIDES.get(site['campus_id'], STATUS_LABELS.get(site['lifecycle_status'], detailed.prose_label(site['lifecycle_status']))))} "
        rf"(as of {detailed.tex(site['lifecycle_as_of_date'] or 'not stated')})\par}}",
        r"\end{minipage}",
        r"\hfill",
        *locator_panel(site, numbers, locator_root),
        r"\par\vspace{0.9em}",
        r"\noindent",
        *satellite_panel(
            site, numbers, opening_evidence if rendered_plate else None
        ),
        r"\par\vspace{0.65em}" if rendered_plate else r"\par\vspace{1.15em}",
        *([] if rendered_plate else opening_evidence),
        *exact_evidence(site, numbers),
        *catalogue_note(site, concordance),
        *sources_block(sources),
        r"\vfill",
        r"\noindent{\color{hairline}\rule{\linewidth}{0.4pt}}\par\smallskip",
        date_footer(evidence_cutoff_date, update_date, update_scope),
        r"\end{minipage}",
    ]
    return lines


def render(
    release: Mapping[str, Any],
    concordance: Mapping[str, Any],
    locator_root: Path = LOCATOR_ROOT,
) -> str:
    sites = physical_sites(release)
    located = sum(site["location"].get("latitude_wgs84") is not None for site in sites)
    usable = sum(
        bool(site.get("imagery") and site["imagery"][0].get("render_path"))
        for site in sites
    )
    exact_relationships = sum(len(site["exact_campus_allocations"]) for site in sites)
    if (located, usable, exact_relationships) not in {
        (29, 23, 9),
        (29, 29, 9),
        (31, 29, 9),
        (31, 31, 9),
    }:
        raise ConciseAtlasError(
            "release coverage changed; review the concise layout and update its frozen contract"
        )
    lines = [
        r"% GENERATED FILE. Edit the normalized Atlas data or concise generator, not this fragment.",
        r"% One-page-per-campus Atlas report derived from the normalized Atlas data.",
    ]
    evidence_cutoff_date = str(
        release.get("base_snapshot_date", release["snapshot_date"])
    )
    update_date = str(release["snapshot_date"])
    if update_date == evidence_cutoff_date:
        update_date = None
    if release.get("campus_reconciliation_release"):
        update_scope = "Targeted campus evidence, lifecycle, location, and imagery"
    elif release.get("lifecycle_refresh_release"):
        update_scope = "Lifecycle evidence, location, and imagery"
    else:
        update_scope = "Location and imagery"
    lines.extend(
        intro_page(
            sites,
            evidence_cutoff_date,
            concordance,
            locator_root,
            update_date,
            update_scope,
            release.get("release", {}).get("version"),
            release.get("release", {}).get("release_date"),
        )
    )
    for site in sites:
        lines.extend(
            site_page(
                site,
                evidence_cutoff_date,
                concordance,
                locator_root,
                update_date,
                update_scope,
            )
        )
    lines.append(r"\clearpage")
    return "\n".join(lines) + "\n"


def run(
    atlas_path: Path = DEFAULT_ATLAS,
    output_path: Path = DEFAULT_FRAGMENT,
    locator_root: Path = LOCATOR_ROOT,
    catalogue_concordance_path: Path = DEFAULT_CATALOGUE_CONCORDANCE,
) -> str:
    atlas_path = rooted(Path(atlas_path))
    output_path = rooted(Path(output_path))
    release = json.loads(atlas_path.read_text(encoding="utf-8"))
    sites = physical_sites(release)
    concordance = load_catalogue_concordance(
        Path(catalogue_concordance_path), atlas_path, sites
    )
    rendered = render(release, concordance, Path(locator_root))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--output", type=Path, default=DEFAULT_FRAGMENT)
    parser.add_argument("--locator-root", type=Path, default=LOCATOR_ROOT)
    parser.add_argument(
        "--catalogue-concordance",
        type=Path,
        default=DEFAULT_CATALOGUE_CONCORDANCE,
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="allow missing campus plates and print a placeholder (not for release)",
    )
    args = parser.parse_args()
    global ALLOW_MISSING_PLATES
    ALLOW_MISSING_PLATES = args.preview
    output = args.output
    if args.preview and output == DEFAULT_FRAGMENT:
        # Keep image-free drafts away from the committed report source.
        output = DEFAULT_FRAGMENT.with_name("campus-profiles-preview.tex")
    rendered = run(
        args.atlas,
        output,
        args.locator_root,
        args.catalogue_concordance,
    )
    status = "PREVIEW" if args.preview else "PASS"
    print(json.dumps({"status": status, "profile_count": rendered.count("% Campus profile ")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
