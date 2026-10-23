# 07. Verification and Evaluation Plan

---

## 1. Purpose and Scope

This plan defines **how the fulfilment of every requirement is verified** and **how the scientific results are evaluated**. It distinguishes two activities:

| Activity | Question answered | Covered in |
|----------|------------------|-----------|
| **Software verification** | Does the platform do what the requirements specify, correctly and reliably? | Sections 3–6, 9 |
| **Scientific evaluation** | How accurate are the three thresholding methods, how sensitive are they, and how do they change the isolation count (RQ, SQ1, SQ2, H1–H3)? | Sections 7–8 |

The literature review showed that validation is the weakest link of published SAR flood studies (proxy references, temporal gaps, too few points, unverifiable claims — Khanh & Le, 2026; Amoah, 2026; Johary et al., 2023; Osako, 2026; Liu et al., 2026). The evaluation design below is built specifically to avoid these weaknesses.

---

## 2. Verification Approach

### 2.1 Verification methods

| Code | Method | Used for |
|------|--------|---------|
| **T** | Test (automated) | Algorithmic correctness, API behaviour, performance |
| **A** | Analysis (quantitative experiment) | Accuracy, sensitivity, isolation comparison |
| **I** | Inspection (review of artefacts, metadata, code) | Openness, documentation, security, provenance |
| **D** | Demonstration (scripted user scenario) | UI functions, usability |

### 2.2 Test levels

| Level | ID prefix | Scope | Tooling | Environment | Execution |
|-------|----------|-------|---------|-------------|-----------|
| Unit | `UT` | Single functions/classes of processing, network and API layers; GEE replaced by NumPy reference implementations or mocks | `pytest`, `hypothesis` (property tests), `pytest-cov` | Local / CI | Every push (GitHub Actions) |
| Integration | `IT` | Interaction between components: API ↔ JobManager ↔ Orchestrator; Orchestrator ↔ GEE; Orchestrator ↔ OSM; persistence | `pytest` with markers `@gee`, `@osm`; FastAPI `TestClient`; `respx` for HTTP mocks | CI (mocked) + nightly/manual with GEE service account | Push (mocked); nightly (live) |
| System / end-to-end | `ST` | Complete run through UI and API on the pilot AOI | Playwright, `docker compose` | Staging (Docker host) | Before each release / pre-defence |
| Performance | `PT` | NFR-01 … NFR-03 | `pytest-benchmark`, `locust`, browser performance trace | Reference machine: 4 vCPU, 16 GB RAM | Before release |
| Acceptance (users) | `UAT` | Use-case scenarios with representatives of target users | Scripted tasks, SUS questionnaire | Staging | Once per major release |
| Scientific experiments | `EXP` | Accuracy, sensitivity, isolation analysis | Platform itself + `scipy`/`statsmodels` notebooks | Production configuration | Evaluation phase |

### 2.3 Test data

| Dataset | Purpose | Notes |
|---------|---------|-------|
| **Synthetic rasters** (`tests/fixtures/raster/`) | Unit tests of thresholds, masks, metrics | Bimodal/unimodal histograms with known optimum; small water fractions (5 %); 10 × 10 hand-computed confusion matrix |
| **Synthetic graphs** (`tests/fixtures/graph/`) | Unit tests of isolation | Grid and tree graphs with known isolated nodes; disconnected components |
| **Small real AOI fixture** (exported GeoTIFF + OSM extract, < 5 MB) | Integration tests without GEE | Sanitised; committed |
| **Pilot AOI — 2024 Kazakhstan flood** | System, performance and scientific tests | Live GEE and OSM data |
| **Sen1Floods11** hand-labelled chips (Bonafilia et al., 2020) | Cross-check of pipeline and metric implementation on independent labels | Subset of chips |
| **Copernicus EMS Rapid Mapping delineations** of historical floods | External validation of generality on other events | See Section 7.4 |
| **CEMS GFM observed flood extent** | Comparison with an operational product | If available for AOI/date |

