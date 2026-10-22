# 03. Literature Review

---

## 1. Purpose and Scope

This review establishes (a) which approaches exist for rapid flood mapping from Sentinel-1 SAR data, (b) what is already known about their accuracy and failure modes, (c) how they are validated, and (d) which limitations the SAR Flood Mapping Platform must take into account. It covers **20 sources**: a core body of **10 peer-reviewed studies from 2023–2026** selected through a systematic search, and **10 foundational works** (methods, datasets and tools) on which the platform directly builds. All 20 are used in the synthesis (Section 4) and in the design decisions (Section 6).

| Category | Count | Period |
|----------|-------|--------|
| Core empirical studies (journal articles and peer-reviewed proceedings) | 10 | 2023–2026 (all within the last five years) |
| Foundational methods, datasets and tools (peer-reviewed) | 10 | 1979–2022 |
| **Total meaningfully used sources** | **20** | — |
| of which scientific publications | 20 | — |

---

## 2. Search Strategy

### 2.1 Concepts and search strings

| Concept | Terms |
|---------|-------|
| Flood mapping | flood mapping, flood detection, inundation, surface water extraction |
| SAR data | SAR, Synthetic Aperture Radar, Sentinel-1, radar imagery |
| Algorithms | thresholding, classification, algorithm, automated, rapid mapping |
| Impact (gap-oriented) | flood impact, isolation, road network |

1. `("flood mapping" OR "flood detection" OR inundation) AND (SAR OR "Synthetic Aperture Radar" OR "Sentinel-1") AND (thresholding OR classification OR algorithm)`
2. `("rapid mapping" OR automated) AND (flood OR "surface water") AND ("Sentinel-1" OR "SAR imagery")`
3. `("flood impact" OR isolation OR "road network") AND (SAR OR radar) AND (mapping OR assessment)`

In Scopus the strings were wrapped in `TITLE-ABS-KEY( … )`.

### 2.2 Databases, filters and results

| Database | Query | Filters | Found | Selected |
|----------|-------|---------|-------|----------|
| Scopus | String 1 | 2022–2026; Open Access; Article / Conference paper; Computer Science / Earth Sciences / Engineering | 197 | 5 |
| Google Scholar | String 2 | Since 2022; full-text PDF available | ~340 | 3 |
| Google Scholar | String 3 | Since 2022; full-text PDF available | ~210 | 2 |

After removing duplicates 315 records remained; 18 were read in full and **10 were included** as the core body.

### 2.3 Inclusion and exclusion criteria

- **Included:** published 2022–2026; English; peer-reviewed article or conference paper; open access; original method for flood or surface-water mapping in which Sentinel-1 is the main data source or a documented part of a multi-sensor workflow; at least one quantitative result (accuracy, IoU, F1, κ, or area comparison with a reference product).
- **Excluded:** duplicates; reviews without a new method; non-English papers; papers without quantitative results; unrelated topics; optical-only studies — with two deliberate exceptions kept as a contrast for threshold/index-based mapping: Bazzan et al. (2026, Landsat-8 only) and Liu et al. (2026, mainly optical with Sentinel-1 support).
- **Credibility check:** title/abstract screening, then full-text screening for reproducible method description and reported metrics. All selected papers have a DOI and appear in peer-reviewed venues (Remote Sensing, Geosciences, Geomatica, Environmental Research Communications, ISPRS Archives/Annals, ACM). Limitations were extracted from the *Discussion* and *Conclusion* sections, not the abstracts.
- **Foundational works** were added by backward citation tracking from the core papers and by the technical needs of the platform (algorithm, data, terrain, network analysis), irrespective of publication year, as the evaluation guidelines allow essential foundational works.

---

## 3. Literature Matrix

### 3.1 Core studies (2023–2026)

