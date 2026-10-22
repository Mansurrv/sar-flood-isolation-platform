# 01. Project Proposal — SAR Flood Mapping Platform

> **Branch:** `DIP-1-project-proposal` · **File:** `docs/01_project_proposal.md`
> **Research basis:** Assignment 1 (Research Topic Selection and Literature Review) and Assignment 2 (Developing a Research Question), Aitynbek & Serikbai, group SE-2423.

---

## 1. Project Identification

| Item | Value |
|------|-------|
| **Project title** | SAR Flood Mapping Platform |
| **Full research title** | Comparing Thresholding Algorithms for Sentinel-1 SAR Flood Mapping and Their Effect on Settlement Isolation: A Case Study of the 2024 Kazakhstan Floods |
| **Repository** | `sar-flood-isolation-platform` |
| **Programme / group** | Software Engineering, SE-2423 |
| **Project type** | Research-driven software engineering project (applied remote sensing + geospatial web platform) |

### 1.1 Team Members

| Member | Role | Main responsibilities |
|--------|------|-----------------------|
| **Nurdaulet Aitynbek** | Web Platform Development Lead (Full-stack / Backend Engineer) | System architecture; FastAPI REST API and asynchronous job management; run registry and result storage; React + Leaflet web interface; integration of the processing pipeline into the platform; Docker Compose deployment; CI and automated testing |
| **Mansur Serikbai** | Geospatial / Data Engineer | Google Earth Engine pipeline; Sentinel-1 pre-processing and terrain masking; Otsu, local (adaptive) and baseline-calibrated thresholding; sensitivity analysis; accuracy metrics and reference data; OpenStreetMap road graph and settlement isolation analysis |

### 1.2 Supervisor

| Item | Value |
|------|-------|
| **Supervisor** | Alua Myrzakerimova |
| **Supervisor's role** | Methodological guidance, review of the research design and documentation, acceptance of deliverables at each pre-defence |

---

## 2. Background and Context

Floods are among the most frequent and damaging natural hazards. In spring 2024 Kazakhstan experienced one of its largest floods in decades: flooding started on 27 March, a state of emergency was declared on 6 April and eventually covered 10 of the country's 17 regions (Abai, Akmola, Aktobe, Atyrau, Karaganda, Kostanay, North Kazakhstan, Pavlodar, Ulytau and West Kazakhstan). By 19 April about 118,200 people had been evacuated, about 6,000 homes were flooded, and **access to 44 settlements was restricted because of damaged roads and bridges**; more than 60 road overflows, 63 washouts and ten collapsed bridges were reported (ACAPS, 2024). This last figure is the operational core of the project: responders need to know not only *where the water is*, but *which settlements can no longer be reached by road*.

Satellite Earth observation is the only practical way to map flood extent over areas of this size. Optical sensors (Sentinel-2, Landsat) are, however, blocked by the clouds that accompany flood-producing weather; Gerčer et al. (2026) abandoned Sentinel-2 for this reason and Falaras et al. (2025) had to discard several optical acquisitions. **Synthetic Aperture Radar (SAR)** is an active microwave sensor that images through cloud, day and night. Calm open water reflects the radar pulse away from the sensor (specular reflection) and therefore appears dark, which makes threshold-based water detection on Sentinel-1 backscatter the standard rapid-mapping technique (Liang et al., 2025; Amoah, 2026; Johary et al., 2023).

---

## 3. Problem Statement

The project addresses two linked problems identified in the literature review (Assignment 1, Sections 3 and 6).

**Problem 1 — The flood map depends on an arbitrarily chosen threshold.** There is no agreed method for selecting the backscatter threshold that separates water from land:

- In Amoah (2026), shifting the VV/VH thresholds by ±1 dB changed F1 from **63.5 % to 74.9 %**.
- Global Otsu thresholding **overestimated** the flooded area on a large rural plain and required manual correction by a multiple of the histogram standard deviation (Falaras et al., 2025); Amoah (2026) also obtained larger water areas with Otsu (7.676 km² VV, 7.129 km² VH) than with a fixed rule (5.868 km²).
- Khanh and Le (2026) name threshold selection as the **dominant source of uncertainty**.
- Every reviewed team calibrates its threshold on its own event, so the published accuracies are not comparable. No study runs Otsu, local (adaptive) and baseline-calibrated thresholds on the **same** flood with the **same** reference, and none compares AND versus OR logic for the VV and VH polarisations on the same data.

**Problem 2 — Flood maps stop at the water polygon.** Existing studies report flooded area in km², affected land cover, built-up exposure or, at most, the length of affected roads (449.16 km in Falaras et al., 2025). **None of the ten reviewed papers tests whether the road network remains connected**, i.e. which settlements are cut off. Yet this is exactly the information emergency services need to set evacuation and supply priorities.