---

## 3. Unit Test Plan

| ID | Component | Test | Pass criterion | Req. |
|----|-----------|------|---------------|------|
| UT-01 | Schemas & Validation | Valid/invalid AOIs (self-intersection, > 50,000 km², wrong type), date logic | Valid → model; invalid → `ValidationError` with field name | FR-01 |
| UT-02 | SceneSelector (mock catalogue) | Selection by date window, pass direction and orbit; empty window | Expected IDs returned; empty → `NoDataError` | FR-02 |
| UT-03 | TerrainMasker (NumPy impl.) | Synthetic slope/HAND/JRC rasters | Masked pixel set equals expected set exactly | FR-03 |
| UT-04 | OtsuThreshold | Synthetic bimodal histogram with analytical optimum | \|t − t*\| ≤ 0.1 dB | FR-04 |
| UT-05 | LocalAdaptiveThreshold | 5 % water image; image with no bimodal tile | \|t − t*\| ≤ 0.5 dB where global Otsu fails; fallback flag set when no tile passes | FR-05 |
| UT-06 | BaselineChangeDetection | Pixels dark in both periods vs dark only post-flood | Only post-flood darkening classified as flood | FR-06 |
| UT-07 | PolarisationCombiner | Random binary VV/VH arrays (property test, 1,000 cases) | AND = VV ∧ VH, OR = VV ∨ VH for 100 % of pixels; AND ⊆ VV, VH ⊆ OR | FR-07 |
| UT-08 | SensitivityRunner | Offsets −1/0/+1 on synthetic data | Flooded area non-decreasing with offset; 36 rows when full grid requested | FR-08 |
| UT-09 | AccuracyEvaluator | Hand-computed 10 × 10 case; all-correct; all-wrong; NoData handling | Metrics equal expected to 4 decimals; perfect map → IoU = F1 = κ = 1; excluded-pixel count correct | FR-09 |
| UT-10 | ReferenceBuilder (NumPy impl.) | MNDWI threshold; cloud coverage < 80 % | Correct water mask; refusal message when coverage < 80 % | FR-10 |
| UT-11 | RoadGraphBuilder | Snapping of settlements on synthetic graph | Nearest node correct; > 2 km flagged `no_road_access` | FR-11 |
| UT-12 | IsolationAnalyzer | Grid graph + flood polygon cutting a known set of edges; pre-disconnected node | Isolated set equals expected; pre-disconnected node not `isolated`; inundated settlement classified `inundated` | FR-12 |
| UT-13 | IsolationComparator | Identical sets; disjoint sets; partial overlap | Jaccard = 1, 0, and expected value; consensus/disputed lists correct | FR-13 |
| UT-14 | PriorityRanker | Settlements with and without population tag | Correct order; missing population shown as `unknown` | FR-14 |
| UT-15 | JobManager | State transitions, retries, time-out | Only legal transitions; 3 retries with back-off; `FAILED` after time-out | FR-16, NFR-12 |
| UT-16 | Exporters | COG and GeoJSON writers | Files valid (rasterio/RFC 7946 validator); CRS and `run_id` metadata present | FR-19, NFR-11 |

**Coverage target:** ≥ 70 % line coverage for `src/processing` and `src/backend` (NFR-09), measured in CI.

---

## 4. Integration Test Plan

