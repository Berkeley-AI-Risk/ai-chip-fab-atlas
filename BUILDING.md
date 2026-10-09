# Building and verification

Create the Python environment from `environment.yml` (Python 3.11 with
matplotlib, Pillow, pypdf, pyproj, and pytest):

```sh
conda env create -f environment.yml
conda activate ai-chip-fab-atlas
```

## Checks that run from a public checkout

The evidence data can be validated and the maps rebuilt without the campus
image plates:

```sh
python src/validate_atlas.py
pytest -q
python src/render_locator_maps.py
python src/render_location_comparison.py
```

`render_location_comparison.py` reads the derived Epoch AI coordinate table in
`data/fab-data-center-comparison/`, produced by a strict exact-name join
between Epoch AI's official CSV and the coordinate records in its official
interactive map. The committed figures were rendered with specific Matplotlib
versions, so a rebuild in a different environment can change figure bytes
without changing their content.

## The Atlas PDF

Building the PDF requires the 31 campus plates, which are not distributed (see
[`assets/README.md`](assets/README.md)), plus a TeX installation with
`latexmk`, pdfTeX, and the XCharter and Source Sans Pro fonts (TeX Live 2021
or later). With the plates in `assets/campus-imagery/`:

```sh
python src/validate_atlas.py
python src/build_report.py
python src/build_release_pdf.py
```

`build_report.py` writes the TeX source `report/campus-profiles.tex` from
`data/atlas.json`; it stops if a campus plate is missing. From a public
checkout, `python src/build_report.py --preview` writes an image-free draft to
the ignored file `report/campus-profiles-preview.tex` instead. `build_release_pdf.py` checks every plate against the
SHA-256 in `data/imagery-provenance.json`, makes JPEG copies of the plates for
each edition, compiles each edition with pdfTeX, and records the results in
`data/atlas-manifest.json`:

| Edition | Plates | File |
| --- | --- | --- |
| Compact | long side at most 1,084 px (about 300 ppi as printed), JPEG quality 85 | `ai-chip-fab-atlas.pdf` (committed) |
| Full resolution | original pixel dimensions, JPEG quality 75 | `output/ai-chip-fab-atlas-full-resolution.pdf` (GitHub Release asset) |

Both editions are compiled directly by pdfTeX, so their text, fonts, and links
are identical. `SOURCE_DATE_EPOCH` is set from the release date so that a
rebuild with the same toolchain reproduces the same files.

## Release checks

Automated (run by `python src/validate_atlas.py` and `pytest`, also in CI):

- 32 records representing 31 unique physical campuses, unique source IDs, no
  unresolved source references, a source-bound coordinate and one image record
  per campus, and summary counts that recompute;
- the recorded hashes of the data, figures, and PDFs, where the files are
  present (the campus plates and the full-resolution PDF are checked only
  locally);
- the compact PDF's page count and size; and
- a text layer in which words with ligatures ("Office", "after") copy and
  search correctly.

Checked by `build_release_pdf.py` when the PDFs are built: every campus plate
against its recorded hash, and 32 pages in each edition.

Checked by hand before a release: embedded fonts (`pdffonts`), no TeX overfull
boxes or fatal warnings, footers that stay above the page number, a visual pass
over the pages, and no standalone image plates staged for Git.
