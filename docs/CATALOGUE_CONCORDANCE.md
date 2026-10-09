# Concordance with other public fab catalogues

The Atlas records dated, campus-level cross-references to four openly
inspectable catalogues: Wikipedia's fab list, Wikidata, Chip Sense, and the
India Semiconductor Tracker. The machine-readable review is in
`data/catalogue-concordance.json`.

## What appears in the PDF

Only positive exact-campus matches appear on profiles. An exact match means
that the external record identifies the same continuous physical complex or a
named fab, phase, or module within it. City, regional, cluster, and ambiguous
fab-family records are retained in the data as `coarse_locality` matches but
are not printed on profiles.

The note is an interoperability cross-reference. Catalogue presence does not
independently establish a campus's process capability, AI relevance, lifecycle,
or product allocation, and catalogues may rely on overlapping public sources.
The absence of a note must not be read as evidence that a campus appears in no
other catalogue.

Chip Sense matches rest on record labels. Its pins are two-decimal, city-level
approximations that lie 0.7 to 54.8 km from the Atlas coordinate for the nine
exact matches, and five of those labels give only an operator and city.

## Frozen review results

All 31 physical campuses were checked on August 25, 2026.

| Catalogue | Exact-campus matches | Additional coarse matches |
| --- | ---: | ---: |
| Wikipedia fab list | 24 | 0 |
| Chip Sense | 9 | 5 |
| Wikidata | 6 | 0 |
| India Semiconductor Tracker | 1 | 0 |

The Wikipedia list's Fab 15 family row covers both non-contiguous Taichung
campuses, Fab 15A and Fab 15B, and is not matched. Its Fab 15 (P5) row is
matched to Fab 15B (AIFAB-001) as a module within the complex: OpenStreetMap
maps the P5 utility plant and the F15B P6 and P7 buildings inside its Fab 15B
site, and TSMC's 20-F records an F15B land lease from March 2015, before P5's
2016 start. This follows the phase-level treatment of Fab 12 phases P4--P6 at
Fab 12B.

Fraunhofer IIS Velektronik was excluded from page-level links because stable,
reader-friendly item pages were not reliably available during the recheck.
Proprietary or paywalled catalogues were not bulk extracted or normalized, so
the Atlas does not imply a record-level comparison with them.
