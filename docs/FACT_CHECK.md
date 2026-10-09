# Fact-check record

All of the checks described here were carried out by AI agents. People reviewed
drafts and questioned doubtful claims, but did not re-verify every citation.

## September 2026: fact-check before version 1.0.0

**Scope.** Every claim printed on the 31 campus pages and the overview page, and
every substantive field of the structured data as it stood in the August 25,
2026 snapshot: the 32 site records, 91 products, 17 product components, 50
unresolved products, and 84 review decisions. The corrections then added 4
products, 9 review decisions, and 50 sources and reduced the unresolved
products to 45, giving the 95 products, 93 review decisions, and 270 sources in
this release. The check also tested the overview's completeness claim by
independently listing operating logic campuses at 16 nm or more advanced run by
the foundries in the product census, and sample-checked the catalogue
concordance. Area measurements and image credit lines were outside its scope;
credits were reviewed separately.

**Method.** A different AI system from the one that built the Atlas (Claude Code
running Claude Opus 5.5, rather than OpenAI Codex) checked each claim against
its cited source and, independently, against other public sources, judging it
as of the August 25, 2026 evidence cutoff. A second agent then re-examined each
flagged problem and tried to refute it. Confirmed problems were corrected. The
corrections were then reviewed the same way, and the further issues that review
found (for example in the Positron, Tesla, and Lingang entries) were fixed and
validated, but not reviewed a third time.

**Results.** 1,485 claims were checked. Checkers flagged 238; verifiers refuted
29 of those. The confirmed problems were:

| Verdict | Count | Meaning |
| --- | ---: | --- |
| False | 12 | Wrong as of the stated date |
| Imprecise | 50 | Overstated, understated, or misleading |
| Omission | 30 | A well-sourced fact the Atlas's own rules call for was missing |
| Citation problem | 79 | Claim true, but the cited source was misdescribed, misdated, dead, or did not support it |
| Changed after the cutoff | 15 | Accurate at the cutoff; later developments are listed in the changelog |
| Could not be verified | 23 | See the open items below |

The false statements included an AI accelerator attributed to the wrong fab
(Positron Archer at TSMC Arizona), a coordinate outside its campus (SMIC/SMBC
Beijing), a false statement about Intel's Ohio schedule, and errors in
product records (for example Biren, Enflame, and Iluvatar CoreX chip details).
The citation problems were most often paraphrased or invented source titles
and missing or wrong dates. Every change is listed in
[`CHANGELOG.md`](../CHANGELOG.md).

### Open items

These could not be settled from public sources, or were judged not worth a
substantive change without better evidence:

- Whether TSMC Fab 14A and Fab 14B are contiguous (the Atlas treats them as
  separate campuses).
- The exact datum of the SMIC Shanghai Lingang coordinate, and the link between
  the SMIC Tianjin campus and its land parcel, which the Atlas already describes
  as inferred.
- Whether the 4 nm Groq LPU that Groq said in 2023 it would make with Samsung is
  the chip now sold as Groq 3.
- Hygon DCU and Iluvatar CoreX records whose sources were unreachable or
  undated at the time of the check.
- The yellow-cross positions are drawn into the images; their coordinates are
  not recorded separately in `data/imagery-provenance.json`.
- Qualcomm Cloud AI 100 Ultra's 7 nm node is supported by Qualcomm's 2019 Cloud
  AI 100 announcement rather than the cited product page.
- Two programs are recorded as watch items rather than listed: Tesla's AI6.5
  (tied by Tesla's CEO to TSMC 2 nm in Arizona, with no schedule) and a reported
  N4 conversion at TSMC Fab 15A. A Samsung 2 nm program for Preferred Networks
  (announced July 2024) is not yet in the product census.

## August 2026: audits during construction

While building the Atlas, fresh AI agents with no access to the working
conversation audited the August 25, 2026 snapshot record by record: campus
units, lifecycle, process capability, product relationships, coordinate
provenance, citation roles, embedded source records, image paths and hashes,
and summary counts. The final pre-release audit returned a hold. Corrections
made before the snapshot included:

- narrowing combined TSMC records to Fab 15B, Fab 14B, and Fab 12B;
- treating Hua Hong Fab 7 and Fab 9 as one continuous Wuxi campus;
- replacing a generic EPA citation with four facility-specific U.S. records;
- correcting the SMIC Southern representative coordinate;
- classifying Samsung Taylor as pre-operational construction;
- updating GlobalFoundries and Intel lifecycle and capability evidence;
- updating Groq 3 to full production while keeping an independent-reporting
  caveat for its exact 4 nm Pyeongtaek allocation;
- regenerating seven yellow-cross markers from corrected coordinates; and
- removing duplicate, broken, and orphan source records.

A further review of the corrected data passed it for release to collaborators.
These audits used the same model family that built the Atlas, so they were
fresh-context checks rather than independent ones.
