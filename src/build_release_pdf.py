#!/usr/bin/env python3
"""Build the two distributed editions of the Atlas PDF.

Each edition is compiled directly by pdfTeX from JPEG copies of the campus
plates, so the text layer, fonts, links, and named destinations are exactly
those of the TeX build (no post-processing step re-encodes the document).

- ``compact``: plates resampled to at most 1,084 pixels on the long side
  (about 300 ppi at the printed plate size), JPEG quality 85.  This is the
  edition committed to the repository as ``ai-chip-fab-atlas.pdf``.
- ``full``: plates at their original pixel dimensions, JPEG quality 75.  This
  edition is attached to GitHub Releases rather than committed.

Every plate is checked against the SHA-256 recorded in
``data/imagery-provenance.json`` before it is used; a missing or altered plate
stops the build.  The edition sizes, hashes, page counts, and encoding settings
are recorded in ``data/atlas-manifest.json``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image, __version__ as PILLOW_VERSION
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
PLATE_PATTERN = re.compile(r"\{\.\./(assets/campus-imagery/[A-Za-z0-9_.-]+\.png)\}")

EDITIONS = {
    "compact": {
        "max_pixels": 1084,
        "jpeg_quality": 85,
        "output": "ai-chip-fab-atlas.pdf",
        "manifest_key": "atlas_pdf",
        "distribution": "committed to the repository",
    },
    "full": {
        "max_pixels": None,
        "jpeg_quality": 75,
        "output": "output/ai-chip-fab-atlas-full-resolution.pdf",
        "manifest_key": "atlas_pdf_full_resolution",
        "distribution": "GitHub Release asset",
    },
}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_plate_hashes() -> dict[str, str]:
    provenance = json.loads((ROOT / "data/imagery-provenance.json").read_text(encoding="utf-8"))
    return {record["asset_path"]: record["asset_sha256"] for record in provenance["campuses"]}


def make_plates(plates: list[str], edition: str, settings: dict) -> Path:
    hashes = expected_plate_hashes()
    target = ROOT / "build" / edition / "plates"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for plate in plates:
        source = ROOT / plate
        if not source.is_file():
            raise SystemExit(f"Missing campus plate: {plate}")
        if hashes.get(plate) != file_sha256(source):
            raise SystemExit(f"Campus plate does not match imagery-provenance.json: {plate}")
        with Image.open(source) as image:
            image = image.convert("RGB")
            limit = settings["max_pixels"]
            if limit and max(image.size) > limit:
                scale = limit / max(image.size)
                size = (round(image.width * scale), round(image.height * scale))
                image = image.resize(size, Image.LANCZOS)
            image.save(
                target / (Path(plate).stem + ".jpg"),
                format="JPEG",
                quality=settings["jpeg_quality"],
                optimize=True,
                subsampling="4:2:0",
            )
    return target


def source_date_epoch(release_date: str) -> str:
    moment = datetime.strptime(release_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return str(int(moment.timestamp()))


def build_edition(edition: str, settings: dict, release_date: str) -> Path:
    profiles = (REPORT / "campus-profiles.tex").read_text(encoding="utf-8")
    plates = sorted(set(PLATE_PATTERN.findall(profiles)))
    expected = len(expected_plate_hashes())
    if len(plates) != expected:
        raise SystemExit(
            f"report/campus-profiles.tex references {len(plates)} campus plates; expected "
            f"{expected}. Rebuild it with build_report.py (not --preview) after adding the plates."
        )
    make_plates(plates, edition, settings)
    variant = PLATE_PATTERN.sub(
        lambda match: "{../build/" + edition + "/plates/" + Path(match.group(1)).stem + ".jpg}",
        profiles,
    )
    (REPORT / f"campus-profiles-{edition}.tex").write_text(variant, encoding="utf-8")
    wrapper = (REPORT / "atlas.tex").read_text(encoding="utf-8")
    if wrapper.count(r"\input{campus-profiles}") != 1:
        raise SystemExit(r"report/atlas.tex must contain exactly one \input{campus-profiles}")
    wrapper = wrapper.replace(r"\input{campus-profiles}", rf"\input{{campus-profiles-{edition}}}")
    job = f"edition-{edition}"
    (REPORT / f"{job}.tex").write_text(wrapper, encoding="utf-8")
    env = dict(os.environ, SOURCE_DATE_EPOCH=source_date_epoch(release_date), FORCE_SOURCE_DATE="1")
    subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", f"{job}.tex"],
        cwd=REPORT,
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    output = ROOT / settings["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(REPORT / f"{job}.pdf", output)
    subprocess.run(["latexmk", "-c", f"{job}.tex"], cwd=REPORT, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--edition", choices=[*EDITIONS, "all"], default="all")
    parser.add_argument("--manifest", default="data/atlas-manifest.json")
    args = parser.parse_args()

    if shutil.which("latexmk") is None:
        raise SystemExit("latexmk was not found on PATH")
    atlas = json.loads((ROOT / "data/atlas.json").read_text(encoding="utf-8"))
    release_date = atlas["release"]["release_date"]
    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_pages = manifest["artifacts"]["atlas_pdf"]["page_count"]

    selected = EDITIONS if args.edition == "all" else {args.edition: EDITIONS[args.edition]}
    summary = {}
    for edition, settings in selected.items():
        output = build_edition(edition, settings, release_date)
        page_count = len(PdfReader(output).pages)
        if page_count != expected_pages:
            raise SystemExit(f"{output.name} has {page_count} pages; expected {expected_pages}")
        manifest["artifacts"][settings["manifest_key"]] = {
            "bytes": output.stat().st_size,
            "distribution": settings["distribution"],
            "page_count": page_count,
            "path": output.relative_to(ROOT).as_posix(),
            "sha256": file_sha256(output),
            "build": {
                "script": "src/build_release_pdf.py",
                "edition": edition,
                "plate_encoding": f"JPEG quality {settings['jpeg_quality']}, 4:2:0 chroma subsampling (Pillow {PILLOW_VERSION})",
                "plate_pixels": (
                    f"long side resampled to at most {settings['max_pixels']} px (Lanczos)"
                    if settings["max_pixels"]
                    else "original pixel dimensions"
                ),
                "tex_engine": "pdfTeX via latexmk; SOURCE_DATE_EPOCH set from the release date",
            },
        }
        summary[edition] = manifest["artifacts"][settings["manifest_key"]]
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
