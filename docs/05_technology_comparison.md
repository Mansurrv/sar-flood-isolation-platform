# 05. Technology Comparison

> **Branch:** `DIP-4-technology-comparison` · **File:** `docs/05_technology_comparison.md`
> **Basis:** project requirements ([`06_requirements.md`](06_requirements.md)), research design from Assignments 1–2, and the existing-systems analysis ([`04_existing_systems_comparison.md`](04_existing_systems_comparison.md)).

---

## 1. Purpose and Method

This document justifies the key technology decisions of the SAR Flood Mapping Platform. For each decision, two to three realistic alternatives are compared to the selected option against criteria that are **derived from the project requirements**, not from general popularity.

**Method.** For every decision:

1. The driving requirements are listed.
2. The alternatives are described with their advantages and disadvantages.
3. A weighted decision matrix is computed: each criterion has a weight (1–5, reflecting its importance for the project requirements); each option is scored 1 (poor) – 5 (excellent); the weighted total is Σ(weight × score).
4. The decision, its rationale, the accepted trade-offs and the conditions under which it would be revisited are stated.

### 1.1 Requirements that drive technology choice

| ID | Requirement (summary) | Consequence for technology |
|----|----------------------|----------------------------|
| FR-02, FR-03 | Sentinel-1 GRD retrieval, pre-processing, slope/HAND and permanent-water masks | Need catalogue access to S1, DEM, HAND, JRC water |
| FR-04 … FR-08 | Three thresholding methods; polarisation logic; ±1 dB sensitivity grid (up to 36 masks per AOI) | Need scalable raster computation incl. histogram statistics |
| FR-09 | Accuracy metrics vs reference | Pixel-level confusion matrices over large areas |
| FR-11 … FR-13 | OSM road graph; reachability; comparison of isolated sets | Graph library with shortest-path / connectivity algorithms |
| FR-15, FR-16, FR-17 | Web map, REST API, job status | Python web framework with async support; web-map library |
| NFR-01 | Complete 3-method run ≤ 15 min for an AOI ≤ 50,000 km² | Cloud-scale raster processing |
| NFR-02 | Isolation analysis ≤ 60 s per mask | In-memory graph algorithms |
| NFR-05 | Reproducibility | Deterministic, parameter-logged runs |
| NFR-06, NFR-14 | Open data and open-source software; zero licence cost | No commercial licences |
| NFR-07 | One-command deployment | Containerisable components |
| — | Team of two with Python and JavaScript skills; one semester | Prefer one primary language and low operational burden |

---

## 2. Decision TD-1 — SAR Raster Processing Engine

**Question.** Where and with which tools are Sentinel-1 scenes pre-processed and thresholded?

### 2.1 Alternatives

| Option | Description |
|--------|-------------|
| **A. Google Earth Engine (Python API)** | Server-side processing on Google's infrastructure using the analysis-ready `COPERNICUS/S1_GRD` collection (already calibrated, terrain-corrected, in dB) and catalogue DEM/HAND/JRC layers |
| **B. Local Python stack (Rasterio / GDAL / NumPy)** | Download GRD products from the Copernicus Data Space Ecosystem and process them on own hardware |
| **C. ESA SNAP (Graph Processing Tool / `esa_snappy`)** | ESA's reference toolbox for full SAR pre-processing (orbit file, thermal noise removal, calibration, speckle filter, terrain correction) run locally |

### 2.2 Advantages and disadvantages

| Option | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A. GEE** | No data download; S1 GRD already pre-processed (Johary et al., 2023); DEM, HAND (MERIT Hydro) and JRC Global Surface Water in the same catalogue; `reduceRegion` histograms make Otsu and local thresholds straightforward; proven speed (30 scenes < 1 h, Johary et al., 2023); used by ≥ 5 reviewed studies → comparability | Proprietary, non-commercial terms; quotas and computation time-outs; lazy server-side execution complicates debugging; vendor lock-in |
| **B. Rasterio / GDAL** | Full control, fully open source; deterministic local execution; easy unit testing | Must download tens of GB per event; must implement or chain all pre-processing; local hardware limits AOI size; slow for a 36-mask sensitivity grid |
| **C. SNAP** | Most rigorous SAR pre-processing (reference implementation); open source | Heavy (Java, high RAM); slow per scene; difficult to containerise and to call from a web service; still needs download; adds a second language/runtime |

