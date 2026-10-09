# Related fab registries and trackers

Last reviewed: August 25, 2026.

No reviewed project provides a fully open, global, campus-level substitute for
the AI Chip Fab Atlas's combination of an AI-relevance rule, claim-level sources,
cited coordinates, and one attributed image per campus. The Atlas should still
be presented as a complement to—rather than a replacement for—the broader
registry ecosystem.

## Open and community resources

- [Wikipedia's fab list](https://en.wikipedia.org/wiki/List_of_semiconductor_fabrication_plants)
  is a broad and useful discovery source, but its unit and campus-level sourcing
  are inconsistent and the list describes itself as incomplete.
- [Wikidata](https://www.wikidata.org/wiki/Q4168959) and
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Semiconductor_fabrication_plants)
  provide open identifiers, coordinates, and scattered reusable photographs.
  They do not provide systematic campus imagery or evidence coverage.
- [OpenStreetMap](https://www.openstreetmap.org/) is valuable for mapped
  industrial features and boundaries. Its aerial editor layers are third-party
  basemaps, not ODbL imagery that can automatically be republished.
- [Chip Sense](https://github.com/aminalav/chip-sense) is an open-source global
  supply-chain map. It uses a schematic basemap and fab-site pins rather than a
  curated satellite archive.
- [India Semiconductor Tracker](https://github.com/pranaykotas/india-semiconductor-tracker)
  is a strong source-linked regional tracker, but it covers a wider mix of
  facility types and does not include fab-by-fab satellite plates.
- [Open Supply Hub](https://opensupplyhub.org/) displays geocoded production
  locations and can use a live Esri imagery basemap. It is cross-sector and
  does not archive a curated image plate for every fab.
- [CSET's Advanced Semiconductor Supply Chain Dataset](https://eto.tech/dataset-docs/chipexplorer/)
  covers processes, tools, materials, firms, countries, and relationships; it
  is not designed to locate individual fabrication campuses.

## View-only and proprietary resources

- [The Buildout](https://thebuildout.ai/methodology) is the main global
  satellite-imagery exception. It provides recurring Sentinel-2-style
  observations for many construction sites, including fabs, but usable imagery
  is not available for every site and its
  [terms](https://thebuildout.ai/terms) prohibit bulk extraction and
  republication of the collection.
- [Aterio's U.S. semiconductor dataset](https://www.aterio.io/datasets/lst_us_semiconductor_manufacturing_facilities)
  uses weekly satellite review and records imagery dates for U.S. projects. It
  is a paid proprietary dataset and does not provide an open global image
  archive.
- [SEMI World Fab Watch](https://www.semi.org/en/products-services/market-data/world-fab-watch)
  and [TechInsights Semiconductor Manufacturing Economics](https://www.techinsights.com/market-analysis-subscriptions/semiconductor-manufacturing-economics)
  provide much broader commercial industry coverage, but their scope, unit of
  analysis, access terms, and evidentiary presentation differ from this Atlas.
- [FabulousMap](https://www.fabulousmap.com/),
  [Silicon Analysts Fab Explorer](https://siliconanalysts.com/tools/fab-explorer),
  [BenchGecko Foundries](https://benchgecko.ai/foundries), and
  [EXAFABS](https://fabs.exafabs.ai/) are useful discovery or comparison tools;
  none was found to offer an openly reusable one-image-per-campus collection.

## Dated open-catalogue concordance

A record-level recheck against four selected open catalogues was completed on
August 25, 2026. Across the Atlas's 31 physical campuses, the review found 24
exact same-campus matches in Wikipedia's fab list, 9 in Chip Sense, 6 in
Wikidata, and 1 in the India Semiconductor Tracker. Chip Sense had five
additional city, regional, or cluster matches. The page profiles display only
positive exact-campus links.

Wikipedia's Fab 15 family row does not distinguish the non-contiguous Fab 15A
and Fab 15B campuses and is not matched, but its Fab 15 (P5) row is a module of
Fab 15B and is matched (corrected in version 1.0.0). See
[`data/catalogue-concordance.json`](data/catalogue-concordance.json) and
[`docs/CATALOGUE_CONCORDANCE.md`](docs/CATALOGUE_CONCORDANCE.md) for the frozen
record links and matching rule.

Catalogue concordance is not proof of completeness or independent evidence of
process capability, AI relevance, lifecycle, or product allocation.

## Using the Atlas alongside other registries

Use the AI Chip Fab Atlas as a purpose-built analytical dataset and use broader
registries for related-work context, candidate discovery, and omission checks.
Do not describe a proprietary database as a validation benchmark unless it was
actually licensed, inspected, and normalized to the same continuous-campus
unit. Candidate records found through another tracker should be verified
against underlying public sources before they enter the Atlas.

The current inclusion protocol is conditioned partly on the foundries in the
reviewed accelerator-product census. That choice can omit disclosure-poor or
uncensused foundries. UMC Fab 12A is a documented boundary case: it has 14 nm
logic capability and public statements about AI applications, but UMC was not
represented in the product census used for this snapshot. Its absence should
be understood as a scope decision, not evidence that it is irrelevant.

The distinguishing visual contribution is therefore not that no one else ever
uses satellite imagery. It is the systematic, cited, one-image-per-campus
presentation in a public release, combined with separate claim-level
evidence. The imagery remains contextual and source-licensed.
