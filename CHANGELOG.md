# Changelog

## 1.0.0 (September 27, 2026)

First public version. The evidence cutoff is unchanged: facility and product
evidence was reviewed through August 25, 2026. This version corrects the
August 25, 2026 snapshot after a fact-check of every claim in the PDF and the
structured data (see [`docs/FACT_CHECK.md`](docs/FACT_CHECK.md)). Corrected
claims rest on sources published on or before the evidence cutoff; later
developments are listed at the end and are not reflected in the Atlas.

### Corrections that change the PDF

**Overview (p. 1).** The inclusion paragraph now says that 11 older-node or
under-construction sites are included beyond the two main routes. It
previously said "a few older-node, pilot, or development sites".

**Taiwan (pp. 2–7).**
- Fab 12B: the OpenStreetMap source is retitled to the feature's actual name,
  "TSMC Fab 12"; identifying the mapped area as Fab 12B is noted as an Atlas
  inference.
- Fab 14B: a source cited under an invented title ("production milestone") now
  carries its real headline, "TSMC Details Impact of Fab 14B Photoresist
  Material Incident, Updates 1Q'19 Guidance" (February 15, 2019).
- Fab 15B: the page now lists the Wikipedia fab list as a same-campus
  catalogue; its Fab 15 (P5) row is a module of Fab 15B.
- Fab 18A/B: TSMC's December 29, 2022 release is cited by its real headline
  and date.
- Fab 20: the N2 ramp is attributed to smartphone, high-performance-computing,
  and AI demand, as TSMC states, not to HPC and AI alone.
- Fab 22: a Science Park Bureau source is cited by its real title and date
  (May 2025).
- TSMC's executive-profile page, which supports several capability statements,
  is now cited from an archived copy made before the page changed.

**Japan and South Korea (pp. 8–12).**
- JASM Kumamoto: the capability line now separates the operating fab (Fab 1,
  which TSMC's 20-F calls Fab 23; 28 nm its most advanced volume node at the end
  of 2025) from the nodes TSMC plans to offer at the two-fab site.
- Hwaseong: capability now notes that 2 nm (SF2) production on the S3 line is
  independently reported; the 3 nm ceremony source has its exact title and date.
  The opening sentences on this page and the next cite only Samsung's own
  sources for what Samsung says.
- Pyeongtaek: the capability line now names the S5 and S6 lines, Samsung's
  2020 plan for EUV 5 nm-and-below production, and independently reported 4 nm
  output on S5. The named product is now "Groq 3 LPU" (the chip Samsung makes);
  Groq 3 LPX is NVIDIA's system built on it. Groq 3 statements that were cited
  only to Samsung's sites page were removed from the opening summary.
- Rapidus IIM-1: the prototyping release is cited by its actual title.

**China (pp. 13–20).**
- SMIC Southern SN1/SN2: the page no longer says planning records make SN1 and
  SN2 "one SMIC Southern campus"; the planning record places them on a
  Zhangjiang block that also holds SMIC's Shanghai 200 mm and 300 mm fabs. The
  unsupported "N+1" is removed. The page now names Huawei Ascend 910B, from
  April 2025 congressional testimony that SMIC was producing 910B dies and that
  SN2 was China's only active 7 nm line, with its limits stated: the link
  combines two statements, the testimony also cites officials as saying TSMC
  made more than 2 million 910B dies, and later production is unconfirmed. The
  location now reads Shanghai, like the other Shanghai campuses. Several
  sources now carry their real titles and dates.
- SMIC/SMBC Beijing: **the coordinate was wrong.** It lay about 270 m outside
  the campus's stated east boundary. It now marks the center of the four-road
  parcel that SMBC's 2024 report gives as the plant boundary (39.727,
  116.572), and the campus image was re-exported, centered on the corrected point.
- SMIC Shanghai Lingang: status changed from "preparing to open or beginning
  operations" to "operating"; SMIC's 2024 interim report counts the fab among
  its operating fabs, and the "undergoing verification" wording is removed. The
  coordinate note no longer claims the point is an auxiliary building inside
  the campus: it was converted from a photomask project's environmental record
  that does not tie the point to this campus.
- Huali Fab 6: the Biren entry now reports only what Reuters says: a single
  source that Biren is using Huali's 7 nm line for tapeout, and, separately,
  that Huali's 7 nm work is at Fab 6. The status line and limits are aligned
  with it, and the location is Shanghai (municipality).
- Hua Hong Wuxi: the node ranges are cited to Hua Hong's own filings; several
  sources carry their real titles and publishers.

**United States (pp. 21–27).**
- GlobalFoundries Fab 8: the CloudBlazer entry now adds that Enflame later
  confirmed 12 nm production and commercial use, without naming the campus.