| # | Author / Year | Research Problem | Method | Dataset | Approach / Technology | Metrics | Findings | Limitations |
|---|---------------|------------------|--------|---------|-----------------------|---------|----------|-------------|
| 1 | **Amer (2025)** | Rapid flood mapping for Tropical Storm Imelda (Texas, 2019) when optical data are unavailable | Supervised Random Forest classification on Sentinel-1 features, including the VH/VV ratio | Sentinel-1 SAR scenes of the storm; land-cover data for impact overlay | Machine learning (RF); SAR feature engineering; land-cover overlay | Classification accuracy measures reported by the author | RF with polarimetric ratio features produces usable rapid flood maps; flood extent overlaid with land cover | Training samples are hard to obtain during rapid response; shallow water on smooth pavement resembles dry ground in C-band; impact limited to land-cover overlay |
| 2 | **Amoah (2026)** | Cloud-independent mapping of floods and surface-water dynamics in the Lower Volta Basin, Ghana | Fixed dual-polarisation VV/VH threshold rule (AND logic); comparison with single-polarisation Otsu; grid of nine VV/VH threshold pairs | Sentinel-1 time series; Sentinel-2 for comparison; slope from DEM | GEE; threshold rules; slope mask < 8° | OA, F1, Cohen's κ; flooded area (km²) | F1 ranged **63.5–74.9 %** across ±1 dB threshold pairs; single-pol Otsu (VV 75.7 %, VH 74.3 %) outperformed the fixed dual-pol rule (70.7 %); Otsu produced larger water areas (7.676 / 7.129 km² vs 5.868 km²); OA 95.833 %, F1 95.697 %, κ 0.917 vs Sentinel-2 | Result is inter-sensor agreement, not independent validation (author's own statement); shallow water, flooded vegetation and shadow cause errors; impact limited to built-up exposure |
| 3 | **Bazzan et al. (2026)** | Accurate open-water mapping with an integrated spectral-index approach (FLOODISI) | Combination of spectral water indices with thresholding; comparison with Random Forest | Landsat-8 OLI (30 m) | GEE; index-based thresholding; RF benchmark; McNemar test | OA; McNemar significance test | Integrated index map reaches **93.5 % OA**, RF 95.0 %; McNemar test shows RF is significantly better (p < 0.001) despite the authors presenting the two as comparable | Optical: requires clear sky; misses narrow channels at 30 m; shadows and mixed pixels; RF training samples drawn from the product under test (circular validation) |
| 4 | **Falaras et al. (2025)** | Mapping flood extent and impacts of Storm Daniel (September 2023) on the Thessaly Plain, Greece | Otsu thresholding on Sentinel-1 corrected by a multiple of the histogram standard deviation; multi-sensor time series | Sentinel-1; optical acquisitions (several discarded due to clouds); Copernicus EMS products; OSM roads and railways | GEE; Otsu; slope mask < 10°; GIS overlay with infrastructure | Difference in maximum extent vs CEMS; affected infrastructure length | Plain Otsu **overestimated** flooding on a large rural plain; corrected extent differed from CEMS by **5.72 %**; **449.16 km** of road and railway affected | No field data; correction factor chosen after testing on the same event; road impact counted as length only — network connectivity not analysed |
| 5 | **Gerčer et al. (2026)** | Near-real-time flood mapping from Sentinel data with machine learning | Semantic segmentation: U-Net vs DeepLabV3+ | Sentinel-1 tiles labelled from Copernicus EMS delineations; 1,466 usable tiles after removing tiles with < 2 % water; Sentinel-2 dropped due to clouds | Deep learning; HAND mask at 5 m | IoU | Average IoU ≈ **0.70**, single scenes from **0.15 to 0.80**; U-Net outperformed DeepLabV3+ | Small dataset (explanation for DeepLabV3+ result not tested); high scene-to-scene variance; requires labelled training data |
| 6 | **Johary et al. (2023)** | Detecting large-scale floods over an entire country (Madagascar) quickly with free tools | Change detection by a normalised difference ratio of pre/post backscatter with a threshold of **−0.35**, calibrated on one small site; VV and VH both retained | 30 Sentinel-1 scenes covering Madagascar; CEMS products for comparison | GEE + Google Colab; HAND mask at 5 m | OA; area comparison with CEMS | 30 scenes processed in **under one hour**; OA **85 %** on the calibration site; VV and VH detect different parts of the flood; speed is more important than the last percent of accuracy in emergencies | Threshold calibrated on a single small site; against CEMS 582 ha vs 3,776 ha because images were acquired days apart; validation limited |
| 7 | **Khanh & Le (2026)** | Uncertainty-aware flood extent and depth mapping when reference data are limited | Backscatter attenuation relative to a pre-flood baseline; thresholds calibrated jointly over several events; OR logic across VV/VH | Multiple Sentinel-1 flood events; proxy reference masks produced by Random Forest | Multi-event calibration; uncertainty quantification; depth estimation | IoU, F1 | IoU > **0.84**, F1 > **0.91**; threshold selection identified as the **dominant source of uncertainty** | Reference is a proxy RF mask — authors state it measures agreement, not accuracy; OR logic increases false positives |
| 8 | **Liang et al. (2025)** | Rapid probabilistic inundation mapping with local thresholds | Gamma-distribution fitting of backscatter per land-cover class to derive local thresholds and inundation probabilities | Sentinel-1; hand-labelled **Sen1Floods11** reference; land-cover map | GEE; local/adaptive thresholds; probabilistic output; calibration analysis | Accuracy per land-cover class; probability calibration | VV closer to ideal calibration than VH; VH underestimates probabilities on test events; weak results in bare and wetland classes; only ≈ **40 %** accuracy for VV in urban areas | Snowmelt-driven floods missing from the validation set; urban, bare and wetland classes problematic |
| 9 | **Liu et al. (2026)** | Rapid inversion of flood inundation extent by fusing multi-source remote sensing with deep learning | Deep-learning segmentation on fused optical and SAR data | Mainly optical imagery with Sentinel-1 support; urban test sites | Data fusion; deep learning | Reported accuracy > 90 % (97.8 % in one city) | Fusion of sources reported to give high accuracy | No metric tables or confusion matrices — accuracy claims cannot be verified; mostly optical |
| 10 | **Osako (2026)** | Multi-temporal flood mapping in the Lower Tubarão River sub-basin, Santa Catarina, Brazil | Object-based classification with backscatter (dB) rules on multi-temporal Sentinel-1 | Sentinel-1 time series; 1 m DTM; Sentinel-2 image acquired eight days after the SAR scene | Object-based image analysis; elevation mask < 10 m | OA on 50 validation points | OA **88 %** | Only 50 points; eight-day gap to reference; errors from building orientation and forest canopy; impact limited to land-cover overlay |

