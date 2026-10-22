# 04. Existing Systems Comparison

> **Branch:** `DIP-3-existing-systems` · **File:** `docs/04_existing_systems_comparison.md`
> **Research basis:** Assignment 1 (Sections 2, 6, 7), Assignment 2 (Section 2); system documentation listed in the references.

---

## 1. Purpose

This document compares the SAR Flood Mapping Platform with existing operational systems and platforms that a flood analyst in Kazakhstan could use today. The goal is to show, with evidence, **which needs are already met, which are not, and therefore why the proposed solution is needed**. Every capability claim is linked to a source in Section 6; where a capability could not be confirmed from public documentation this is stated explicitly.

---

## 2. Selection of Systems

Five systems were selected because they represent the main ways in which satellite flood information is produced and delivered:

| ID | System | Type | Why it is relevant |
|----|--------|------|--------------------|
| **S1** | **Copernicus EMS – Rapid Mapping** | On-demand, analyst-produced emergency mapping service | The reference European service for post-event flood delineation maps; its products are also used as validation data in the literature (Falaras et al., 2025; Gerčer et al., 2026) |
| **S2** | **Copernicus EMS – Global Flood Monitoring (GFM)** | Fully automatic, global Sentinel-1 flood product (part of GloFAS) | The closest existing system to the proposed one: systematic SAR flood mapping with several algorithms |
| **S3** | **GloFAS – Global Flood Awareness System (forecasting)** | Hydrological forecasting system | The standard global early-warning system; represents the modelling (not observation) approach |
| **S4** | **Google Earth Engine (with community/UN-SPIDER flood scripts)** | Cloud geoprocessing platform | The environment in which most reviewed studies implement thresholding (Johary et al., 2023; Liang et al., 2025; Amoah, 2026) |
| **S5** | **Sentinel Hub / Copernicus Data Space Ecosystem (EO Browser)** | Cloud imagery access and on-the-fly processing service | The most common interactive way to view and script Sentinel-1 imagery without local processing |

Desktop software (ESA SNAP, QGIS) is not treated as a "system" here because it provides generic tools rather than a flood-mapping service; it is considered as a technology alternative in [`05_technology_comparison.md`](05_technology_comparison.md).

---

## 3. Comparison Criteria

Ten criteria were derived from the needs of the target users (emergency services, GIS analysts, regional authorities) and from the research gap identified in [`03_literature_review.md`](03_literature_review.md).

| ID | Criterion | What is assessed | Link to project need |
|----|-----------|------------------|---------------------|
| **C1** | Cloud independence | Is the observed flood extent derived from SAR, i.e. usable under cloud cover? | Clouds block optical data at the flood peak |
| **C2** | Timeliness / processing speed | Time from satellite acquisition (or request) to usable product | Rapid response |
| **C3** | Availability for Kazakhstan on demand | Can a Kazakh user obtain a product for any chosen area and date without external activation? | Local operational use |
| **C4** | Openness and cost | Are data, code and products free and open? Is the algorithm open source? | Reproducibility, budget |
| **C5** | Algorithm transparency and configurability | Can the user see and change the threshold method, polarisation and masks? | Threshold choice is the dominant uncertainty (Khanh & Le, 2026) |
| **C6** | Method comparison and sensitivity analysis | Does the system run several methods on the same data and quantify sensitivity (±1 dB, AND/OR)? | Core research gap |
| **C7** | Accuracy reporting | Does the system report accuracy metrics (IoU, F1, κ) for the user's specific run against a reference? | Users must know how reliable a map is |
| **C8** | Road-network isolation analysis | Does the system determine which settlements are cut off from the road network? | Core research gap; most decision-relevant output |
| **C9** | Automation | Can the full workflow run without manual GIS steps or coding by the end user? | Analysts without programming skills |
| **C10** | API and export | Programmatic access and standard GIS export formats | Integration with authorities' GIS |

