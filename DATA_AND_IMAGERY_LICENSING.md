# Licensing

The repository combines original work by Berkeley AI Risk with third-party
data and imagery. These parts are licensed differently.

| Material | Terms |
| --- | --- |
| Code in `src/` and `tests/` | [MIT License](LICENSE) |
| Original text and data: the Atlas PDF's text, tables, and maps; the documentation; `data/atlas.json`, `data/catalogue-concordance.json`, `data/imagery-provenance.json`, `data/fab-data-center-comparison/atlas-campuses.csv`; and the figures in `figures/` | [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0) (CC BY 4.0), except for the third-party material listed below |
| Aerial and satellite images on the Atlas PDF's campus pages | **Not covered by either license.** Each image remains subject to the terms of the provider credited beside it. |
| Coordinates for 16 campuses that are representative points of OpenStreetMap features | © OpenStreetMap contributors, [Open Database License](https://www.openstreetmap.org/copyright) |
| `data/fab-data-center-comparison/epoch-data-centers.csv` | Epoch AI, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `data/geography/countries.geojson` | Natural Earth, public domain |

## Imagery

Each of the 31 campus pages shows one attributed image. The providers are Esri
World Imagery (16 pages), Taiwan's National Land Surveying and Mapping Center
PHOTO2 service (6), the U.S. Department of Agriculture's National Agriculture
Imagery Program (2), and one page each from the New York State, Oregon, and
Ohio statewide imagery programs, the Capital Area Council of Governments
(Texas), Japan's Geospatial Information Authority, the City of Dresden, and
Saxony's Landesamt für Geobasisinformation (GeoSN). The credit printed beside
each image is the provider's required attribution. Provider, collection, terms,
acquisition date, and a SHA-256 hash for every image are recorded in
[`data/imagery-provenance.json`](data/imagery-provenance.json).

The images appear only inside the attributed PDF. The standalone image files
are not part of the repository, and the images should not be extracted from
the PDF and reused as a separate collection.

See also [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). This document
describes the project's licensing choices; it is not legal advice.
