# Methodology

## Research purpose

The Atlas supports a narrower question than a conventional semiconductor-fab
census: which continuous physical front-end wafer-fabrication campuses may
matter for the manufacture of advanced AI chips, according to reviewed public
evidence?

It is best understood as a selective candidate inventory, not a claim that all
listed campuses currently make AI accelerators and not a guarantee that every
relevant campus has been found.

## Unit of analysis and inclusion

One record represents one continuous physical campus. Multiple fab modules or
phases on the same continuous site are counted once; noncontiguous sites are
not silently merged. Headquarters, design offices, packaging-only plants, and
assembly/test facilities are outside the primary count.

The review uses two routes:

1. trace publicly documented data-center AI processors and related
   manufacturing programs to plausible production campuses; and
2. review publicly identified operating logic campuses at 16 nm or more
   advanced operated by the foundries identified in the first step.

Eleven older-node or under-construction sites are also included because their
documented capabilities may matter for older or future AI chips. This rule
reduces—but does not eliminate—product-first selection bias, because the second
route is still limited to the foundries identified in the first.

## Claim separation

The data model treats the following as different propositions:

- the campus exists and is operated by the named organization;
- the displayed coordinate is a reproducible point associated with it;
- the campus is operating, expanding, commissioning, or under construction;
- a fabrication process is documented at that campus;
- a product's foundry and node are documented; and
- a named product is allocated to that exact physical campus.

Evidence for one proposition does not automatically support another. In
particular, a campus having a compatible node does not establish that it makes
a given chip. Exact campus allocations, independently reported allocations,
and node-compatibility candidates remain distinct in the data.

## Dates

Five kinds of date appear in the Atlas:

- **Evidence cutoff** (August 25, 2026): the latest date of the public evidence
  reviewed for this version. Claims describe what that evidence showed; later
  developments are listed in `CHANGELOG.md` but not reflected in the records.
- **Status "as of" date**: printed with each campus's facility status and
  stored as `lifecycle_as_of_date` (products have the same field). It is the
  date the recorded status describes: the evidence cutoff for most records, or
  an earlier date when the status rests on evidence reviewed before the cutoff.
  Statuses corrected after the cutoff keep an as-of date no later than it.
- **Source dates**: each source's publication date, or its access date when it
  is undated; undated web pages cited through a web-archive capture show the
  capture date. The 50 sources added during the September 2026 fact-check, and
  4 earlier sources whose access date it updated, carry an access date of
  September 27, 2026, after the cutoff; none has a recorded publication date
  after the cutoff. The PDF prints one source date after the cutoff: the Beijing
  Jingcheng page cites Esri World Imagery as accessed September 27, 2026, when
  that plate was re-exported from imagery dated January 11, 2026.
- **Image dates**: each plate caption gives the imagery's acquisition date or,
  when the provider does not state it, the date the image was accessed. Images
  can predate the cutoff by several years and show the campus as it was then.
- **Review and release dates**: `review_date` records when a review decision
  (adding, splitting, correcting, or excluding a record or relationship) was
  last made, and the release date is the date a version was finalized
  (September 27, 2026 for version 1.0.0). Corrections made after the cutoff
  still use evidence from on or before it.

## Coordinates and images

Every profile states a coordinate and cites its origin. Depending on the
available evidence, the point may be an operator-linked map point, an
OpenStreetMap representative point, a regulator facility point, an in-facility
stack or process point, or a documented analyst estimate. These points are
search anchors, not surveyed legal boundaries.

The yellow cross is generated from the cited coordinate. A crop can be shifted
to show the campus better, so the cross need not be centered. Imagery provides
geographic and physical context only. It does not establish process node,
product allocation, production volume, ownership, or legal parcel boundaries.

Embedded geometry measurements describe visible roofs, developed plant, or a
campus-use envelope under the definitions recorded in the data. They are not
cleanroom area, capacity, or legal-property measurements, and some estimates
fail closed when interpreters could not establish a defensible interval. The
outlines behind these measurements were traced by two independent AI-agent
annotators on Taiwan NLSC and U.S. NAIP imagery; they are not surveyed
boundaries and were outside the scope of the September 2026 fact-check.

## External registries

The recommended research design combines resources asymmetrically. The Atlas
is the frozen analytical dataset because its unit and evidence model match the
policy question. Broader registries are used for candidate discovery, related
work, and omission checks. Individual Atlas claims continue to rest on their
underlying public sources.

This avoids two errors: treating a proprietary or mutable registry as
automatically reproducible, and treating an author-created Atlas as independent
confirmation of itself.

The PDF displays positive same-campus cross-references from the dated review of
four selected open catalogues. City-, regional-, cluster-, and ambiguous
fab-family matches are retained in the machine-readable concordance but are not
shown on profiles. See `docs/CATALOGUE_CONCORDANCE.md`. These links improve
interoperability; they do not independently establish capability or products.

## Citing the Atlas

Cite a specific version of the Atlas, with its release date and evidence
cutoff, as the source of any sample, coordinates, classifications, or maps you
use (see `CITATION.cff`). That is ordinary citation of an author-created
dataset; it is not independent confirmation of the dataset's contents.

Statements about an individual facility should cite the underlying public
sources recorded for that claim, not only the Atlas. Broader industry
registries are best cited separately as related work and, when actually
inspected, used for candidate discovery and omission checks. Agreement between
registries is not a completeness or recall estimate: registries may share
upstream sources, may use a fab or production line rather than a continuous
campus as their unit, and may omit undisclosed sites.

A compact description is:

> The AI Chip Fab Atlas is a public-evidence inventory of physical front-end
> wafer-fabrication campuses that met its stated inclusion protocol as of the
> evidence cutoff. Campus claims retain their underlying public citations. It
> is not a complete global census.

## Principal limitations

- Public disclosure is uneven across firms, countries, languages, and time.
- Product-to-campus allocation is often confidential or reported only by
  secondary sources.
- The foundry-conditioned reverse review can miss operators absent from the
  product census; UMC Fab 12A is a known boundary case.
- The cohort excludes memory, HBM, packaging, and assembly/test plants from the
  primary front-end-logic count even though those facilities also matter for AI
  hardware supply chains.
- Absence from the Atlas means only that a campus was not included under this
  snapshot's protocol. It is not evidence that the campus does not exist or is
  irrelevant.
- The image collection is heterogeneous and optimized for publication context,
  not for estimating population-level remote-sensing detectability.

## Updating the Atlas

Proposed changes should identify the affected claim, attach
proposition-matched sources, and state whether the change affects campus scope,
coordinates, lifecycle, capability, product allocation, or imagery. A release
should be frozen and audited before it is used for paper-level counts or maps.
Stable public filenames point to the current release; historical states are
preserved by tags and archival releases.