**Rating scale:** ✅ fully supported · ◐ partially supported / requires significant user effort · ❌ not supported.

---

## 4. Comparison Matrix

| Criterion | S1 CEMS Rapid Mapping | S2 CEMS GFM | S3 GloFAS forecast | S4 Google Earth Engine | S5 Sentinel Hub / CDSE | **Proposed platform** |
|-----------|----------------------|-------------|--------------------|-----------------------|-----------------------|-----------------------|
| **C1** Cloud independence | ◐ Uses any suitable imagery, incl. SAR; optical where available | ✅ Sentinel-1 only | ❌ Not an observation — model forecast of river discharge | ✅ Sentinel-1 in catalogue (user must implement) | ✅ Sentinel-1 available (user must script) | ✅ Sentinel-1 GRD |
| **C2** Timeliness | ◐ Delineation ≈ 7 h after image reception, **but only after activation** | ✅ Target ≤ 8 h from acquisition; automatic | ✅ Daily forecasts with lead time (but not observed extent) | ◐ Minutes to hours, depending on user code | ◐ On-the-fly, but no flood product | ✅ Target: complete 3-method run ≤ 15 min per AOI (NFR-01) |
| **C3** On-demand for Kazakhstan | ❌ Activation restricted to authorised users (EU civil protection); others via ERCC; no guarantee of activation | ✅ Global, systematic for every Sentinel-1 scene | ✅ Global | ✅ Any AOI | ✅ Any AOI | ✅ Any AOI and dates chosen by the user |
| **C4** Openness / cost | ◐ Products free; production process manual and not open source | ◐ Products free; algorithms published, operational code not user-modifiable | ◐ Products free (registration); model complex | ◐ Free for research / non-commercial; platform proprietary | ◐ Commercial plans based on processing units; free quota via CDSE | ✅ Open source; open data; free tiers |
| **C5** Transparency / configurability | ❌ Analyst decisions not configurable by user | ❌ Fixed ensemble of three algorithms; user cannot change thresholds or logic | ❌ Not applicable | ✅ Fully configurable — but only by writing code | ◐ Custom evalscripts possible; per-pixel scripting limits histogram-based methods | ✅ Method, threshold offset, polarisation logic and masks selectable in UI/API |
| **C6** Method comparison & sensitivity | ❌ | ❌ Ensemble = majority vote; individual methods not compared per run for the user | ❌ | ◐ Possible only if the user writes it | ❌ | ✅ 3 methods × {−1, 0, +1 dB} × {VV, VH, AND, OR} |
| **C7** Accuracy reporting per run | ◐ Quality notes; no per-run IoU/F1 | ◐ Thematic accuracy target (CSI ≥ 70 %) at product level; advisory flags; no per-run metrics vs user reference | ◐ Forecast skill scores, not extent accuracy | ◐ User must implement | ❌ | ✅ IoU, F1, κ, precision, recall, confusion matrix |
| **C8** Road isolation analysis | ❌ Maps affected roads visually; no connectivity/reachability analysis documented | ❌ Affected population and land cover layers; no road connectivity | ❌ | ◐ Not available; would require exporting results to external network tools | ❌ | ✅ OSM graph reachability → list of isolated settlements |
| **C9** Automation for non-programmers | ◐ Automated for the requester, but manual production | ✅ Fully automatic | ✅ | ❌ Requires JavaScript/Python coding | ◐ Visualisation without code; analysis needs scripting | ✅ Web UI; runs end-to-end without coding |
| **C10** API / export | ◐ Downloadable map packages (vector/PDF) | ◐ Web services / portal download | ✅ Data via Copernicus EWDS | ✅ Python/JS API; exports | ✅ REST APIs (Process, Catalog) | ✅ REST API (OpenAPI); GeoTIFF, GeoJSON, GeoPackage, CSV |

### 4.1 Summary score

Counting ✅ = 2, ◐ = 1, ❌ = 0 (maximum 20):