- Intel Arizona: the coordinate note now says the EPA point is an
  address-matched point on the road at the campus edge. The page now names
  Positron's Archer: EE Times reports that the Altera Agilex-7M FPGAs in
  Positron's Atlas system are made by Intel in Chandler, and Business Insider
  also places Positron's chips there. The campus link is marked as an inference
  from these city-level reports.
- Intel Oregon: status changed from "operating; expansion under construction"
  to "operating"; no reviewed source shows expansion under construction.
- Intel Ohio One: **the schedule statement was false.** The page said Intel's
  2030–2032 module dates "were not reaffirmed"; the Columbus Dispatch reported
  that Intel gave a firmer timeline in a 2026 state report, and June 2026
  reporting still listed 2030–2032 operations. The page also said Intel had not
  specified a node; the CHIPS award record lists Intel 14A and future nodes for
  the campus.
- Samsung Taylor: "None identified" is replaced by two planned allocations,
  Tesla AI6 and AI5, with dated statements: Tesla's CEO said in January 2026 that
  AI6 is for Optimus and data centers and in April 2026 that it would use
  Samsung's 2 nm fab in Texas; he said in October 2025 that Samsung would make
  AI5 in Texas, and a July 2026 post by a Samsung Foundry engineer, later
  deleted, placed AI5 at Taylor on 2 nm. Both are marked as plans, not observed
  output.
- TSMC Arizona: **Positron's Archer was removed.** The page said Archer was
  made at TSMC Fab 21; Archer is an Altera Agilex-7M FPGA made by Intel (now
  listed on the Intel Arizona page). Tesla AI5 is added as a planned allocation
  (in July 2025 Tesla's CEO said TSMC would make AI5 first in Taiwan and then in
  Arizona). NVIDIA's October 2025 source carries its actual title.

**Europe, Israel, and India (pp. 28–32).**
- Intel Leixlip: the unsupported clause "Fab 24 has 14 nm production" is
  removed; no cited source states Fab 24's current node. The one-campus
  statement is also cited to Intel Ireland's 2025 environmental report, and the
  2016 report is cited only for the coordinate.
- Intel Kiryat Gat: the expansion sentence now says only what the sources
  support: Intel lists its Israel expansion as delayed or cancelled, and the
  name Fab 38 is attributed to June 2026 reporting. The government facility
  record is cited by its real title.
- Tata Dholera: the 32,000 wafers/month figure is described as an
  environmental-clearance record, not a phase; the minutes are cited by their
  own heading.

### Imagery and credits

- Every campus image now prints its provider's required credit beside it,
  including "Created by editing GSI Tiles" for Japan's GSI image and the
  dl-de/by-2-0 license notice and license link for the two Saxony images.
  Saxony's survey office is named by its current name, Landesamt für
  Geobasisinformation Sachsen (GeoSN).
- The SMIC/SMBC Beijing image was re-exported on September 27, 2026, from the
  same Esri imagery (Vantor, January 11, 2026), centered on the corrected
  coordinate.

### Data-only corrections

These change `data/atlas.json` but not the printed pages.

- **Products.** Corrected foundry, node, lifecycle, scope, or aliases for, among
  others: Huawei Ascend 910B (mixed SMIC- and TSMC-made dies reported), Ascend
  910C and 950PR, NVIDIA Blackwell Ultra and Rubin, AMD Instinct MI455X (N2
  compute dies, N3P fabric and I/O dies), Biren BR166 (shipments reported in
  2025) and BR110 (inference), SambaNova SN40L and SN50, Enflame S60 and L600
  (the chips are Suisi 320 and 400, not "Suiran"), Iluvatar CoreX TianGai 100,
  150, and 300 and ZhiKai 100, Meta MTIA 100, 200, and 300, Alibaba T-Head
  Zhenwu M890, FuriosaAI RNGD, Groq's and Tenstorrent's Samsung 4 nm chips,
  NextSilicon Maverick-2, Graphcore GC200/Bow, and Intel Gaudi 2 and 3. Positron
  Archer is reclassified as an Intel-made FPGA product (see Intel Arizona).
  Groq's 2023 Samsung 4 nm design, which SemiAnalysis reports was never
  productized, is no longer counted as a future program at Samsung Taylor.