**Consequence.** An emergency analyst who runs a Sentinel-1 threshold today cannot know (a) how much the chosen method biases the flooded area, nor (b) how that bias propagates into the list of isolated settlements that drives the response. Without automation, producing such a list requires manual GIS work (downloading scenes, thresholding, overlaying roads, tracing routes) that takes days, while rapid response needs results within hours to days.

> **Problem statement (one sentence).** Cloud cover makes optical flood mapping unreliable at the flood peak, and the Sentinel-1 SAR alternative depends on an unstandardised threshold choice whose effect on the most decision-relevant output — the set of settlements isolated from the road network — has never been measured; there is no open, automated tool that produces and compares such results for Kazakhstan.

---

## 4. Target Users and Stakeholders

| User group | Need | How the platform serves it |
|------------|------|---------------------------|
| **Emergency services** (Ministry of Emergency Situations of the Republic of Kazakhstan, regional emergency departments) | A prioritised list of settlements cut off by flood water, available quickly and in any weather | Automated Sentinel-1 flood mask + road-network isolation analysis; exportable list and map of isolated settlements |
| **GIS analysts and remote-sensing researchers** | Comparable, reproducible thresholding methods with transparent accuracy metrics | Three methods run under identical conditions; IoU, F1, Cohen's κ, precision, recall; sensitivity analysis; logged parameters |
| **Regional and local authorities** (akimats, road administration) | Evidence for road and infrastructure planning; identification of chronically vulnerable road links | Maps of flooded road segments and lost connections; GeoJSON / CSV exports for their own GIS |
| **Academic community** (secondary) | Open benchmark for spring-flood mapping on flat terrain | Open code, open data, documented methodology |

User evidence (interviews and discussions with representatives of these groups) is documented separately in [`02_evidence_of_relevance.md`](02_evidence_of_relevance.md). Findings that are verified by user evidence are distinguished there from assumptions made by the team.

---

## 5. Research Question

**Primary research question (RQ).** To what extent do Otsu, local (adaptive) and baseline-calibrated thresholding of Sentinel-1 data differ in flood-mapping accuracy (IoU, F1, κ) and in the number of settlements assessed as isolated from the OpenStreetMap road network during the 2024 spring floods in Kazakhstan?

- **SQ1.** How sensitive are the accuracy and false positives of each method to a ±1 dB threshold shift and to AND versus OR logic for VV and VH?
- **SQ2.** Do the methods ranked highest by IoU and F1 also identify the same isolated settlements?

**Hypotheses** (from Assignment 2, Section 7):

| ID | Hypothesis | Null hypothesis |
|----|------------|-----------------|
| H1 | Otsu yields a larger flooded area and lower precision than the baseline-calibrated method against the same reference | No difference in precision |
| H2 | The three methods yield different numbers of isolated settlements | The number of isolated settlements is the same for all three |
| H3 | At the same threshold, OR logic gives higher recall and AND logic higher precision | Recall and precision do not differ between OR and AND |

---

## 6. Aim

To design, implement and evaluate an open, automated web platform that maps flood extent from Sentinel-1 SAR imagery with three alternative thresholding algorithms and determines which settlements are isolated from the road network, and to use it to investigate how the choice of thresholding algorithm affects flood-mapping accuracy and the number of isolated settlements during the 2024 spring floods in Kazakhstan.

---

## 7. Objectives

The objectives combine the research objectives of Assignment 2 (O1–O4) with the engineering objectives needed to deliver them as a platform (O5–O7). Each objective is traceable to requirements in [`06_requirements.md`](06_requirements.md).

| ID | Objective | Measurable result |
|----|-----------|-------------------|
| **O1** | Implement Otsu, local (adaptive) and baseline-calibrated thresholding on Sentinel-1 GRD data of the 2024 flood in GEE, with identical pre-processing, terrain mask and input scenes for all three methods | Three flood masks per study area, generated by one parameterised pipeline |
| **O2** | Compare the three masks against one common reference | IoU, F1, Cohen's κ, precision, recall and confusion matrix per method |
| **O3** | Examine the sensitivity of each method to a ±1 dB threshold shift and to AND vs OR polarisation logic | Sensitivity table: metrics for each method × {−1, 0, +1 dB} × {VV, VH, AND, OR} |
| **O4** | Determine the settlements isolated from the OpenStreetMap road network under each mask and test whether accuracy differences change the isolation count | Isolated-settlement list per method; agreement (Jaccard) between lists |
| **O5** | Expose the pipeline through a documented REST API | FastAPI service with OpenAPI specification |
| **O6** | Provide a web map interface for running analyses and inspecting results | React + Leaflet single-page application |
| **O7** | Ensure reproducibility and verifiability | Parameter-logged runs, automated tests, Docker Compose deployment |

