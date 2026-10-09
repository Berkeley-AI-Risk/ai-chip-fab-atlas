from __future__ import annotations

import importlib.util
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "src/validate_atlas.py"
    spec = importlib.util.spec_from_file_location("validate_atlas", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_atlas_validation_passes():
    atlas = load_json("data/atlas.json")
    assert load_validator().validate(require_assets=False) == {
        "record_count": 32,
        "physical_campus_count": 31,
        "source_count": len(atlas["source_registry"]),
    }


def test_canonical_paths_exist():
    required = [
        "ai-chip-fab-atlas.pdf",
        "README.md",
        "LICENSE",
        "LICENSE-CC-BY-4.0",
        "CITATION.cff",
        "CHANGELOG.md",
        "data/atlas.json",
        "data/atlas-manifest.json",
        "data/catalogue-concordance.json",
        "data/imagery-provenance.json",
        "figures/fab-data-center-comparison.pdf",
        "figures/fab-data-center-comparison.jpg",
        "report/atlas.tex",
        "report/campus-profiles.tex",
    ]
    assert [path for path in required if not (ROOT / path).is_file()] == []


def test_no_historical_release_names_in_public_paths():
    forbidden = ("_v1", "_v2", "-v1", "-v2", "final_v", "best_free")
    paths = [path.relative_to(ROOT).as_posix().lower() for path in ROOT.rglob("*")]
    assert not [path for path in paths if any(token in path for token in forbidden)]


def test_manifest_matches_atlas():
    atlas = load_json("data/atlas.json")
    manifest = load_json("data/atlas-manifest.json")
    assert manifest["physical_campus_count"] == atlas["summary"]["physical_campus_count"]
    assert manifest["record_count"] == atlas["summary"]["record_count"]
    assert manifest["source_count"] == atlas["summary"]["source_count"]
    assert manifest["version"] == atlas["release"]["version"]
    assert manifest["release_date"] == atlas["release"]["release_date"]
    assert manifest["atlas_sha256"] == digest(ROOT / "data/atlas.json")


def test_every_recorded_hash_matches():
    """Every file hash recorded in a manifest must match the file, when present.

    The full-resolution PDF and the campus plates are not distributed with the
    repository, so their hashes are checked only when the files exist locally.
    """
    checked = 0
    mismatched = []

    def check(path: str, expected: str) -> None:
        nonlocal checked
        target = ROOT / path
        if target.is_symlink() and not target.exists():
            mismatched.append(f"{path} (broken link)")
        elif target.is_file():
            checked += 1
            if digest(target) != expected:
                mismatched.append(path)

    def walk(value) -> None:
        if isinstance(value, dict):
            for path_key, hash_key in (
                ("path", "sha256"),
                ("output_path", "sha256"),
                ("atlas_path", "atlas_sha256"),
                ("asset_path", "asset_sha256"),
            ):
                if isinstance(value.get(path_key), str) and isinstance(value.get(hash_key), str):
                    check(value[path_key], value[hash_key])
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for manifest in (
        "data/atlas-manifest.json",
        "data/catalogue-concordance.json",
        "data/imagery-provenance.json",
        "figures/campus-locators/manifest.json",
        "figures/fab-data-center-comparison-manifest.json",
    ):
        walk(load_json(manifest))
    assert mismatched == []
    assert checked >= 40


def test_committed_pdf_is_the_compact_edition():
    manifest = load_json("data/atlas-manifest.json")
    compact = manifest["artifacts"]["atlas_pdf"]
    assert compact["path"] == "ai-chip-fab-atlas.pdf"
    assert compact["page_count"] == 32
    assert compact["bytes"] < 25 * 1024 * 1024
    from pypdf import PdfReader

    pdf = ROOT / compact["path"]
    assert len(PdfReader(pdf).pages) == compact["page_count"]
    assert pdf.stat().st_size == compact["bytes"]


def test_catalogue_concordance_is_bound_and_conservative():
    atlas = load_json("data/atlas.json")
    concordance = load_json("data/catalogue-concordance.json")
    physical_ids = {
        site["campus_id"]
        for site in atlas["sites"]
        if site["record_unit_type"] == "physical_front_end_campus"
    }
    assert concordance["atlas"]["sha256"] == digest(ROOT / "data/atlas.json")
    assert set(concordance["campus_matches"]) == physical_ids
    exact_classes = {"same_complex", "module_within_complex"}
    for matches in concordance["campus_matches"].values():
        for match in matches:
            if match["display_on_profile"]:
                assert match["match_class"] in exact_classes


def test_pdf_text_layer_keeps_ligature_words():
    """Ligature glyphs must map back to plain letters for copying and search."""
    import re

    from pypdf import PdfReader

    text = "".join(page.extract_text() or "" for page in PdfReader(ROOT / "ai-chip-fab-atlas.pdf").pages)
    for word in ("Office", "official", "shifted", "after", "sufficiency"):
        assert word in text, word
    assert not re.search(r"\b(Oice|oicial|shied|aer|suiciency)\b", text)
    assert not re.search("[\ufb00-\ufb06]", text)