| ID | Interaction | Scenario | Pass criterion | Req. |
|----|-------------|----------|---------------|------|
| IT-01 | Web Client → API → Run Registry | `POST /runs` with valid config | HTTP 202 within 2 s; run stored as `QUEUED`; `GET /runs/{id}` returns the config | FR-01, FR-15, FR-16 |
| IT-02 | API → JobManager → Orchestrator (mocked GEE/OSM) | Full run on small fixture AOI | Status sequence `QUEUED → RUNNING → SUCCEEDED`; all result endpoints return data | FR-15, FR-16 |
| IT-03 | Orchestrator ↔ GEE (live, `@gee`) | Pilot AOI: scene selection and composites | Scene list equals list obtained manually in GEE Code Editor; scene IDs stored | FR-02 |
| IT-04 | Orchestrator ↔ GEE (live) | Same terrain mask used by all methods | Identical mask hash in metadata of all masks of the run | FR-03, NFR-05 |
| IT-05 | GEE implementation vs NumPy reference | Thresholds and metrics on the small fixture exported from GEE | GEE and NumPy thresholds differ ≤ 0.05 dB; metrics differ ≤ 0.001 | FR-04 … FR-09 |
| IT-06 | Orchestrator ↔ OSM (live, `@osm`) | Graph build for pilot AOI; cache reuse | Node/edge counts and extract timestamp stored; second method reuses identical graph hash | FR-11 |
| IT-07 | Raster → vector → network | Exported flood polygons intersected with real graph | Every removed edge intersects a buffered flood polygon (spatial check on a random sample of 100 edges) | FR-12 |
| IT-08 | Reference upload → AccuracyEvaluator | Upload GeoTIFF and GeoJSON reference in different CRS | Reprojected correctly; metrics computed; CRS mismatch handled | FR-09, NFR-11 |
| IT-09 | Fault injection | Simulated transient GEE 429/500 and permanent 403; Overpass time-out | Transient → run succeeds after retry; permanent → `FAILED` with stage and message | NFR-12 |
| IT-10 | Contract tests | All endpoints against OpenAPI schema (`schemathesis`) | No schema violations; malformed inputs → 4xx, never 5xx | FR-15, NFR-08, NFR-13 |
| IT-11 | Reproducibility | Re-run stored configuration (`POST /runs/{id}/rerun`) | Pixel-wise identical masks; metrics equal to 4 decimals | FR-20, NFR-05 |

GEE-dependent tests use a dedicated service account; they run nightly and before releases rather than on every push, because they depend on an external quota.

---

## 5. System and Performance Tests

| ID | Scenario | Pass criterion | Req. |
|----|----------|---------------|------|
| ST-01 | UC-01 → UC-07 end-to-end in the browser (Playwright) on the pilot AOI | All steps succeed; map shows masks, settlements and flooded roads; exports downloadable | FR-17, FR-18, FR-19 |
| ST-02 | UC-04 reference upload + accuracy display | Dashboard values equal API values | FR-09, FR-18 |
| ST-03 | UC-05 sensitivity grid | 36 rows displayed; sortable | FR-08, FR-18 |
| ST-04 | UC-08 history and re-run | New run with identical parameters; results identical | FR-20 |
| ST-05 | Fresh deployment | Clean VM → `docker compose up` → working UI in ≤ 30 min following README | NFR-07 |
| PT-01 | Complete run (3 methods × 4 modes, Δ = 0, metrics) on pilot AOI ≤ 50,000 km² | Median of 5 runs ≤ 15 min | NFR-01 |
| PT-02 | Run with full sensitivity grid | Median of 3 runs ≤ 45 min | NFR-01 |
| PT-03 | Isolation analysis per mask on graph ≤ 250,000 edges | Median of 10 runs ≤ 60 s | NFR-02 |
| PT-04 | Load test: 10 concurrent users, 5 min, read endpoints | p95 ≤ 2 s; 0 % errors | NFR-03 |
| PT-05 | Initial map render (browser trace) | ≤ 3 s | NFR-03 |

Because GEE execution time depends on Google's shared infrastructure, PT-01/PT-02 record the time of day and repeat runs; a failure is investigated before it is accepted as a defect.

---

## 6. User Acceptance Tests

Participants: at least five representatives of the target groups (emergency services, GIS analysts, regional authority), recruited through the contacts documented in [`02_evidence_of_relevance.md`](02_evidence_of_relevance.md).