### 3.2 Foundational methods, datasets and tools

| # | Author / Year | Research Problem | Method | Dataset | Approach / Technology | Metrics | Findings | Limitations / Relevance to this project |
|---|---------------|------------------|--------|---------|-----------------------|---------|----------|-------------|
| 11 | **Otsu (1979)** | Automatic threshold selection for grey-level images | Maximisation of between-class variance of the histogram | Generic images | Non-parametric global thresholding | Class separability (between-class variance) | Optimal threshold for bimodal histograms without training data | Assumes a bimodal histogram; fails when water is a small fraction of the scene — motivates the local (tile-based) variant |
| 12 | **Lee (1980)** | Speckle and noise reduction in radar/optical imagery | Local-statistics adaptive filter | Radar imagery | Spatial filtering | Noise reduction vs edge preservation | Reduces speckle while preserving edges | Basis of the speckle filter in the pre-processing stage; filter window affects narrow channels |
| 13 | **Torres et al. (2012)** | Design of the GMES Sentinel-1 C-band SAR mission | Mission and system description | Sentinel-1 specification | C-band SAR; IW mode; VV+VH dual polarisation | System parameters | Defines the operational, free, all-weather SAR data stream | Revisit depends on constellation size; after the loss of Sentinel-1B (2021) only Sentinel-1A was available in 2024 |
| 14 | **Nobre et al. (2011)** | Hydrologically meaningful terrain normalisation | Height Above the Nearest Drainage (HAND) from a DEM and drainage network | DEM-derived drainage | Terrain model | Correlation with water-table / soil classes | HAND separates floodable lowlands from uplands | Used by Johary et al. (2023) and Gerčer et al. (2026) at 5 m; its usefulness on very flat steppe is untested |
| 15 | **Twele et al. (2016)** | Fully automated Sentinel-1 flood processing chain | Automatic tile-based thresholding, fuzzy-logic refinement, HAND-based post-processing | Sentinel-1 flood events | Operational automated chain (DLR) | Accuracy vs reference maps | Demonstrates that fully automatic SAR flood mapping is operationally feasible | Calibrated for operational rather than comparative use; tile selection depends on water presence — informs our local-threshold design |
| 16 | **Pekel et al. (2016)** | Global, long-term mapping of surface water | Expert-system classification of the Landsat archive (1984–2015) | Landsat archive | GEE; JRC Global Surface Water | Omission/commission errors | Global 30 m occurrence and seasonality maps of permanent and seasonal water | Used to separate permanent water from flood water |
| 17 | **Chini et al. (2017)** | Automatic flood mapping from SAR with unknown water fraction | Hierarchical split-based approach with change detection and region growing | SAR flood events | Automatic tiling of bimodal regions | Accuracy vs reference | Robust thresholds when water occupies a small part of the image | One of the three algorithms of the CEMS Global Flood Monitoring ensemble; theoretical basis for our local method |
| 18 | **Gorelick et al. (2017)** | Planetary-scale geospatial analysis | Cloud computing platform with a public data catalogue | Sentinel-1, Landsat, DEMs, JRC GSW and others | Google Earth Engine | Scalability | Petabyte-scale data and processing available to researchers at no cost | Quotas and non-commercial terms; computation is server-side and opaque — affects architecture |
| 19 | **Boeing (2017)** | Acquisition, modelling and analysis of street networks | Download of OSM data and conversion to topologically correct graphs | OpenStreetMap | OSMnx (Python) + NetworkX | Network statistics | Reproducible street-network graphs for any place | Quality depends on OSM completeness; used for the isolation analysis |
| 20 | **Bonafilia et al. (2020)** | Lack of labelled data to train and test SAR flood algorithms | Creation of a georeferenced, hand-labelled dataset | **Sen1Floods11**: Sentinel-1 chips with hand-labelled water from 11 flood events | Benchmark dataset | IoU and related metrics | Standard benchmark used e.g. by Liang et al. (2025) | No Central Asian spring/snowmelt events — used only for pipeline cross-checks |

