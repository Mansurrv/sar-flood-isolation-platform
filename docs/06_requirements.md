# 06. Requirements Specification

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional (FR) and non-functional (NFR) requirements of the SAR Flood Mapping Platform. Every requirement has a unique identifier, a priority, a source, and **acceptance criteria that make its fulfilment verifiable**. The verification method for each requirement is detailed in [`09_verification_plan.md`](09_verification_plan.md); the components that realise each requirement are shown in [`07_architecture.md`](07_architecture.md).

### 1.2 Priority scheme (MoSCoW)

| Priority | Meaning |
|----------|---------|
| **Must** | Required to answer the research question or for the platform to be usable; the project fails without it |
| **Should** | Important; delivered unless a documented risk materialises |
| **Could** | Desirable; delivered if time allows |
| **Won't (this release)** | Explicitly excluded (see Section 7) |

### 1.3 Requirement sources

| Code | Source | Nature |
|------|--------|--------|
| RQ | Research question, sub-questions and hypotheses (Assignment 2) | Verified by research design |
| LIT | Literature review findings (Assignment 1; [`03`](03_literature_review.md)) | Verified by published evidence |
| SYS | Gaps of existing systems ([`04`](04_existing_systems_comparison.md)) | Verified by system documentation |
| USR | User evidence ([`02`](02_evidence_of_relevance.md)) and ACAPS (2024) situation report | Verified where documented in `02`; otherwise marked as assumption |
| ENG | Engineering constraints (team, time, budget, technology decisions) | Team decision |
| ASM | Team assumption not yet validated with users | **Assumption** — to be confirmed |

### 1.4 Definitions

| Term | Definition |
|------|-----------|
| **AOI** | Area of interest: polygon in EPSG:4326 for which an analysis is run |
| **Run** | One execution of the pipeline for one AOI, one pre-flood period, one post-flood date window and one parameter set; identified by a `run_id` |
| **Flood mask** | Binary raster (1 = flood water, 0 = no flood water, NoData = masked) at 10 m pixel spacing, excluding permanent water |
| **Method** | One of: `otsu` (global Otsu), `local` (tile-based adaptive Otsu with bimodality check), `baseline` (change detection: post-flood minus pre-flood backscatter, calibrated threshold) |
| **Polarisation mode** | `VV`, `VH`, `AND` (water if VV and VH both below their thresholds), `OR` (water if either is below) |
| **Threshold offset** | Δ ∈ {−1, 0, +1} dB added to the method's threshold for sensitivity analysis |
| **Reference mask** | Independent binary water map used as ground truth (see verification plan) |
| **Hub** | Reference node of the road graph that represents access to services: regional and district administrative centres located in or adjacent to the AOI (configurable list) |
| **Isolated settlement** | A settlement whose nearest road-graph node was connected to at least one hub in the pre-flood graph **G**, but has no path to any hub in the flood-affected graph **G′**, where **G′** is **G** with every edge removed whose geometry intersects the flood polygon (buffered by 10 m) |
| **Inundated settlement** | A settlement whose point location lies inside the flood polygon (reported separately from isolation) |
| **Metrics** | IoU = TP/(TP+FP+FN); Precision = TP/(TP+FP); Recall = TP/(TP+FN); F1 = 2PR/(P+R); Cohen's κ from the 2×2 confusion matrix |

---

## 2. Stakeholders and Actors

| Actor | Description | Main goals |
|-------|-------------|-----------|
| **Emergency planner** (Ministry of Emergency Situations / regional emergency department) | Primary user; limited GIS skills | Obtain a list and map of isolated settlements quickly |
| **GIS analyst / researcher** | Advanced user | Configure methods, compare accuracy, run sensitivity analyses, export data |
| **Regional authority representative** (akimat, road administration) | Occasional viewer | View affected roads and settlements; download data |
| **Google Earth Engine** (external system) | Provides Sentinel-1, DEM, HAND, JRC water, Sentinel-2 data and computation | — |
| **OpenStreetMap / Overpass API** (external system) | Provides roads and settlements | — |