| ID | Task | Pass criterion | Req. |
|----|------|---------------|------|
| UAT-01 | "Run an analysis for the given AOI and dates and find the list of isolated settlements." | ≥ 80 % of participants complete unaided in ≤ 5 min | NFR-10, UC-01, UC-06 |
| UAT-02 | "Which settlements are isolated under all methods, and which only under some?" | ≥ 80 % answer correctly | FR-13, NFR-15 |
| UAT-03 | "Switch between the Otsu and baseline masks and identify a settlement whose status differs." | ≥ 80 % complete | FR-17 |
| UAT-04 | "Download the isolated settlements and open them in your GIS / spreadsheet." | ≥ 80 % complete | FR-19 |
| UAT-05 | System Usability Scale questionnaire | Mean SUS ≥ 68 | NFR-10 |

Qualitative feedback is recorded and turned into YouTrack issues; verified findings are distinguished from participants' suggestions.

---

## 7. Accuracy Evaluation Methodology (Scientific Evaluation)

### 7.1 Experimental design

The design follows Assignment 2 (Objectives 1–4) and controls every factor except the one under study:

| Factor | Setting |
|--------|---------|
| Event | 2024 spring floods, Kazakhstan; 1–2 pilot AOIs in the most affected regions |
| Input scenes | Identical Sentinel-1 pre- and post-flood scenes for all methods |
| Pre-processing and masks | Identical (same mask hash — IT-04) |
| Independent variable | Method ∈ {Otsu, local adaptive, baseline}; mode ∈ {VV, VH, AND, OR}; offset Δ ∈ {−1, 0, +1} dB |
| Reference | One common reference for all masks |
| Dependent variables | IoU, F1, precision, recall, Cohen's κ, flooded area; number and identity of isolated settlements |

### 7.2 Reference data for the 2024 Kazakhstan event

The lack of an independent reference is the main methodological risk. A two-tier reference is used:

1. **Primary — pixel reference map.** A Sentinel-2 L2A scene acquired within **±2 days** of the Sentinel-1 post-flood scene, cloud-free over ≥ 80 % of the AOI. Water is derived with MNDWI and a cloud/shadow mask (FR-10), then **manually reviewed and corrected** by an analyst against the imagery. Pixels under cloud are excluded. The date gap is reported, because a gap of several days is known to bias comparisons (Johary et al., 2023; Osako, 2026).
2. **Secondary — stratified sample points.** At least **600 points** stratified by (a) the union of all predicted classes (flood in any mask / flood in no mask / disputed between masks) and (b) land-cover class (cropland, grassland, bare, built-up, wetland). Each point is labelled water / non-water by visual interpretation of Sentinel-2 and high-resolution imagery by **two interpreters independently**; inter-interpreter agreement must reach κ ≥ 0.80, disagreements are resolved jointly or the point is discarded. Point-based metrics are compared with the pixel-based metrics.
3. **If a Copernicus EMS Rapid Mapping delineation or GFM product exists** for the AOI and a date within ±1 day, it is used as an additional, independent comparison layer (FR-22). Availability for the 2024 Kazakhstan floods has not been confirmed at the time of writing.

The reference is never derived from any of the masks being evaluated, avoiding the circularity identified in Bazzan et al. (2026) and Khanh and Le (2026).

### 7.3 Metrics

From the confusion matrix (TP, FP, FN, TN) over the common valid area:

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| IoU (= Critical Success Index) | TP / (TP + FP + FN) | Overlap of flood classes; insensitive to the large true-negative area |
| Precision | TP / (TP + FP) | Share of mapped flood that is real (false positives — H1, H3) |
| Recall | TP / (TP + FN) | Share of real flood that is mapped (omissions — H3) |
| F1 | 2·P·R / (P + R) | Balance of precision and recall |
| Cohen's κ | (p₀ − pₑ) / (1 − pₑ) | Agreement beyond chance |
| Overall accuracy | (TP + TN) / N | Reported for comparability only (inflated by large dry areas) |

Uncertainty: **95 % confidence intervals** for IoU and F1 by spatial block bootstrap (1,000 resamples of 1 km × 1 km blocks) to account for spatial autocorrelation. Metrics are also reported per land-cover class to locate failure zones (Liang et al., 2025).