### 2.3 Decision matrix

| Criterion | Weight | A. GEE | B. Rasterio/GDAL | C. SNAP |
|-----------|-------:|------:|----------------:|-------:|
| Processing speed / scalability (NFR-01) | 5 | 5 | 2 | 2 |
| Data availability (S1, DEM, HAND, JRC) without download (FR-02, FR-03) | 5 | 5 | 2 | 2 |
| Support for histogram-based thresholding (FR-04, FR-05) | 4 | 5 | 4 | 3 |
| Comparability with literature (research validity) | 3 | 5 | 3 | 3 |
| Openness / licence (NFR-06) | 3 | 3 | 5 | 5 |
| Testability / determinism (NFR-05, NFR-09) | 3 | 3 | 5 | 3 |
| Integration with a Python web service (FR-15) | 3 | 4 | 5 | 2 |
| Learning curve for the team | 2 | 4 | 3 | 2 |
| **Weighted total** (max 140) | | **123** | **96** | **75** |

### 2.4 Decision

**Selected: A — Google Earth Engine Python API**, with **Rasterio/GDAL (B) as a complementary local layer** for post-processing exported results (vectorisation, COG conversion, unit-testable metric calculation on small fixtures).

**Rationale.** Speed and data availability are decisive for NFR-01 and FR-02/03: the sensitivity grid alone produces up to 36 masks per AOI, which is impractical with downloaded GRD files. Using the same pre-processed collection as most reviewed studies keeps the results comparable with the literature.

**Trade-offs accepted and mitigations.** Vendor lock-in and opacity are mitigated by (1) isolating all GEE calls behind a `GeeClient` adapter interface (see architecture), (2) logging all GEE asset IDs and parameters per run (NFR-05), and (3) unit-testing algorithm logic on small local fixtures with NumPy implementations of the same formulas. **Revisit if** GEE terms change or quotas prevent the experiments — then option B with CDSE downloads becomes the fallback.

---

## 3. Decision TD-2 — Backend Framework

**Question.** Which server framework exposes the pipeline through a REST API?

### 3.1 Alternatives

| Option | Description |
|--------|-------------|
| **A. FastAPI (Python)** | ASGI micro-framework with Pydantic validation and automatic OpenAPI documentation |
| **B. Django + Django REST Framework / GeoDjango (Python)** | Full-stack framework with ORM, admin and GIS extensions |
| **C. Node.js (Express / NestJS)** | JavaScript/TypeScript server runtime |

### 3.2 Advantages and disadvantages

| Option | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A. FastAPI** | Same language as GEE API, OSMnx, GeoPandas → processing code imported directly; native async for long-running jobs; automatic OpenAPI/Swagger (NFR-13); Pydantic schemas double as request validation; lightweight | Fewer batteries included (no admin, no built-in auth — not needed in scope); smaller ecosystem than Django |
| **B. Django / DRF** | Mature; ORM; admin panel; GeoDjango for spatial models | Heavier; synchronous-first (async partial); ORM/admin largely unused because results live in GEE assets and files; OpenAPI requires add-ons |
| **C. Node.js** | Strong async I/O; same language as the frontend | GEE has a JS client but OSMnx/NetworkX/GeoPandas have no equivalent → processing would need a separate Python service and inter-process communication; two backend languages for a two-person team |

### 3.3 Decision matrix