| System | Score | Strongest at | Weakest at |
|--------|-------|--------------|------------|
| S1 CEMS Rapid Mapping | 6 | Expert-quality maps | Availability, configurability, isolation |
| S2 CEMS GFM | 11 | Systematic, automatic SAR mapping | Configurability, method comparison, isolation |
| S3 GloFAS forecast | 10 | Early warning | Not an observed flood extent |
| S4 Google Earth Engine | 13 | Flexibility, compute | Requires coding; no ready workflow; no isolation |
| S5 Sentinel Hub / CDSE | 10 | Data access, visualisation | No flood product; cost beyond quota |
| **Proposed platform** | **20** (target) | Comparison + isolation | Not operational at national scale (scope) |

The score is a design-target comparison, not a measured benchmark: the proposed platform's ratings are **requirements to be verified** (see [`06_requirements.md`](06_requirements.md) and [`09_verification_plan.md`](09_verification_plan.md)), whereas the ratings of S1–S5 are taken from their documentation.

---

## 5. Analysis of Individual Systems

### S1 — Copernicus EMS Rapid Mapping

**Strengths.** High-quality delineation and grading maps produced by expert analysts; free products; delineation available about seven hours after image reception (Copernicus EMS, 2021). Its maps are widely used as reference data (Falaras et al., 2025; Gerčer et al., 2026).

**Limitations.** The service is **activation-based**: only authorised users (civil-protection focal points of EU Member States and a few other countries and EU services) can trigger it directly, and other countries must go through the EU Emergency Response Coordination Centre (Copernicus EMS, 2021). An activation for a given flood and area is therefore not guaranteed; for the 2024 Kazakhstan floods the team has **not been able to confirm** a Rapid Mapping activation covering the pilot areas (this is tracked as a risk). The production process is manual and not reproducible by the user, method parameters are not exposed, and the products show affected roads but do not compute which settlements lose connectivity. Johary et al. (2023) also demonstrated that a time offset between CEMS imagery and other imagery can produce very different extents (582 ha vs 3,776 ha).

### S2 — Copernicus EMS Global Flood Monitoring (GFM)

**Strengths.** The closest existing system. It processes every incoming Sentinel-1 GRD scene automatically and runs **three independent algorithms** — LIST's hierarchical split-based approach (Chini et al., 2017), DLR's fuzzy-logic approach and TU Wien's time-series approach — combining them by majority vote (a pixel is flooded if at least two of three algorithms agree). It targets delivery within eight hours, provides an exclusion mask for areas where SAR mapping is infeasible (urban areas, dense vegetation, water look-alikes, shadow), a reference water mask, advisory flags, and affected population and land-cover layers. Its required thematic accuracy is a Critical Success Index of at least 70 % (EODC, n.d.).

**Limitations.** (1) The ensemble is fixed: users cannot change thresholds, polarisation logic or masks, and the **individual algorithms are not compared or scored for the user's event** — the very comparison the research question asks for. (2) Accuracy is a product-level target, not a per-run metric against a local reference. (3) The impact layers stop at population and land cover; **road-network connectivity is not analysed**. (4) The exclusion mask removes urban areas — where settlements are — so settlement-level isolation cannot be derived from it alone. GFM is therefore a valuable **comparison baseline** for the proposed platform rather than a replacement.

### S3 — GloFAS (forecasting)

**Strengths.** Global, free hydrological forecasts of river discharge and flood probability with lead times of days to weeks; version 4 runs at 0.05° (≈ 5 km) resolution (Copernicus EMS, 2023).

**Limitations.** GloFAS **models** discharge; it does not observe the actual inundation extent. At ≈ 5 km resolution it cannot resolve individual roads or settlements. Snowmelt-driven floods on flat steppe with ice jams and dam failures (e.g. the collapse of a protective dam reported in Aktobe region in 2024) are difficult to forecast. It answers *"where may a flood occur?"*, not *"which settlements are cut off now?"*.