**Targets:** best method/mode IoU ≥ 0.70 and F1 ≥ 0.80 (NFR-04). These are evaluation targets; not reaching them is a research finding, and results are reported for all methods regardless of outcome.

### 7.4 Validation strategy with historical Copernicus EMS flood maps

To show that the pipeline and its metrics generalise beyond one event and to check the implementation against expert products, the platform is additionally run on **historical flood events with published CEMS Rapid Mapping delineations**:

| Step | Description |
|------|-------------|
| 1. Event selection | Select 3–5 CEMS activations for river floods on predominantly flat agricultural terrain, where the delineation's image date is within ±1 day of a Sentinel-1 acquisition (e.g. the Storm Daniel / Thessaly 2023 event used by Falaras et al., 2025). Snowmelt events are preferred where available. |
| 2. Reference preparation | Download the CEMS "observed flood extent" vector; rasterise at 10 m; exclude areas outside the CEMS AOI and the CEMS "not analysed" zones. |
| 3. Processing | Run all methods/modes with default parameters (no re-tuning per event). |
| 4. Scoring | Compute the metrics of Section 7.3 for each event. |
| 5. Analysis | Compare method rankings across events: is the ranking from the Kazakhstan event stable? Report mean and range of IoU per method. |

This addresses the literature's main weakness — thresholds tuned and validated on one event only. CEMS maps are expert products, not field truth, so differences are interpreted as **agreement with an independent expert reference**, and the acquisition date gap is reported (Johary et al., 2023). Additionally, a subset of **Sen1Floods11** chips (hand-labelled; Bonafilia et al., 2020) is used to verify the metric implementation and method behaviour on independent labels.

### 7.5 Hypothesis testing

| Hypothesis | Test | Data | Decision rule (α = 0.05) |
|-----------|------|------|-------------------------|
| **H1** Otsu: larger area and lower precision than baseline | **McNemar's test** on paired pixel/point classifications of the two methods; one-sided comparison of precision with bootstrap CI of the difference | Reference pixels / stratified points | Reject H0 if p < 0.05 **and** precision(Otsu) < precision(baseline) with CI of the difference excluding 0 |
| **H2** Methods give different numbers of isolated settlements | **Cochran's Q test** on the paired binary status (isolated / not) of every settlement across the three methods; post-hoc pairwise McNemar with Holm correction | Settlement statuses at Δ = 0 | Reject H0 if p < 0.05 |
| **H3** OR → higher recall, AND → higher precision | **Wilcoxon signed-rank test** on per-tile recall and precision differences (OR − AND) over ≥ 30 evaluation tiles, for each method | Per-tile metrics | Reject H0 if p < 0.05 in the hypothesised direction |

**SQ1** (sensitivity) is answered descriptively by the sensitivity table (36 masks): range of IoU/F1 and flooded area across Δ for each method, compared with the 63.5–74.9 % F1 range reported by Amoah (2026).
**SQ2** is answered by (a) Spearman rank correlation between methods' IoU/F1 ranking and their isolation results, and (b) pairwise Jaccard indices of isolated-settlement sets (FR-13).

### 7.6 Evaluation of isolation results

There is no complete official list of isolated settlements for the AOI, so isolation is verified at three levels:

1. **Algorithmic correctness** — synthetic graphs with known answers (UT-12, IT-07).
2. **Plausibility against reports** — settlements reported with restricted access during the 2024 floods (e.g. the 44 settlements reported by ACAPS (2024) at national level, regional emergency-department and news reports) are matched by name to the platform's results for the AOI; matches, misses and extra detections are tabulated. This is reported as qualitative agreement, not accuracy.
3. **Visual audit** — for a random sample of 30 settlements classified `isolated` and 30 classified `connected` near the flood edge, an analyst inspects the flooded road segments on Sentinel-2/SAR imagery; the share of confirmed classifications is reported.