---

## 8. Expected Outcomes

**Research outcomes**

1. A controlled, like-for-like comparison of three thresholding families on one spring-flood event over flat, open terrain — a setting not tested in any reviewed study.
2. Quantified sensitivity of each method to ±1 dB threshold shifts and to AND/OR polarisation logic.
3. The first measurement (to the authors' knowledge, within the reviewed literature) of how the flood-mapping method changes the **number and identity of isolated settlements**.
4. Accept/reject decisions on hypotheses H1–H3.

**Engineering outcomes**

1. A reproducible processing pipeline (GEE Python API + OSMnx/NetworkX) that can be re-run for the next flood by changing the area of interest and dates.
2. A REST API (FastAPI) and a web map application (React + Leaflet).
3. Exportable products: flood masks (GeoTIFF), flood polygons and isolated settlements (GeoJSON / GeoPackage), metrics and isolation tables (CSV).
4. Complete engineering documentation: requirements, architecture, technology decisions and a verification plan.

**Practical outcome.** A list of settlements to prioritise, instead of only a flooded area in km². As Johary et al. (2023) note, in an emergency speed matters more than the last percentage point of accuracy, which makes a fast, transparent threshold-based platform a reasonable operational tool.

---

## 9. Engineering Complexity

The project is not a CRUD application; its difficulty lies in geospatial and hydrological data processing:

| Area | Source of complexity |
|------|---------------------|
| **SAR signal processing** | Speckle noise, conversion to decibels, separate VV and VH channels, orbit/incidence-angle consistency between pre- and post-flood scenes; Sentinel-1B was lost in December 2021, so in 2024 only Sentinel-1A was available with a 12-day repeat cycle per orbit, which constrains scene selection |
| **Hydrological / terrain masking** | Removal of false positives on slopes and in radar shadow using a DEM-derived slope mask and Height Above Nearest Drainage (HAND); separation of flood water from permanent water bodies (JRC Global Surface Water) |
| **Algorithm design** | Three thresholding families with different statistical assumptions (global bimodal histogram, local tile-based histograms, change detection against a dry baseline); parameterised polarisation logic |
| **Accuracy assessment** | Construction of an independent reference; pixel-level confusion matrices over millions of pixels; statistical comparison of methods |
| **Network analysis** | Conversion of OSM data into a routable graph; intersection of road geometries with raster-derived flood polygons; reachability analysis from each settlement to reference hubs on graphs with up to hundreds of thousands of edges |
| **System integration** | Long-running cloud computations (GEE) orchestrated asynchronously behind a REST API; coordinate reference system consistency; large raster/vector outputs delivered to a web map |

---

## 10. Project Scope

### 10.1 In scope

- Sentinel-1 GRD (IW mode, VV + VH) data accessed through Google Earth Engine.
- Case study: 2024 spring floods in Kazakhstan; one or two pilot areas of interest (AOIs) in the most affected regions (e.g. Kostanay, Akmola, Aktobe, West Kazakhstan, North Kazakhstan).
- Pre-processing: speckle filtering, dB conversion, slope/HAND terrain mask, permanent-water mask.
- Three thresholding methods: global Otsu, local (adaptive, tile-based) and baseline-calibrated change detection.
- Sensitivity analysis: ±1 dB shift; VV, VH, AND, OR logic.
- Accuracy assessment against one common reference (see risks below).
- OSM road graph and settlement extraction; isolation analysis per mask; comparison of isolated-settlement lists.
- FastAPI REST API, React + Leaflet web interface, exports, Docker Compose deployment.

### 10.2 Out of scope

- Machine-learning / deep-learning classifiers (Random Forest, U-Net) — discussed in the literature review but not implemented, because rapid response rarely has training data (Amer, 2025; Gerčer et al., 2026).
- Optical (Sentinel-2) imagery as the primary flood data source; it may only be used to build the reference.
- Flood depth estimation, hydrodynamic modelling and flood forecasting.
- Real-time streaming / automatic triggering on every new Sentinel-1 acquisition.
- User authentication, multi-tenant management and a mobile application.
- Field validation campaigns.

### 10.3 Why the scope is realistic

- **Data and compute are free and open:** Sentinel-1, DEMs and JRC water data are in the GEE catalogue; roads and settlements come from OpenStreetMap. Johary et al. (2023) processed 30 Sentinel-1 scenes covering Madagascar in under one hour in GEE, which shows the computational load is manageable.
- **One event, one country, three methods** keep the experiment bounded.
- **Threshold methods need no training data**, so there is no labelling effort.
- **The isolation step is algorithmically simple** (graph reachability), so engineering effort can go into robustness and integration.
- The team has defined a fallback for each major risk (Section 11).

### 10.4 Assumptions and constraints

- A GEE account (non-commercial / research access) is available to the team.
- OSM road coverage in the pilot AOIs is adequate for regional and district roads; completeness is checked before analysis.
- Working definition of isolation: *a settlement is isolated when no road path that avoids flooded segments connects it to a reference node (e.g. the district or regional centre)*. The final definition is fixed in the requirements and verification documents.

---

## 11. Key Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| No independent reference flood map for the 2024 Kazakhstan event (availability of a Copernicus EMS delineation for these AOIs has not been confirmed) | Accuracy metrics cannot be computed | Reference from a cloud-free Sentinel-2 scene close to the SAR date (MNDWI) plus manual interpretation of stratified sample points; validate the pipeline additionally on events with labelled data (Sen1Floods11, CEMS delineations) |
| Temporal gap between SAR and reference acquisitions | Disagreement caused by water level change, not by the method (cf. Johary et al., 2023) | Restrict the reference to ≤ 2 days from the SAR acquisition; report the gap |
| Single Sentinel-1 satellite (12-day repeat) in 2024 | Few post-event scenes | Combine ascending and descending passes; choose AOIs with an acquisition close to the peak |
| Incomplete OSM roads | Isolation count biased | Completeness check against official maps; report coverage; sensitivity of the count to missing links |
| GEE quotas / computation timeouts | Slow or failed runs | Tile the AOI, export to assets, cache results |
| Snowmelt-specific conditions (wet snow, ice) causing false positives | Reduced precision | Date selection after snow disappearance; terrain/land-cover masks; documented as a limitation |

---

## 12. Timeline (high level)

| Phase | Deliverables |
|-------|-------------|
| Pre-defence 1 | Proposal, evidence of relevance, literature review, existing-system and technology comparisons, requirements, architecture, UX prototype, verification plan, project management |
| Implementation | GEE pipeline and three methods → metrics module → road graph and isolation → API → web interface |
| Evaluation | Accuracy and sensitivity experiments, isolation comparison, hypothesis testing, usability test |
| Final defence | Thesis text, deployed demo, tagged release |

Detailed planning and risk tracking are maintained in YouTrack and in [`10_project_management_risks.md`](10_project_management_risks.md).

---

## References

- ACAPS. (2024, April 23). *Kazakhstan: Floods* (Briefing note). https://www.acaps.org/fileadmin/Data_Product/Main_media/20240423_ACAPS_briefing_note_Kazakhstan_floods.pdf
- Amer, R. (2025). Machine learning-driven rapid flood mapping for Tropical Storm Imelda using Sentinel-1 SAR imagery. *Remote Sensing, 17*(11), 1869. https://doi.org/10.3390/rs17111869
- Amoah, G. O. (2026). Cloud-independent flood mapping and surface water dynamics using Sentinel-1 SAR in the Lower Volta Basin, Ghana. *Geomatica, 78*, 100131. https://doi.org/10.1016/j.geomat.2026.100131
- Falaras, T., et al. (2025). Mapping of flood impacts caused by the September 2023 Storm Daniel in Thessaly's Plain (Greece) with the use of remote sensing satellite data. *Remote Sensing, 17*(10), 1750. https://doi.org/10.3390/rs17101750
- Gerčer, M., et al. (2026). Near real-time flood mapping from Sentinel data using machine learning techniques. *ISPRS Archives, XLIX-B3-2026*, 797–803. https://doi.org/10.5194/isprs-archives-XLIX-B3-2026-797-2026
- Johary, R., et al. (2023). Detection of large-scale floods using Google Earth Engine and Google Colab. *Remote Sensing, 15*(22), 5368. https://doi.org/10.3390/rs15225368
- Khanh, D. X., & Le, X.-H. (2026). An uncertainty-aware framework for flood extent and depth mapping from Sentinel-1 SAR via multi-event calibration under limited reference conditions. *Environmental Research Communications, 8*, 075024. https://doi.org/10.1088/2515-7620/ae88de
- Liang, J., et al. (2025). Rapid probabilistic inundation mapping using local thresholds and Sentinel-1 SAR data on Google Earth Engine. *Remote Sensing, 17*(10), 1747. https://doi.org/10.3390/rs17101747