---

## 4. Critical Synthesis

### 4.1 Two families of methods

The ten core studies follow two approaches. **Threshold and change-detection methods on backscatter** dominate: a fixed VV/VH rule (Amoah, 2026), a normalised difference ratio with a −0.35 threshold (Johary et al., 2023), Otsu with a manual correction (Falaras et al., 2025), object-based dB rules (Osako, 2026), attenuation against a pre-flood baseline (Khanh & Le, 2026) and gamma-fitted thresholds per land-cover class (Liang et al., 2025). **Supervised learning** forms the second family: Random Forest on the VH/VV ratio (Amer, 2025) and U-Net / DeepLabV3+ (Gerčer et al., 2026; Liu et al., 2026).

Thresholding is preferred for rapid mapping because it is fast and needs no training data. At least five studies implement it in Google Earth Engine (Gorelick et al., 2017), and Johary et al. (2023) processed 30 scenes in under an hour. Machine learning buys accuracy with data: Amer (2025) concedes that training samples are hard to obtain during a rapid response, and Gerčer et al. (2026) were left with only 1,466 usable tiles. The operational CEMS Global Flood Monitoring ensemble likewise relies on non-ML algorithms, one of which is the split-based approach of Chini et al. (2017), and the automated chain of Twele et al. (2016) showed earlier that such processing can run without human intervention. **Implication for the platform:** the project implements three threshold families and treats ML as out of scope.

### 4.2 The threshold is the weak point

The studies differ most in how the threshold is selected. Amoah (2026) obtained F1 between 63.5 % and 74.9 % across nine VV/VH threshold pairs that differ by ±1 dB, and Otsu (Otsu, 1979) yielded larger water areas than his fixed rule. Falaras et al. (2025) also found that Otsu overestimated flooding on a large rural plain. The two studies **agree on the direction** of the bias but **disagree on the remedy**: Amoah keeps a conservative fixed rule, whereas Falaras shifts the Otsu value by a multiple of the histogram standard deviation chosen after testing on the same event. Khanh and Le (2026) instead calibrate on several events to obtain a stable setting, and Johary et al. (2023) calibrated −0.35 on one small site. Otsu's assumption of a bimodal histogram explains part of the problem: when water occupies a small share of the scene, the histogram is not bimodal and the global threshold drifts, which is precisely why tile-based and split-based approaches were developed (Chini et al., 2017; Twele et al., 2016; Liang et al., 2025).

The decisive observation is methodological: **every team tunes its threshold on its own event, and no paper runs different threshold methods on the same event against the same reference.** Reported accuracies are therefore not comparable across papers.

### 4.3 Polarisation logic is unresolved