### S4 — Google Earth Engine (GEE)

**Strengths.** Petabyte catalogue (Sentinel-1, DEMs, JRC Global Surface Water) and server-side processing at no cost for research (Gorelick et al., 2017). At least five reviewed studies implement thresholding in GEE, and Johary et al. (2023) processed 30 scenes in under one hour. Community scripts such as the UN-SPIDER recommended practice provide change-detection flood mapping.

**Limitations.** GEE is a **platform, not a product**: every flood map requires writing and maintaining code, choosing thresholds by hand and validating separately. Each reviewed study did exactly this and ended up with incomparable, event-specific thresholds (Amoah, 2026; Falaras et al., 2025; Johary et al., 2023). GEE has no built-in routable road graph, so isolation analysis must be done outside it. Its terms are non-commercial and processing quotas apply. **The proposed platform uses GEE as its processing back-end** (see technology comparison) and adds what GEE lacks: a fixed, comparable experiment design, accuracy evaluation, isolation analysis and a user interface.

### S5 — Sentinel Hub / Copernicus Data Space Ecosystem

**Strengths.** Fast, on-the-fly access and visualisation of Sentinel-1 imagery through EO Browser and REST APIs; custom per-pixel scripts (evalscripts).

**Limitations.** No ready flood product or accuracy assessment. Processing is billed in processing units on commercial plans, with a limited free quota available through the Copernicus Data Space Ecosystem (Sentinel Hub, n.d.). Per-pixel evalscripts are not designed for histogram-based thresholding such as Otsu, which requires statistics over a whole area. No network analysis.

---

## 6. Evidence for Claims

| Claim | Source |
|-------|--------|
| CEMS Rapid Mapping is triggered by authorised users; non-authorised users via ERCC; delineation ≈ 7 h after image reception; products free | Copernicus EMS (2021), *CEMS overview*, UN-SPIDER conference presentation |
| GFM: three algorithms (LIST, DLR, TUW), majority-vote ensemble, ≤ 8 h target, exclusion mask, reference water mask, advisory flags, affected population/land cover, CSI ≥ 70 % target | EODC (n.d.), *GFM Product User Manual – Technical Overview* |
| GloFAS v4 at 0.05° resolution | Copernicus EMS (2023), *What is new in GloFAS v4.0* |
| GEE catalogue and free research access | Gorelick et al. (2017) |
| Thresholding commonly implemented in GEE; 30 scenes < 1 h | Johary et al. (2023); Liang et al. (2025); Amoah (2026) |
| CEMS vs other imagery: 582 ha vs 3,776 ha due to acquisition gap | Johary et al. (2023) |
| Event-specific thresholds make results incomparable | Assignment 1, Section 6; Amoah (2026); Falaras et al. (2025) |
| Sentinel Hub billing in processing units; CDSE quota | Sentinel Hub (n.d.), *Billing* documentation |
| 44 settlements with restricted access in Kazakhstan, April 2024 | ACAPS (2024) |

---

## 7. Justification of the Proposed Solution

The comparison shows that **no existing system combines** (a) cloud-independent observation, (b) user-controlled, transparent thresholding, (c) side-by-side comparison and sensitivity analysis of several methods on the same event, (d) per-run accuracy metrics against a reference, and (e) road-network isolation analysis.

- Operational services (S1, S2) deliver flood extents but **hide method choices** and **stop at the water polygon or at population/land-cover overlays**. They cannot tell an analyst how much the chosen method biases the result, nor which settlements are cut off.
- Forecasting (S3) answers a different question at a resolution too coarse for roads.
- Platforms (S4, S5) provide data and compute but **require programming** and offer no ready workflow, so every analyst re-invents and re-tunes thresholds — the root cause of incomparable results identified in the literature.