---

## 3. Functional Requirements

### 3.1 Analysis configuration and data acquisition

| ID | Requirement | Priority | Source | Acceptance criteria |
|----|-------------|----------|--------|--------------------|
| **FR-01** | **AOI and period definition.** The user shall define a run by an AOI (drawn on the map or uploaded as GeoJSON), a pre-flood reference period and a post-flood date window. | Must | RQ, SYS (CEMS activation dependency) | (1) AOI can be drawn as polygon or uploaded as a valid GeoJSON Polygon/MultiPolygon. (2) Invalid geometries, AOI > 50,000 km², or post-flood window before the pre-flood period are rejected with HTTP 422 and a readable message. (3) The accepted configuration is stored in the run registry and returned by `GET /runs/{id}`. |
| **FR-02** | **Sentinel-1 retrieval and pre-processing.** The system shall select Sentinel-1 GRD IW scenes (VV+VH) covering the AOI for both periods, use the same relative orbit/pass direction for pre- and post-flood images where available, apply a speckle filter, and build pre-flood (median) and post-flood composites in dB. | Must | LIT (Johary 2023; Lee 1980), RQ (O1) | (1) The run metadata lists the IDs, dates, orbit number and pass direction of every scene used. (2) If no post-flood scene exists in the window, the run fails with status `NO_DATA` and the message names the window. (3) On a test AOI with known scenes, the selected scene list matches the list obtained manually in the GEE Code Editor. |
| **FR-03** | **Terrain and permanent-water masking.** The system shall mask pixels with slope > 5°, HAND > 15 m (configurable), and permanent water (JRC Global Surface Water occurrence ≥ 80 %), identically for all methods. | Must | LIT (Nobre 2011; Pekel 2016; Amoah 2026; Falaras 2025) | (1) Mask parameters are recorded per run. (2) For a synthetic test raster, masked pixels equal the expected set exactly. (3) The same mask image ID/hash is used by all methods of one run (verified in metadata). |

### 3.2 Flood detection methods