| Criterion | Weight | A. FastAPI | B. Django | C. Node.js |
|-----------|-------:|----------:|---------:|----------:|
| Direct integration with Python geospatial stack | 5 | 5 | 5 | 1 |
| Support for asynchronous long-running jobs (FR-16) | 4 | 5 | 3 | 5 |
| Automatic API documentation (NFR-13) | 3 | 5 | 3 | 3 |
| Simplicity / development speed for 2 people | 4 | 5 | 3 | 3 |
| Performance of read endpoints (NFR-03) | 2 | 4 | 3 | 4 |
| Ecosystem maturity | 2 | 4 | 5 | 5 |
| **Weighted total** (max 100) | | **96** | **74** | **64** |

### 3.4 Decision

**Selected: A — FastAPI.** It keeps the whole backend in Python, so processing modules are called in-process, and it provides async request handling and OpenAPI documentation out of the box. Django's main advantages (ORM, admin, auth) target needs that are out of scope. **Revisit if** multi-user accounts and role management enter scope — then Django or FastAPI + an auth library would be re-evaluated.

---

## 4. Decision TD-3 — Geodata and Result Storage

**Question.** Where are flood masks, vectors, isolation results and run metadata stored?

### 4.1 Alternatives

| Option | Description |
|--------|-------------|
| **A. File-based: GEE assets + Cloud-Optimized GeoTIFF (COG) + GeoPackage / SQLite run registry** | Raster masks remain as GEE assets and are exported as COG files; vector results (flood polygons, roads, isolated settlements) in GeoPackage; run parameters and metrics in an SQLite registry |
| **B. PostgreSQL + PostGIS (+ optional raster)** | Spatial relational database server holding all vectors, metadata and optionally rasters |
| **C. MongoDB (GeoJSON documents)** | Document database with 2dsphere geospatial indexes |

### 4.2 Advantages and disadvantages

| Option | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A. File-based** | Zero server administration; GeoPackage is an OGC standard readable by QGIS/ArcGIS (NFR-11); COG enables HTTP range requests for web display; each run is a self-contained, versionable folder (NFR-05); trivially containerised | No concurrent multi-user writes; spatial queries across runs require loading files; SQLite write concurrency limited |
| **B. PostGIS** | Industry-standard spatial SQL; concurrent access; spatial indexes; pgRouting available | Extra service to deploy and maintain; raster storage in PostGIS is inefficient for large masks; duplication of data that already lives in GEE |
| **C. MongoDB** | Flexible schema for run metadata; native GeoJSON | Weak support for rasters and complex spatial operations (no topology, limited CRS support); not a GIS standard format → poor interoperability with authorities' GIS |

### 4.3 Decision matrix

| Criterion | Weight | A. Files (GEE/COG/GPKG) | B. PostGIS | C. MongoDB |
|-----------|-------:|-----------------------:|-----------:|-----------:|
| Raster handling (masks up to 10⁸ px) | 5 | 5 | 2 | 1 |
| Interoperability / GIS standard formats (NFR-11, FR-19) | 4 | 5 | 4 | 2 |
| Reproducibility / versioning of runs (NFR-05) | 4 | 5 | 3 | 3 |
| Operational simplicity (NFR-07) | 4 | 5 | 3 | 3 |
| Spatial query capability | 3 | 3 | 5 | 3 |
| Multi-user concurrency | 1 | 2 | 5 | 4 |
| **Weighted total** (max 105) | | **96** | **70** | **50** |

### 4.4 Decision

**Selected: A — GEE assets + COG + GeoPackage, with an SQLite run registry.** The platform is used by a small group of analysts for event-based analyses, so multi-user concurrency carries little weight, while raster handling and reproducibility carry a lot. **Revisit if** the platform moves to operational multi-user deployment — PostGIS (B) is the planned upgrade path; the repository-layer abstraction (`ResultRepository`) makes this a contained change.

---

## 5. Decision TD-4 — Road-Network Isolation Analysis

**Question.** How are roads modelled and how is isolation computed?

### 5.1 Alternatives

| Option | Description |
|--------|-------------|
| **A. OSMnx + NetworkX (+ GeoPandas)** | Download OSM roads into a Python graph; remove edges intersecting the flood mask; compute connected components / reachability to hub nodes |
| **B. pgRouting on PostGIS** | Load OSM into PostGIS (osm2pgrouting) and use SQL routing functions |
| **C. OSRM / GraphHopper routing engine** | Pre-processed routing server queried over HTTP |

