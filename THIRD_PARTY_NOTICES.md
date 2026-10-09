# Third-party notices

- **Epoch AI, AI Data Centers.** `data/fab-data-center-comparison/epoch-data-centers.csv`
  contains, for 83 data centers, the name, country, address, owner, current
  H100-equivalent compute, and current power from Epoch AI's dataset
  (`owner_raw` keeps Epoch's owner field verbatim, including its confidence
  tags such as `#confident`, `#likely`, and `#speculative`),
  joined by exact name to coordinates and operational status from Epoch's
  official interactive map.
  The join and the column selection are modifications by Berkeley AI Risk.
  Source: [Epoch AI, "AI Data Centers"](https://epoch.ai/data/ai-data-centers),
  used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Natural Earth.** The country boundaries in `data/geography/countries.geojson`
  (Natural Earth 1:110m Admin 0 Countries, version 5.1.1) and the base maps
  drawn from them are [public domain](https://www.naturalearthdata.com/about/terms-of-use/).
- **OpenStreetMap.** Coordinates for 16 campuses are representative points of
  OpenStreetMap features, © OpenStreetMap contributors, available under the
  [Open Database License](https://www.openstreetmap.org/copyright).
- **Campus imagery.** Providers, collections, terms URLs, required credits,
  dates, and image hashes are listed campus by campus in
  [`data/imagery-provenance.json`](data/imagery-provenance.json). The
  standalone images are not part of the repository; see
  [`DATA_AND_IMAGERY_LICENSING.md`](DATA_AND_IMAGERY_LICENSING.md).
- **Other fab catalogues.** `data/catalogue-concordance.json` records dated
  cross-references (catalogue names, record labels, and links) to Wikipedia's
  fab list, Wikidata, Chip Sense, and the India Semiconductor Tracker. Their
  content remains subject to each catalogue's own terms.

All other cited publications remain the property of their authors and
publishers. The Atlas records citations and links; it does not redistribute
the underlying publications.