Liang et al. (2025) found VV closer to ideal probability calibration and VH underestimating probabilities, while Johary et al. (2023) observed that VV and VH detect different parts of a flood and kept both. Khanh and Le (2026) flag a pixel when *either* channel drops (OR), whereas Amoah (2026) requires *both* to be low (AND). OR logic should reduce omissions and AND logic should reduce false positives, but **no study tests both rules on the same data** — the basis of hypothesis H3.

### 4.4 Terrain masking and flat terrain

Terrain masks are used to suppress false detections on slopes and in radar shadow: HAND at 5 m (Nobre et al., 2011; Gerčer et al., 2026; Johary et al., 2023), slope < 8° (Amoah, 2026) or < 10° (Falaras et al., 2025), and elevation < 10 m from a 1 m DTM (Osako, 2026). None of them quantifies how much a mask contributes on very flat ground. On the Kazakh steppe a slope mask is expected to remove little, so the main sources of false positives will instead be radar-dark dry surfaces and permanent water (handled with JRC Global Surface Water, Pekel et al., 2016) — an expectation, not yet a result.

### 4.5 Consistent failure zones

Urban areas, bare ground, wetlands and vegetation cause errors in almost every study. Liang et al. (2025) report weak scores for bare and wetland classes and only ≈ 40 % accuracy for VV in urban areas; Amer (2025) notes that shallow water on smooth pavement looks like dry ground in C-band; Osako (2026) points to building orientation and forest canopy; Amoah (2026) to shallow water, flooded vegetation and shadow. Speckle filtering (Lee, 1980) reduces noise but also blurs narrow channels. Optical data are not a remedy: Bazzan et al. (2026) reach 93.5 % OA but still miss narrow channels at 30 m, struggle with shadows and mixed pixels, and need a clear sky — the very condition that floods remove. **Implication:** the platform must report *where* each method fails, not only global scores, and must flag settlements located in low-confidence classes (urban cores).

### 4.6 Validation is the weakest link

Most reported accuracies are agreements with proxies rather than independent validation. Khanh and Le (2026) achieve IoU > 0.84 and F1 > 0.91 against a mask produced earlier by Random Forest and state that this measures agreement, not accuracy. Amoah (2026) reports κ 0.917 against Sentinel-2 and calls it inter-sensor agreement. In Bazzan et al. (2026) the RF training samples came from the product being tested. Falaras et al. (2025) compare with CEMS (5.72 % difference in maximum extent) without field data. Johary et al. (2023) report OA 85 % on their calibration site, but CEMS showed 582 ha versus 3,776 ha because the images were acquired days apart. Osako (2026) uses 50 points and a Sentinel-2 scene acquired eight days later (OA 88 %). Only Liang et al. (2025), with hand-labelled Sen1Floods11 data (Bonafilia et al., 2020), and Gerčer et al. (2026), with EMS delineations, use labelled references — and Gerčer still obtains an average IoU of only ≈ 0.70 with single scenes from 0.15 to 0.80.

Some claims cannot be verified. Liu et al. (2026) report accuracy above 90 % (97.8 % in one city) without metric tables. Bazzan et al. (2026) present their map as comparable to RF although the McNemar test shows RF is significantly better (p < 0.001). Gerčer et al. (2026) attribute the weaker DeepLabV3+ result to the small dataset without testing that explanation.

**Implication:** (1) the platform must compute all methods against *one* reference with the *same* metric definitions; (2) the reference must be temporally close to the SAR scene; (3) realistic accuracy targets for flat-terrain thresholding lie around IoU 0.70, not 0.90.

### 4.7 Impact assessment stops at the overlay

On the impact side, Falaras et al. (2025) count the length of affected roads and railways (449.16 km), Amoah (2026) counts exposed built-up area, and Amer (2025) and Osako (2026) overlay land cover. **None evaluates connectivity of the road network.** Tools for this exist — OSMnx turns OpenStreetMap into routable graphs (Boeing, 2017) — but they have not been connected to SAR flood masks in the reviewed literature. Yet during the 2024 Kazakhstan floods, access to 44 settlements was restricted by damaged roads and bridges (ACAPS, 2024), which shows that isolation, not area, is the operational quantity.

### 4.8 Data-availability context

Sentinel-1 provides free C-band dual-polarisation data (Torres et al., 2012), but after the failure of Sentinel-1B in December 2021 only Sentinel-1A was operating in 2024, so a given orbit was revisited every 12 days. The pipeline must therefore combine ascending and descending passes and tolerate the gap between the flood peak and the nearest acquisition.

