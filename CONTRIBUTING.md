# Contributing

Corrections and additions are welcome through GitHub issues or pull requests.
Please do not submit a facility solely because it appears on a map or resembles
a fab in imagery.

A campus proposal should provide:

- the operator and precise physical campus being proposed;
- evidence that it meets the documented inclusion rule;
- a source for campus identity and a separate source for the coordinate;
- lifecycle and process-capability evidence with publication or access dates;
- proposition-matched evidence for any named product allocation; and
- enough information to distinguish the campus from adjacent fabs, offices,
  packaging plants, and assembly/test facilities.

Prefer operator filings, official company publications, government or
regulatory records, and other primary sources. Credible independent reporting
can support claims that are not publicly disclosed by an operator, but the
record should label that evidentiary status. External fab trackers are useful
discovery leads; their entries should be independently checked against the
underlying public evidence before inclusion.

For imagery changes, include the provider, collection, acquisition date when
known, resolution, source URL, governing terms, attribution, crop method, and a
clean image retained separately from any marker or boundary overlay. Do not
commit an image unless redistribution permission has been reviewed.

Do not commit re-rendered maps or figures unless their content changed: a
Matplotlib version other than the one that rendered them changes the files'
bytes even when the image looks the same. If you do change a figure, commit the
manifest its script rewrites (`figures/campus-locators/manifest.json` or
`figures/fab-data-center-comparison-manifest.json`). For the comparison map,
also copy the new PDF's `bytes` and `sha256` into
`artifacts.fab_data_center_comparison_pdf` in `data/atlas-manifest.json`, which
no script updates. The tests check every hash these manifests record.

A change to `data/atlas.json` changes its hash, which
`data/atlas-manifest.json`, `data/catalogue-concordance.json`, and both figure
manifests record; the tests fail until those records are updated.

Run `python src/validate_atlas.py` and `pytest -q` before submitting a pull
request.
