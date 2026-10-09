# Local release outputs

`python src/build_release_pdf.py` writes the full-resolution edition of the
Atlas here as `ai-chip-fab-atlas-full-resolution.pdf`. That file is attached to
each [GitHub Release](../../../releases) rather than committed. The compact
edition is committed at the repository root as
[`ai-chip-fab-atlas.pdf`](../ai-chip-fab-atlas.pdf). Both editions' byte counts and
SHA-256 hashes are recorded in `data/atlas-manifest.json`.