---

## 5. Research Gap

**What is known.** Sentinel-1 thresholding yields usable flood extents quickly in GEE (Johary et al., 2023; Liang et al., 2025; Amoah, 2026); terrain masks and pre-flood baselines reduce false positives (Khanh & Le, 2026; Gerčer et al., 2026).

**What is not known.**
1. Which thresholding method to use: F1 changes by about 11 points with a ±1 dB shift (Amoah, 2026), Otsu needed correction (Falaras et al., 2025), and every study calibrates on its own event. No paper compares Otsu, local/adaptive and baseline-calibrated thresholds on the same flood with the same reference.
2. Whether AND or OR polarisation logic is preferable — never compared on the same data.
3. How these methods behave on flat, open terrain during a snowmelt-driven spring flood — missing from validation sets (Liang et al., 2025).
4. How the mapping method affects the number of settlements cut off from the road network — no reviewed study measures connectivity.

> **Gap statement.** Although Sentinel-1 thresholding is widely used for rapid flood mapping, it remains insufficiently investigated how different thresholding algorithms compare in accuracy and false positives on flat, open terrain during a spring flood, and how the differences between them change the number of settlements assessed as isolated from the road network.

---

## 6. Limitations the Project Takes into Account

| Limitation found in the literature | Evidence | How the platform addresses it |
|-----------------------------------|----------|-------------------------------|
| Thresholds tuned on a single event make results incomparable | Amoah 2026; Falaras 2025; Johary 2023; Khanh & Le 2026 | Three methods run with identical scenes, pre-processing, masks and reference |
| High sensitivity to small threshold shifts | Amoah 2026 | Built-in ±1 dB sensitivity analysis for every method |
| Unresolved VV/VH logic | Liang 2025; Johary 2023; Khanh & Le 2026; Amoah 2026 | Configurable VV, VH, AND and OR modes, evaluated side by side |
| Otsu bias when water fraction is small | Otsu 1979; Falaras 2025; Chini 2017 | Local (tile-based) variant with bimodality check |
| False positives on slopes, shadow, permanent water | Nobre 2011; Pekel 2016; Gerčer 2026 | Slope + HAND mask; JRC permanent-water exclusion |
| Urban / bare / wetland failure zones | Liang 2025; Amer 2025; Osako 2026 | Per-land-cover error reporting; low-confidence flag for affected settlements |
| Proxy or temporally distant validation | Khanh & Le 2026; Amoah 2026; Johary 2023; Osako 2026 | One independent reference within ≤ 2 days; stratified sampling; cross-check on Sen1Floods11 / CEMS-labelled events |
| Unverifiable accuracy claims | Liu 2026; Bazzan 2026 | Full confusion matrices and run parameters stored and exported |
| ML requires training data unavailable in emergencies | Amer 2025; Gerčer 2026 | ML out of scope; threshold methods only |
| No road-connectivity analysis | All ten core studies | OSMnx road graph + reachability-based isolation analysis per mask |
| Single-satellite revisit in 2024 | Torres 2012 (mission design) | Ascending + descending passes; acquisition gap reported |

---

## References

**Core studies**