The 2024 Kazakhstan floods illustrate the operational gap: access to **44 settlements** was restricted by damaged roads and bridges (ACAPS, 2024), yet none of the five systems produces a list of isolated settlements.

**Positioning.** The proposed platform does not compete with CEMS on operational coverage. It is a **research and decision-support tool** that (1) builds on GEE as the processing engine, (2) uses CEMS and GFM products as validation/comparison data where available, and (3) adds the two missing capabilities — controlled method comparison and isolation analysis — in a form usable without programming.

| Gap in existing systems | Proposed capability | Requirement |
|-------------------------|---------------------|-------------|
| Fixed, hidden algorithms | Selectable Otsu / local / baseline methods, VV/VH/AND/OR | FR-04 … FR-07 |
| No sensitivity analysis | ±1 dB × polarisation grid | FR-08 |
| No per-run accuracy | IoU, F1, κ, precision, recall vs reference | FR-09 |
| No connectivity analysis | OSM graph reachability, isolated-settlement list | FR-11 … FR-13 |
| Coding required (GEE, Sentinel Hub) | Web UI + REST API | FR-15, FR-17, FR-18 |
| Activation dependency (CEMS) | On-demand for any AOI/date | FR-01 |

---

## References

- ACAPS. (2024, April 23). *Kazakhstan: Floods* (Briefing note). https://www.acaps.org/fileadmin/Data_Product/Main_media/20240423_ACAPS_briefing_note_Kazakhstan_floods.pdf
- Amoah, G. O. (2026). Cloud-independent flood mapping and surface water dynamics using Sentinel-1 SAR in the Lower Volta Basin, Ghana. *Geomatica, 78*, 100131. https://doi.org/10.1016/j.geomat.2026.100131
- Chini, M., Hostache, R., Giustarini, L., & Matgen, P. (2017). A hierarchical split-based approach for parametric thresholding of SAR images: Flood inundation as a test case. *IEEE TGRS, 55*(12), 6975–6988. https://doi.org/10.1109/TGRS.2017.2737664
- Copernicus EMS. (2021). *Copernicus Emergency Management Service overview* (UN-SPIDER Conference 2021). https://un-spider.org/sites/default/files/18_Conf2021_CEMS_overview.pdf
- Copernicus EMS. (2023). *What is new in GloFAS v4.0*. https://global-flood.emergency.copernicus.eu/media/events/4/what_is_new_in_glofas_v4.0.pdf
- EODC. (n.d.). *GFM Product User Manual – Technical overview*. https://extwiki.eodc.eu/GFM/PUM/TechnicalOverview
- Falaras, T., et al. (2025). Mapping of flood impacts caused by the September 2023 Storm Daniel in Thessaly's Plain (Greece). *Remote Sensing, 17*(10), 1750. https://doi.org/10.3390/rs17101750
- Gerčer, M., et al. (2026). Near real-time flood mapping from Sentinel data using machine learning techniques. *ISPRS Archives, XLIX-B3-2026*, 797–803. https://doi.org/10.5194/isprs-archives-XLIX-B3-2026-797-2026
- Gorelick, N., et al. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment, 202*, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
- Johary, R., et al. (2023). Detection of large-scale floods using Google Earth Engine and Google Colab. *Remote Sensing, 15*(22), 5368. https://doi.org/10.3390/rs15225368
- Khanh, D. X., & Le, X.-H. (2026). An uncertainty-aware framework for flood extent and depth mapping from Sentinel-1 SAR. *Environmental Research Communications, 8*, 075024. https://doi.org/10.1088/2515-7620/ae88de
- Liang, J., et al. (2025). Rapid probabilistic inundation mapping using local thresholds and Sentinel-1 SAR data on Google Earth Engine. *Remote Sensing, 17*(10), 1747. https://doi.org/10.3390/rs17101747
- Sentinel Hub. (n.d.). *Billing* (API documentation). https://docs.sentinel-hub.com/api/latest/api/overview/billing