| ID | Requirement | Priority | Source | Acceptance criteria |
|----|-------------|----------|--------|--------------------|
| **FR-04** | **Global Otsu thresholding.** The system shall compute a threshold per polarisation by Otsu's method on the AOI histogram of the post-flood composite and classify water below it. | Must | RQ (O1), LIT (Otsu 1979; Falaras 2025) | (1) On a synthetic bimodal test image with known optimum, the computed threshold is within ±0.1 dB of the analytical value. (2) The threshold value per polarisation is stored in run results. |
| **FR-05** | **Local (adaptive) thresholding.** The system shall split the AOI into tiles (default 0.1° × 0.1°), compute Otsu thresholds only on tiles passing a bimodality test (Ashman's D ≥ 2 or equivalent), and derive the threshold from the accepted tiles (default: median). | Must | RQ (O1), LIT (Chini 2017; Twele 2016; Liang 2025) | (1) Number of tested and accepted tiles and the resulting threshold are stored. (2) If no tile passes the test, the method falls back to global Otsu and records `fallback=true`. (3) Unit test on a synthetic image with a small water fraction (5 %) returns a threshold within ±0.5 dB of the true separation, where global Otsu does not. |
| **FR-06** | **Baseline-calibrated change detection.** The system shall compute the difference (post − pre, dB) and classify water where the difference is below a calibrated threshold and the post-flood backscatter is below an absolute cap. | Must | RQ (O1), LIT (Khanh & Le 2026; Johary 2023) | (1) Default threshold and cap are documented and configurable via API. (2) Pixels that are dark in both periods (permanent dark surfaces) are not classified as flood in a synthetic test. |
| **FR-07** | **Polarisation logic.** For each method the system shall produce masks for VV, VH, AND and OR modes. | Must | RQ (SQ1, H3), LIT (Amoah 2026; Khanh & Le 2026) | (1) For synthetic inputs, AND mask = VV ∧ VH and OR mask = VV ∨ VH pixel-wise (100 % agreement). (2) All four modes are available in API and UI. |
| **FR-08** | **Sensitivity analysis.** The system shall, on request, re-run each method with threshold offsets of −1, 0 and +1 dB for each polarisation mode (up to 3 × 3 × 4 = 36 masks) and tabulate area and accuracy metrics. | Must | RQ (SQ1, O3), LIT (Amoah 2026) | (1) The sensitivity table contains one row per (method, offset, mode) with flooded area (km²) and, if a reference exists, IoU, F1, precision, recall. (2) Flooded area is monotonically non-decreasing with increasing offset for every method/mode (property test). |

### 3.3 Accuracy assessment

| ID | Requirement | Priority | Source | Acceptance criteria |
|----|-------------|----------|--------|--------------------|
| **FR-09** | **Accuracy evaluation.** Given a reference mask (uploaded GeoTIFF/GeoJSON or a reference generated within GEE), the system shall compute the confusion matrix, IoU, precision, recall, F1 and Cohen's κ for every mask over the common valid area. | Must | RQ (O2), LIT (validation weaknesses) | (1) For a hand-computed 10 × 10 test case, all metrics equal expected values to 4 decimal places. (2) Pixels masked in either the prediction or the reference are excluded and their count is reported. (3) Results are retrievable via `GET /runs/{id}/metrics` and exportable as CSV. |
| **FR-10** | **Reference generation support.** The system should generate a candidate reference water mask from a Sentinel-2 scene (MNDWI threshold, cloud mask) acquired within ±2 days of the SAR scene, for analyst review. | Should | LIT (Amoah 2026; Osako 2026 — temporal gap problem), ASM | (1) The candidate is generated only if cloud-free coverage of the AOI ≥ 80 %; otherwise the user is informed. (2) The date gap to the SAR acquisition is displayed and stored. |

### 3.4 Road network and isolation

| ID | Requirement | Priority | Source | Acceptance criteria |
|----|-------------|----------|--------|--------------------|
| **FR-11** | **Road graph and settlements.** The system shall build a drivable road graph from OpenStreetMap for the AOI (+ 10 km buffer) and extract settlements (`place = city, town, village, hamlet`) and hubs. | Must | RQ (O4), LIT (Boeing 2017; Falaras 2025) | (1) Graph node/edge counts, OSM extract timestamp and settlement count are stored. (2) Every settlement is snapped to its nearest graph node; the snapping distance is stored and settlements > 2 km from any road are flagged `no_road_access`. (3) The graph is cached per AOI and reused across methods of one run (identical hash). |
| **FR-12** | **Isolation analysis.** For every flood mask the system shall remove flooded edges and determine isolated and inundated settlements according to the definitions in Section 1.4. | Must | RQ (O4, H2), USR (ACAPS 2024: 44 settlements with restricted access), SYS (no system offers it) | (1) On a synthetic grid graph with a known flood polygon, the set of isolated settlements equals the expected set exactly. (2) Each result lists settlement name, OSM ID, coordinates, status (`isolated`, `inundated`, `connected`, `no_road_access`) and number of removed edges. (3) Settlements already disconnected in **G** are never reported as isolated. |
| **FR-13** | **Comparison of isolation results across methods.** The system shall compare the isolated-settlement sets of all masks: counts per method, pairwise Jaccard index, and settlements isolated under all / only some methods. | Must | RQ (SQ2, H2) | (1) Jaccard values are within [0, 1] and equal 1 for identical sets (unit test). (2) A "consensus" list (isolated under all three methods at Δ = 0) and a "disputed" list are produced. |
| **FR-14** | **Priority list.** The system should rank isolated settlements by an indicator (default: OSM population tag if present, otherwise settlement class) and the shortest pre-flood road distance to the nearest hub. | Should | USR (evacuation priorities), ASM | (1) The ranked list is sortable in the UI and exported in CSV. (2) Missing population values are shown as "unknown", never as 0. |

### 3.5 User interface, API and outputs

| ID | Requirement | Priority | Source | Acceptance criteria |
|----|-------------|----------|--------|--------------------|
| **FR-15** | **REST API.** All functions shall be available through a versioned REST API (`/api/v1`) with JSON/GeoJSON payloads. | Must | SYS (C10), ENG (TD-2, TD-5) | (1) Each FR-01 … FR-14 function has at least one documented endpoint in the OpenAPI specification. (2) Contract tests for every endpoint pass. |
| **FR-16** | **Asynchronous run management.** Starting a run shall return immediately with a `run_id`; the user can query status (`QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `NO_DATA`) and progress per stage. | Must | ENG (TD-5), NFR-01 | (1) `POST /runs` responds with HTTP 202 within 2 s. (2) Status transitions follow the defined state machine (test). (3) Failed runs store an error message and stage. |
| **FR-17** | **Map visualisation.** The web interface shall display the AOI, flood masks per method/mode/offset, the reference mask, flooded road segments and settlements coloured by status, with layer toggling and a legend. | Must | USR, SYS (C9) | (1) A user can switch between all masks of a finished run without reloading the page. (2) Clicking a settlement shows name, status and per-method status. (3) Verified in UI acceptance test UAT-03. |
| **FR-18** | **Results dashboard.** The interface shall show the metrics table, sensitivity table and isolation comparison (counts, Jaccard, consensus/disputed lists). | Must | RQ, USR | (1) Values displayed equal those returned by the API (UI test). (2) Tables can be sorted by any metric. |
| **FR-19** | **Export.** The user shall be able to download masks (Cloud-Optimized GeoTIFF), flood polygons and settlements (GeoJSON and GeoPackage) and tables (CSV) for any finished run. | Must | SYS (C10), USR (authorities' GIS) | (1) Exported rasters open in QGIS with correct CRS and extent. (2) GeoJSON validates against RFC 7946. (3) Every export includes `run_id` and parameters in metadata or a sidecar JSON. |
| **FR-20** | **Run history and reproduction.** The user should be able to list past runs and re-run a past configuration with one action. | Should | NFR-05 | (1) Re-running a configuration produces a new `run_id` with identical parameters. (2) Results meet NFR-05. |
| **FR-21** | **Side-by-side comparison view.** The interface could offer a swipe or split view comparing two masks. | Could | USR, ASM | (1) Two masks can be selected and compared in a swipe view. |
| **FR-22** | **Comparison with CEMS GFM.** The system could load the CEMS GFM observed-flood-extent product for the same date as an additional comparison layer and score it with FR-09. | Could | SYS (S2 as baseline) | (1) GFM extent is displayed and scored when the product is available for the AOI/date. |

---

## 4. Non-Functional Requirements

| ID | Category | Requirement | Priority | Source | Acceptance criteria (measurable) |
|----|----------|-------------|----------|--------|----------------------------------|
| **NFR-01** | Performance — processing | A complete run (pre-processing, 3 methods × 4 polarisation modes at Δ = 0, metrics) for an AOI ≤ 50,000 km² shall finish within **15 minutes**; a run including the full sensitivity grid (36 masks) within **45 minutes**. | Must | LIT (Johary 2023: 30 scenes < 1 h), USR (rapid response) | Median of 5 runs on the pilot AOI, measured from `RUNNING` to `SUCCEEDED` timestamps, ≤ 15 min (≤ 45 min with grid). |
| **NFR-02** | Performance — isolation | Isolation analysis (FR-12) for one mask on a graph of ≤ 250,000 edges shall complete in **≤ 60 s**. | Must | ENG (TD-4) | Benchmark test on the pilot AOI graph; median of 10 runs ≤ 60 s on the reference machine (4 vCPU, 16 GB RAM). |
| **NFR-03** | Performance — API / UI | Read endpoints (status, metrics, isolation lists) shall respond in **≤ 2 s at p95**; map tiles shall render in **≤ 3 s** for the initial view. | Must | USR (usability under time pressure) | Load test with 10 concurrent users for 5 minutes: p95 latency ≤ 2 s; browser performance trace for initial map ≤ 3 s. |
| **NFR-04** | Accuracy (target) | The best-performing method/mode on the 2024 Kazakhstan reference shall reach **IoU ≥ 0.70 and F1 ≥ 0.80**. A stretch goal of IoU ≥ 0.80 is classed as Could. | Should | LIT (Gerčer 2026: mean IoU ≈ 0.70; CEMS GFM requirement CSI ≥ 70 % — CSI equals IoU for binary maps) | Computed with FR-09 on the independent reference; results reported for all methods regardless of outcome. *Rationale for Should:* the comparison itself is the research outcome; failing the target is a finding, not a defect. |
| **NFR-05** | Reproducibility | Re-running a stored configuration shall reproduce identical masks and metrics. | Must | LIT (incomparable, unverifiable results — Liu 2026; Bazzan 2026), RQ | Pixel-wise agreement = 100 % and metrics equal to 4 decimals across two runs with identical parameters and input scene IDs. All parameters, scene IDs, OSM extract timestamp and software version stored per run. |
| **NFR-06** | Openness | Only openly licensed data (Sentinel-1/2, JRC GSW, MERIT Hydro/DEM, OSM) and open-source libraries shall be used, except GEE (free research tier). | Must | ENG, SYS (C4) | Licence inventory in README; automated dependency licence check passes. |
| **NFR-07** | Portability / deployability | The platform shall start with a single `docker compose up` on a clean machine with Docker installed. | Must | ENG (TD-3, TD-5) | Fresh-VM test: from clone to running UI ≤ 30 min following README, with no manual steps other than providing GEE credentials. |
| **NFR-08** | Security | No credentials shall be stored in the repository; GEE service-account keys are provided via environment variables / mounted secrets; the API validates all inputs. | Must | ENG | Secret-scanning (e.g. gitleaks) reports 0 findings in CI; malformed input fuzz tests return 4xx, never 5xx. |
| **NFR-09** | Maintainability / testability | Processing and backend modules shall have automated tests with **≥ 70 % line coverage**; code passes linting (ruff) and type checks (mypy) for the processing package. | Should | ENG | Coverage report in CI ≥ 70 %; linters exit with code 0. |
| **NFR-10** | Usability | Emergency-planner users shall be able to launch a run and obtain the isolated-settlement list without assistance. | Should | USR | Usability test with ≥ 5 participants: ≥ 80 % complete task UAT-01 unaided in ≤ 5 min; mean SUS score ≥ 68. |
| **NFR-11** | Interoperability | Outputs shall use standard formats (COG, GeoJSON RFC 7946, GeoPackage, CSV) and declare CRS (EPSG:4326 for vectors; EPSG:4326 or UTM zone for rasters). | Must | USR (authorities' GIS), SYS | Exports open in QGIS without warnings; CRS present in every file. |
| **NFR-12** | Reliability | Transient GEE/Overpass errors shall be retried up to 3 times with exponential back-off; any unrecoverable failure shall leave the run in `FAILED` with a diagnostic message; no run remains `RUNNING` indefinitely (time-out 60 min). | Should | ENG (TD-5) | Fault-injection tests: simulated transient error → run succeeds; simulated permanent error → `FAILED` with message within the time-out. |
| **NFR-13** | Documentation | The API shall be self-documented via OpenAPI; the methods (thresholds, defaults, definitions) shall be documented in the repository. | Must | ENG | `/docs` page lists 100 % of endpoints with schemas; method documentation reviewed by supervisor. |
| **NFR-14** | Cost | The platform shall run without paid licences or paid cloud services for the scope of the case study. | Must | ENG | Bill of materials shows zero licence cost. |
| **NFR-15** | Transparency of uncertainty | Results shall show, for each settlement, whether its status is consistent across methods, and flag settlements in urban/low-confidence areas. | Should | LIT (urban failure zones — Liang 2025; GFM exclusion mask) | Consensus/disputed flag and low-confidence flag present in UI and exports. |

---

## 5. Requirements Traceability

### 5.1 Objectives → requirements

| Objective (Proposal §7) | Requirements |
|------------------------|-------------|
| O1 Implement three methods under identical conditions | FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, NFR-05 |
| O2 Compare masks against one reference | FR-09, FR-10, NFR-04 |
| O3 Sensitivity (±1 dB, AND/OR) | FR-07, FR-08 |
| O4 Isolated settlements per mask; effect of accuracy differences | FR-11, FR-12, FR-13, FR-14 |
| O5 REST API | FR-15, FR-16, NFR-13 |
| O6 Web interface | FR-17, FR-18, FR-19, FR-21, NFR-10 |
| O7 Reproducibility and verifiability | FR-20, NFR-05, NFR-07, NFR-09 |

### 5.2 Hypotheses → requirements that produce the evidence

| Hypothesis | Evidence produced by |
|-----------|---------------------|
| H1 Otsu: larger area, lower precision than baseline | FR-04, FR-06, FR-09 |
| H2 Different numbers of isolated settlements | FR-12, FR-13 |
| H3 OR → higher recall; AND → higher precision | FR-07, FR-08, FR-09 |

### 5.3 Use cases → requirements

| Use case | Requirements |
|----------|-------------|
| UC-01 Configure and launch analysis run | FR-01, FR-02, FR-03, FR-15, FR-16 |
| UC-02 Monitor run status | FR-16, NFR-12 |
| UC-03 Inspect flood masks on the map | FR-04 … FR-07, FR-17, FR-21 |
| UC-04 Provide/generate reference and evaluate accuracy | FR-09, FR-10, FR-22 |
| UC-05 Run sensitivity analysis | FR-08, FR-18 |
| UC-06 View isolated settlements and priority list | FR-11 … FR-14, FR-17 |
| UC-07 Export results | FR-19 |
| UC-08 Browse and reproduce past runs | FR-20, NFR-05 |

---

## 6. Constraints and Assumptions

| ID | Constraint / assumption | Type |
|----|------------------------|------|
| C-1 | Processing depends on Google Earth Engine availability, quotas and non-commercial terms | Constraint |
| C-2 | In 2024 only Sentinel-1A was operating (12-day repeat per orbit); post-flood scene availability is limited | Constraint |
| C-3 | Team of two; one academic year; no budget | Constraint |
| A-1 | OSM road coverage in the pilot AOIs is sufficient for regional and district roads (to be checked before analysis) | **Assumption** |
| A-2 | A cloud-free Sentinel-2 scene within ±2 days of a Sentinel-1 post-flood acquisition exists for at least one pilot AOI; otherwise manual interpretation of stratified sample points is used | **Assumption** |
| A-3 | A road segment intersecting flood water is impassable (no water-depth threshold) | **Assumption** (conservative; documented limitation) |
| A-4 | Administrative centres are appropriate hubs for "access to services" | **Assumption** — to be confirmed with user representatives (`02`) |

---

## 7. Out of Scope (Won't in this release)

- Machine-learning classifiers; flood depth; hydrodynamic modelling or forecasting.
- Automatic triggering on new Sentinel-1 acquisitions; real-time streaming.
- User accounts, authentication and role management; mobile application.
- National-scale operational deployment.

---

## References

- ACAPS. (2024, April 23). *Kazakhstan: Floods* (Briefing note).
- EODC. (n.d.). *GFM Product User Manual – Technical overview*. https://extwiki.eodc.eu/GFM/PUM/TechnicalOverview
- All scientific sources as listed in [`03_literature_review.md`](03_literature_review.md).