### 5.2 Advantages and disadvantages

| Option | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A. OSMnx + NetworkX** | Pure Python, same stack as backend; graph built per AOI in minutes (Boeing, 2017); full control over edge removal; connected components are O(V + E); easy to unit test with synthetic graphs | In-memory: very large national graphs need more RAM; NetworkX slower than C++ engines |
| **B. pgRouting** | Scales to large networks; SQL integration | Requires PostGIS (rejected in TD-3); edge removal per mask means re-building topology per run; extra tooling |
| **C. OSRM / GraphHopper** | Very fast shortest paths | Designed for a static network: excluding flooded edges requires re-pre-processing the graph for every mask (36 per AOI) → impractical; returns routes, not connectivity sets |

### 5.3 Decision matrix

| Criterion | Weight | A. OSMnx + NetworkX | B. pgRouting | C. OSRM |
|-----------|-------:|-------------------:|------------:|-------:|
| Dynamic edge removal per flood mask (FR-12) | 5 | 5 | 3 | 1 |
| Performance for AOI-scale graphs (NFR-02) | 4 | 4 | 5 | 5 |
| Fit with the Python stack / TD-2, TD-3 | 4 | 5 | 2 | 2 |
| Testability with synthetic graphs (NFR-09) | 3 | 5 | 3 | 2 |
| Deployment simplicity (NFR-07) | 3 | 5 | 2 | 2 |
| **Weighted total** (max 95) | | **91** | **58** | **45** |

### 5.4 Decision

**Selected: A — OSMnx + NetworkX.** The core operation is not routing but **connectivity under a changing set of removed edges**, repeated for many masks; NetworkX handles this directly with connected-component and reachability algorithms. AOI-scale graphs (regional networks, ≲ 250,000 edges) fit comfortably in memory. **Revisit if** national-scale graphs exceed memory — then the graph would be partitioned by region or `igraph` used as a faster drop-in.

---

## 6. Decision TD-5 — Component Interaction (Backend ↔ Processing ↔ Frontend)

**Question.** How do the frontend, API and long-running processing communicate? A full run (3 methods, sensitivity grid, isolation) can take minutes, which exceeds normal HTTP time-outs.

### 6.1 Alternatives

| Option | Description |
|--------|-------------|
| **A. REST + asynchronous job pattern with polling** | `POST /runs` returns `202 Accepted` with a `run_id`; work executes in a background worker; client polls `GET /runs/{id}`; results fetched from result endpoints |
| **B. Synchronous REST** | Request blocks until processing finishes |
| **C. Message broker (Celery + Redis / RabbitMQ) with WebSocket push** | Distributed task queue; progress pushed to the client |

### 6.2 Advantages and disadvantages

| Option | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A. REST + async jobs + polling** | Robust to long runs; stateless HTTP; simple to implement with FastAPI background workers and the SQLite run registry; easy to test; progress visible (FR-16) | Polling adds some latency/overhead; a single worker process limits parallelism |
| **B. Synchronous REST** | Simplest | Requests of several minutes hit browser/proxy time-outs; no progress reporting; failed runs leave no record → violates FR-16, NFR-12 |
| **C. Celery + Redis + WebSocket** | Horizontal scaling; retries; real-time push | Two extra services; more complex deployment and testing; over-engineered for a small number of concurrent analysts |

### 6.3 Decision matrix

| Criterion | Weight | A. Async jobs + polling | B. Sync REST | C. Broker + WebSocket |
|-----------|-------:|-----------------------:|------------:|---------------------:|
| Handles minute-long runs (NFR-01, FR-16) | 5 | 5 | 1 | 5 |
| Reliability / failure recording (NFR-12) | 4 | 4 | 1 | 5 |
| Implementation and deployment simplicity (NFR-07) | 4 | 4 | 5 | 2 |
| Testability (NFR-09) | 3 | 5 | 5 | 3 |
| Scalability to many users | 1 | 2 | 1 | 5 |
| **Weighted total** (max 85) | | **74** | **45** | **67** |