- **New records.** Products: Tesla AI5 and AI6, PFN's MN-Core processor planned
  at Rapidus, and Enflame CloudBlazer T20/T21. Twenty relationships added and
  two removed (Archer at TSMC Arizona; Groq's unproductized design at Taylor):
  four new campus allocations (the Tesla plans and Archer at Intel Arizona), the
  Ascend 910B upgrade at SMIC SN2, and node-compatibility candidates applying
  the Atlas's existing rules consistently (for example MI455X at Fab 20 and Fab
  22; Hanguang 800 at Fab 14B and Fab 16; Gaudi 2, TianGai 100, and ZhiKai 100
  at Fab 15B; Maverick-2 at Fab 18A/B; H100, H200, and Blackwell Ultra at TSMC
  Arizona). Nine new review decisions record these and two watch items: a
  reported N4 conversion at TSMC Fab 15A, not confirmed by TSMC, and Tesla's
  AI6.5, which Tesla's CEO tied to TSMC 2 nm in Arizona without a schedule.
- **Sources.** 50 sources added and 87 corrected: real titles in place of
  paraphrases, missing or wrong publication dates, canonical or archived URLs
  for pages that moved or disappeared, and notes that overstated what a source
  says.
- **Records.** The monitoring record for a reported Shenzhen cluster is
  renamed "PXW/PST Shenzhen cluster" (no source supports "Guanlan"); several
  campus notes, aliases, and inclusion rationales are corrected; the Chip
  Sense catalogue matches now state that they are label-based.

### Presentation and packaging

- The Atlas is named the AI Chip Fab Atlas (working drafts used "Chip Fab
  Atlas" and "Public-Evidence AI-Chip Fab Atlas"). The PDF's title page and
  running header use the name, with "Public-Evidence Atlas of AI-Relevant
  Chip-Fabrication Campuses" as the subtitle.
- The overview page reads "This atlas presents" (not "This appendix") and shows
  the version and release date.
- The product heading on every campus page reads "Named data-center AI
  accelerators or programs", matching the scope of the product census.
- Citations of undated web pages that are cited through a web-archive capture
  show the capture date. Translated or romanized titles are marked "In Korean."
  or "In Chinese."
- The PDF is published in two editions built directly by pdfTeX: a compact
  edition in the repository and a full-resolution edition attached to the
  release. Copying and searching text now works for words with ligatures ("fi",
  "fl", "ff", "ft"), which earlier builds had broken.
- Three pages whose text pushed the footer below the page number now fit.
- The PDF's author metadata is Berkeley AI Risk.
- The comparison map of fab and AI data-center locations uses the palette of
  September 23, 2026 and reflects the corrected Beijing coordinate and
  statuses.
- Licenses (MIT for code; CC BY 4.0 for original text and data), third-party
  notices, a citation file, and this changelog were added.

### Developments after the evidence cutoff (not reflected in this version)

- Samsung Taylor: Seoul Economic Daily reported on September 16, 2026 that the
  fab had begun 2 nm trial production, including Tesla AI5.
  ([source](https://en.sedaily.com/finance/2026/09/16/samsung-starts-trial-production-of-tesla-ai-chips-in-texas))
- ESMC Dresden: topping-out ceremony on September 14, 2026; first process-tool
  installation expected in the second half of 2027.
  ([source](https://focustaiwan.tw/business/202609150007))
- Intel Ohio One: WOSU reported on August 26, 2026 that Intel says it remains
  on track to complete the first fab by 2031, with deadlines "flexible based on
  customer demand".
  ([source](https://www.wosu.org/2026-08-26/slow-progress-continues-at-intels-new-albany-semiconductor-fab-still-set-to-open-by-2031))
- Hua Hong Wuxi: on September 1, 2026, Hua Hong Grace announced a capital
  increase for a Phase III 12-inch line targeted for December 2027.
  ([source](https://www.nbd.com.cn/articles/2026-09-04/4573374.html))
- Huali Fab 6: Hua Hong Grace completed its acquisition of Shanghai Huali
  Microelectronics (the Fab 5 company) on September 11, 2026; the reviewed
  reporting does not indicate a change in Fab 6's operator.
  ([source](https://www.nbd.com.cn/articles/2026-09-11/4579395.html))
- Tata Dholera: Tata Electronics announced a collaboration with Kelington on
  September 25, 2026 to speed the fab's operational readiness.
  ([source](https://evertiq.com/design/2026-09-25-tata-electronics-kelington-to-advance-development-of-dholera-fab))
- NVIDIA Rubin: NVIDIA's Form 10-Q signed August 26, 2026 says Vera Rubin began
  production shipments in the third quarter of fiscal 2027.
  ([source](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm))
- Iluvatar CoreX: its interim results of August 28, 2026 confirm that the July
  2026 launch (TianGai 300) was TG Gen 4.
- Positron: a September 10, 2026 release says its Asimov ASIC will tape out on
  TSMC N3P at the end of 2026.

## August 25, 2026 snapshot

The original Atlas, compiled by AI agents under human direction between
August 5 and 25, 2026 and audited by fresh-context agents before release to
collaborators. Not publicly released.