1. Amer, R. (2025). Machine learning-driven rapid flood mapping for Tropical Storm Imelda using Sentinel-1 SAR imagery. *Remote Sensing, 17*(11), 1869. https://doi.org/10.3390/rs17111869
2. Amoah, G. O. (2026). Cloud-independent flood mapping and surface water dynamics using Sentinel-1 SAR in the Lower Volta Basin, Ghana. *Geomatica, 78*, 100131. https://doi.org/10.1016/j.geomat.2026.100131
3. Bazzan, T., Rennó, C. D., Reckziegel, E. W., Guasselli, L. A., & Korb, C. C. (2026). Flood detection integrating spectral indices (FLOODISI): A novel approach to open-water mapping. *Geosciences, 16*(8), 325. https://doi.org/10.3390/geosciences16080325
4. Falaras, T., Dosiou, A., Tounta, S., Diakakis, M., Lekkas, E., & Parcharidis, I. (2025). Mapping of flood impacts caused by the September 2023 Storm Daniel in Thessaly's Plain (Greece) with the use of remote sensing satellite data. *Remote Sensing, 17*(10), 1750. https://doi.org/10.3390/rs17101750
5. Gerčer, M., Grabrijan, T., Tekavec, J., Lisec, A., & Oštir, K. (2026). Near real-time flood mapping from Sentinel data using machine learning techniques. *ISPRS Archives, XLIX-B3-2026*, 797–803. https://doi.org/10.5194/isprs-archives-XLIX-B3-2026-797-2026
6. Johary, R., Révillion, C., Catry, T., Alexandre, C., Mouquet, P., Rakotoniaina, S., Pennober, G., & Rakotondraompiana, S. (2023). Detection of large-scale floods using Google Earth Engine and Google Colab. *Remote Sensing, 15*(22), 5368. https://doi.org/10.3390/rs15225368
7. Khanh, D. X., & Le, X.-H. (2026). An uncertainty-aware framework for flood extent and depth mapping from Sentinel-1 SAR via multi-event calibration under limited reference conditions. *Environmental Research Communications, 8*, 075024. https://doi.org/10.1088/2515-7620/ae88de
8. Liang, J., Liu, D., Feng, L., & Huang, K. (2025). Rapid probabilistic inundation mapping using local thresholds and Sentinel-1 SAR data on Google Earth Engine. *Remote Sensing, 17*(10), 1747. https://doi.org/10.3390/rs17101747
9. Liu, J., Wu, G., Li, C., Tai, Y., Li, Z., Du, C., Han, W., Wu, J., & Deng, Q. (2026). Research on rapid inversion method of flood inundation extent based on fusion of multi-source remote sensing data and deep learning algorithms. In *CMNM 2026* (pp. 805–814). ACM. https://doi.org/10.1145/3832928.3833047
10. Osako, L. S. (2026). Flood mapping using multi-temporal Sentinel-1 SAR images: A case study from Lower Tubarão River Sub-basin, Santa Catarina State, Brazil. *ISPRS Annals, XI-3-2026*, 441–446. https://doi.org/10.5194/isprs-annals-XI-3-2026-441-2026

**Foundational works**

11. Otsu, N. (1979). A threshold selection method from gray-level histograms. *IEEE Transactions on Systems, Man, and Cybernetics, 9*(1), 62–66. https://doi.org/10.1109/TSMC.1979.4310076
12. Lee, J.-S. (1980). Digital image enhancement and noise filtering by use of local statistics. *IEEE Transactions on Pattern Analysis and Machine Intelligence, PAMI-2*(2), 165–168. https://doi.org/10.1109/TPAMI.1980.4766994
13. Torres, R., et al. (2012). GMES Sentinel-1 mission. *Remote Sensing of Environment, 120*, 9–24. https://doi.org/10.1016/j.rse.2011.05.028
14. Nobre, A. D., et al. (2011). Height Above the Nearest Drainage – a hydrologically relevant new terrain model. *Journal of Hydrology, 404*(1–2), 13–29. https://doi.org/10.1016/j.jhydrol.2011.03.051
15. Twele, A., Cao, W., Plank, S., & Martinis, S. (2016). Sentinel-1-based flood mapping: A fully automated processing chain. *International Journal of Remote Sensing, 37*(13), 2990–3004. https://doi.org/10.1080/01431161.2016.1192304
16. Pekel, J.-F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature, 540*, 418–422. https://doi.org/10.1038/nature20584
17. Chini, M., Hostache, R., Giustarini, L., & Matgen, P. (2017). A hierarchical split-based approach for parametric thresholding of SAR images: Flood inundation as a test case. *IEEE Transactions on Geoscience and Remote Sensing, 55*(12), 6975–6988. https://doi.org/10.1109/TGRS.2017.2737664
18. Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment, 202*, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
19. Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems, 65*, 126–139. https://doi.org/10.1016/j.compenvurbsys.2017.05.004
20. Bonafilia, D., Tellman, B., Anderson, T., & Issenberg, E. (2020). Sen1Floods11: A georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. In *Proceedings of the IEEE/CVF CVPR Workshops* (pp. 210–211).

**Contextual source (grey literature)**

- ACAPS. (2024, April 23). *Kazakhstan: Floods* (Briefing note). https://www.acaps.org/fileadmin/Data_Product/Main_media/20240423_ACAPS_briefing_note_Kazakhstan_floods.pdf