**Sensitivity of the isolation count** to OSM completeness: repeat the analysis after randomly removing 5 % of minor-road edges (10 repetitions) and report the variation in the count.

---

## 8. Requirement Verification Matrix

Every functional and non-functional requirement is mapped to its verification method, test(s) and acceptance evidence.

| Req. | Priority | Method | Test / experiment IDs | Evidence of fulfilment |
|------|----------|--------|----------------------|----------------------|
| FR-01 | Must | T | UT-01, IT-01 | CI report |
| FR-02 | Must | T, I | UT-02, IT-03 | CI report; scene list comparison |
| FR-03 | Must | T | UT-03, IT-04 | CI report; mask hash in metadata |
| FR-04 | Must | T | UT-04, IT-05 | CI report |
| FR-05 | Must | T | UT-05, IT-05 | CI report |
| FR-06 | Must | T | UT-06, IT-05 | CI report |
| FR-07 | Must | T | UT-07 | Property-test report |
| FR-08 | Must | T, D | UT-08, ST-03 | CI report; sensitivity table screenshot |
| FR-09 | Must | T | UT-09, IT-05, IT-08, ST-02 | CI report; Sen1Floods11 cross-check |
| FR-10 | Should | T | UT-10 | CI report |
| FR-11 | Must | T | UT-11, IT-06 | CI report; graph metadata |
| FR-12 | Must | T, A | UT-12, IT-07, Section 7.6 | CI report; isolation audit table |
| FR-13 | Must | T | UT-13, UAT-02 | CI report; UAT results |
| FR-14 | Should | T | UT-14 | CI report |
| FR-15 | Must | T, I | IT-01, IT-10 | Contract-test report; OpenAPI |
| FR-16 | Must | T | UT-15, IT-01, IT-02 | CI report |
| FR-17 | Must | D | ST-01, UAT-03 | E2E report; UAT results |
| FR-18 | Must | D, T | ST-02, ST-03 | E2E report |
| FR-19 | Must | T, D | UT-16, ST-01, UAT-04 | Validator output; QGIS check |
| FR-20 | Should | T | IT-11, ST-04 | CI / E2E report |
| FR-21 | Could | D | ST-01 (optional step) | Demo |
| FR-22 | Could | A | Section 7.2 (3) | Comparison table |
| NFR-01 | Must | T | PT-01, PT-02 | Benchmark log |
| NFR-02 | Must | T | PT-03 | Benchmark log |
| NFR-03 | Must | T | PT-04, PT-05 | Locust report; browser trace |
| NFR-04 | Should | A | EXP (Section 7.3) | Metrics table with CIs |
| NFR-05 | Must | T | IT-04, IT-11, ST-04 | Pixel-diff report |
| NFR-06 | Must | I | Licence inventory review | README licence table; licence-check output |
| NFR-07 | Must | D | ST-05 | Deployment log |
| NFR-08 | Must | T, I | IT-10, secret scan (gitleaks) in CI | CI report |
| NFR-09 | Should | T | Coverage + linters in CI | Coverage ≥ 70 % |
| NFR-10 | Should | D | UAT-01 … UAT-05 | UAT report, SUS score |
| NFR-11 | Must | T, I | UT-16, IT-08, ST-01 | Validator output |
| NFR-12 | Should | T | UT-15, IT-09 | Fault-injection report |
| NFR-13 | Must | I | IT-10; review of `/docs` | OpenAPI coverage 100 % |
| NFR-14 | Must | I | Bill of materials review | BOM document |
| NFR-15 | Should | D | UAT-02 | UAT results |

---

## 9. Continuous Integration and Quality Gates

| Stage (GitHub Actions) | Tools | Gate |
|-----------------------|-------|------|
| Lint and type check | `ruff`, `mypy` (processing), `eslint`, `tsc` (frontend) | No errors |
| Unit + mocked integration tests | `pytest`, `pytest-cov`, `vitest` (frontend) | All pass; coverage ≥ 70 % |
| Contract tests | `schemathesis` against OpenAPI | No violations |
| Security | `gitleaks`, `pip-audit` | 0 secrets; no high-severity vulnerabilities |
| Build | `docker compose build` | Images build |
| Nightly (manual secret) | Live `@gee` / `@osm` integration tests | All pass or documented external outage |