### 6.4 Decision

**Selected: A — REST API with an asynchronous job pattern and client polling** (JSON over HTTP; GeoJSON for vectors; COG/XYZ tiles for rasters). The `JobManager` is designed behind an interface so that it can be backed by Celery + Redis (option C) without changing the REST contract if concurrency requirements grow.

---

## 7. Decision TD-6 — Frontend Web-Map Library

**Question.** Which library renders flood masks, roads and settlements in the browser?

### 7.1 Alternatives and matrix

| Option | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A. React + Leaflet (react-leaflet)** | Lightweight; very simple API; plugins for side-by-side comparison and GeoJSON styling; XYZ tiles from GEE (`getMapId`) work directly | Raster/vector performance lower than WebGL for very large vector sets |
| **B. React + OpenLayers** | Full GIS capabilities, projections, WMS/WFS | Steeper learning curve; heavier |
| **C. React + MapLibre GL JS** | WebGL rendering; smooth with large vector data | Optimised for vector tiles; raster overlays and GeoJSON styling more complex; requires a style specification |

| Criterion | Weight | A. Leaflet | B. OpenLayers | C. MapLibre |
|-----------|-------:|----------:|-------------:|-----------:|
| Ease of use / development speed | 4 | 5 | 3 | 3 |
| Display of GEE XYZ tiles and GeoJSON (FR-17) | 4 | 5 | 5 | 4 |
| Mask comparison (swipe / layer toggle, FR-21) | 3 | 5 | 4 | 3 |
| Performance with AOI-scale data (NFR-03) | 3 | 4 | 4 | 5 |
| Bundle size / simplicity | 2 | 5 | 3 | 3 |
| **Weighted total** (max 80) | | **77** | **62** | **58** |

**Selected: A — React + Leaflet.** Isolated-settlement layers contain hundreds, not millions, of features, and rasters are served as tiles, so WebGL is not required.

---

## 8. Summary of Decisions

| ID | Decision | Selected | Alternatives considered | Key driving requirements |
|----|----------|----------|------------------------|--------------------------|
| TD-1 | SAR processing engine | **Google Earth Engine Python API** (+ Rasterio/GDAL locally) | Local Rasterio/GDAL only; ESA SNAP | NFR-01, FR-02 … FR-08 |
| TD-2 | Backend framework | **FastAPI** | Django/DRF; Node.js | FR-15, FR-16, NFR-13 |
| TD-3 | Storage | **GEE assets + COG + GeoPackage + SQLite registry** | PostGIS; MongoDB | NFR-05, NFR-07, NFR-11 |
| TD-4 | Isolation analysis | **OSMnx + NetworkX** | pgRouting; OSRM | FR-11 … FR-13, NFR-02 |
| TD-5 | Component interaction | **REST + async jobs + polling** | Synchronous REST; Celery + Redis + WebSocket | FR-16, NFR-01, NFR-12 |
| TD-6 | Web map | **React + Leaflet** | OpenLayers; MapLibre GL | FR-17, FR-21 |
| — | Deployment | **Docker Compose** (backend + frontend containers) | — | NFR-07 |

All selected components are open source (Apache-2.0, MIT, BSD or similar) except Google Earth Engine, which is free for research and non-commercial use; this exception is justified in TD-1 and contained behind an adapter.

---

## References

- Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems, 65*, 126–139. https://doi.org/10.1016/j.compenvurbsys.2017.05.004
- Gorelick, N., et al. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment, 202*, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
- Johary, R., et al. (2023). Detection of large-scale floods using Google Earth Engine and Google Colab. *Remote Sensing, 15*(22), 5368. https://doi.org/10.3390/rs15225368
- Liang, J., et al. (2025). Rapid probabilistic inundation mapping using local thresholds and Sentinel-1 SAR data on Google Earth Engine. *Remote Sensing, 17*(10), 1747. https://doi.org/10.3390/rs17101747