A pull request into `main` is merged only when all gates pass and one team member has reviewed it.

---

## 10. Entry and Exit Criteria, Defect Management

**Entry criteria for system testing:** all Must FRs implemented; CI green; pilot AOI configuration fixed; GEE service account available.

**Exit criteria for release / defence:**
- 100 % of Must requirements verified with passing evidence (Section 8).
- ≥ 80 % of Should requirements verified; unverified ones documented with reasons.
- No open defects of severity *critical* or *major*.
- Scientific evaluation complete: metrics with CIs for all masks, sensitivity table, hypothesis test results, isolation audit.

**Defect management:** defects are recorded in YouTrack with severity (critical / major / minor), linked requirement ID and test ID; each fix requires a regression test.

---

## 11. Schedule

| Phase | Activities | Output |
|-------|-----------|--------|
| Implementation | Unit tests written with each module (test-first for metrics and isolation) | UT-01 … UT-16 |
| Integration | IT-01 … IT-11, CI pipeline | CI reports |
| System | ST-01 … ST-05, PT-01 … PT-05 | E2E and performance reports |
| Evaluation | Reference construction, EXP accuracy, sensitivity, hypothesis tests, CEMS events, isolation audit | Evaluation chapter of the thesis |
| Acceptance | UAT-01 … UAT-05 | UAT report |

---

## References

- ACAPS. (2024, April 23). *Kazakhstan: Floods* (Briefing note). https://www.acaps.org/fileadmin/Data_Product/Main_media/20240423_ACAPS_briefing_note_Kazakhstan_floods.pdf
- Amoah, G. O. (2026). Cloud-independent flood mapping and surface water dynamics using Sentinel-1 SAR in the Lower Volta Basin, Ghana. *Geomatica, 78*, 100131. https://doi.org/10.1016/j.geomat.2026.100131
- Bazzan, T., et al. (2026). Flood detection integrating spectral indices (FLOODISI). *Geosciences, 16*(8), 325. https://doi.org/10.3390/geosciences16080325
- Bonafilia, D., Tellman, B., Anderson, T., & Issenberg, E. (2020). Sen1Floods11: A georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. *CVPR Workshops*, 210–211.
- Falaras, T., et al. (2025). Mapping of flood impacts caused by the September 2023 Storm Daniel in Thessaly's Plain (Greece). *Remote Sensing, 17*(10), 1750. https://doi.org/10.3390/rs17101750
- Johary, R., et al. (2023). Detection of large-scale floods using Google Earth Engine and Google Colab. *Remote Sensing, 15*(22), 5368. https://doi.org/10.3390/rs15225368
- Khanh, D. X., & Le, X.-H. (2026). An uncertainty-aware framework for flood extent and depth mapping from Sentinel-1 SAR. *Environmental Research Communications, 8*, 075024. https://doi.org/10.1088/2515-7620/ae88de
- Liang, J., et al. (2025). Rapid probabilistic inundation mapping using local thresholds and Sentinel-1 SAR data on Google Earth Engine. *Remote Sensing, 17*(10), 1747. https://doi.org/10.3390/rs17101747
- Liu, J., et al. (2026). Research on rapid inversion method of flood inundation extent based on fusion of multi-source remote sensing data and deep learning algorithms. *CMNM 2026*, 805–814. https://doi.org/10.1145/3832928.3833047
- Osako, L. S. (2026). Flood mapping using multi-temporal Sentinel-1 SAR images: Lower Tubarão River Sub-basin, Brazil. *ISPRS Annals, XI-3-2026*, 441–446. https://doi.org/10.5194/isprs-annals-XI-3-2026-441-2026
