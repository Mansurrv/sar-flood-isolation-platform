# SAR Flood Isolation Platform

**Brief Description:** Automated web platform for rapid SAR-based flood mapping
with settlement isolation assessment: a case study of the 2024 spring floods in
Kazakhstan.

---

## 1. Problem Statement

The threshold largely decides the result of SAR flood mapping, and there is no
agreed way to set it. A ±1 dB shift in VV/VH changes F1 from 63.5% to 74.9%
(Amoah, 2026). Otsu overestimates flooded area (Falaras et al., 2025). Khanh &
Le (2026) name threshold selection as the dominant source of uncertainty.

A second problem: studies stop at the water polygon. None of the reviewed
papers checks whether the road network stays connected — i.e., which
settlements are cut off. Emergency services need exactly that for evacuation
priorities.

## 2. Target Users

- **Emergency services** — evacuation priorities and relief planning.
- **GIS analysts and researchers** — comparable, reproducible threshold methods.
- **Local authorities** — road and infrastructure planning.

## 3. Expected Outcomes

- Controlled comparison of Otsu, local (adaptive) and baseline-calibrated
  thresholding on one flood event with one reference.
- Sensitivity analysis (±1 dB, AND/OR polarisation logic).
- List of settlements isolated from the OpenStreetMap road network under each
  flood mask.
- Reproducible GEE pipeline and web platform (FastAPI + React).

---

## 4. Team Members and Responsibilities

| Участник | Роль | Ответственность |
|----------|------|-----------------|
| Backend / SAR Lead | GEE pipeline, threshold algorithms, metrics, FastAPI |
| Frontend / GIS / PM Lead | React UI, OSM road graph, isolation count, YouTrack |
| Supervisor | Methodology, review, acceptance |

---

## 5. Project Scope and Current Status

### Scope (In)
- Sentinel-1 GRD data via Google Earth Engine.
- 2024 Kazakhstan spring flood case study.
- Three threshold methods + sensitivity analysis.
- OSM road graph and isolation count.
- Web platform (FastAPI REST API + React SPA).

### Scope (Out)
- Authentication and multi-user management.
- Real-time streaming.
- Sentinel-2 optical as the primary data source.
- Mobile application.

### Current Development Status (Pre-defense 1)

| Component | Status |
|-----------|--------|
| Project proposal | ✅ |
| Evidence of relevance (interviews) | ✅ |
| Literature review | ✅ |
| Existing system comparison | ✅ |
| Technology comparison | ✅ |
| Requirements specification | ✅ |
| Architecture & diagrams | ✅ |
| UX / prototype | ✅ |
| Verification & evaluation plan | ✅ |
| Project management (YouTrack) | ✅ |
| Supervisor feedback | ✅ |
| Algorithm reference implementations | Available on DIP-14—19 feature branches |
| GEE processing pipeline | DIP-14—19 orchestration implemented in FastAPI backend |
| Frontend / asynchronous processing API | Implemented; requires configured GEE and network access |

---

## 6. Selected Technologies

| Layer | Technology | Why |
|-------|------------|-----|
| SAR processing | Google Earth Engine (Python API) | Free, fast, 30+ scenes <1 h (Johary, 2023) |
| Threshold algorithms | Otsu, local (adaptive), baseline-calibrated | Compared in this project |
| Road graph | OSMnx + OpenStreetMap | Open data, shortest-path API |
| Backend | FastAPI (Python) | Lightweight REST, OpenAPI docs |
| Frontend | React + Leaflet | Map rendering, simple SPA |
| Storage | GEE assets + GeoPackage | Versioned, reproducible |
| Deployment | Docker Compose | One-command local run |

---

## 7. Links

- **YouTrack Project:** https://sar-flood-isolation.youtrack.cloud/agiles/204-0/current

- **Documentation:** [`docs/`](docs/)
  - [01. Project Proposal](docs/01_project_proposal.md)
  - [02. Literature Review](docs/02_literature_review.md)
  - [03. Existing Systems Comparison](docs/03_existing_systems_comparison.md)
  - [04. Technology Comparison](docs/04_technology_comparison.md)
  - [05. Requirements](docs/05_requirements.md)
  - [06. Architecture](docs/06_architecture.md)
  - [07. Verification Plan](docs/07_verification_plan.md)
  - [09. Interviews](docs/09_interviews.md)
  - [10. UX Prototype](docs/10_ux_prototype.md)
  - [11. Project Management & Risks](docs/11_project_management_risks.md)
  - [12. Supervisor Feedback](docs/12_supervisor_feedback.md)
  - [20. User Needs and Usability Survey](docs/20_user_survey.md)
- **Architecture Decision Records:** [`docs/adr/`](docs/adr/)
- **Diagrams:** [`docs/diagrams/`](docs/diagrams/)
- **Prototype:** [`docs/prototype/`](docs/prototype/)

---

## 8. Repository Structure

```text
sar-flood-isolation-platform/
├── config/
│   ├── .env.example         # Safe placeholders; copy locally to .env
│   └── requirements.txt     # Python dependency definitions
├── data/                    # Local/private data; contents are ignored
├── docs/
│   ├── 01_project_proposal.md
│   ├── 02_literature_review.md
│   ├── 03_existing_systems_comparison.md
│   ├── 04_technology_comparison.md
│   ├── 05_requirements.md
│   ├── 06_architecture.md
│   ├── 07_verification_plan.md
│   ├── 09_interviews.md
│   ├── 10_ux_prototype.md
│   ├── 11_project_management_risks.md
│   ├── 12_supervisor_feedback.md
│   ├── adr/                 # Architecture decision records
│   ├── diagrams/
│   │   ├── source/          # Editable Mermaid / draw.io sources
│   │   └── exports/         # Readable SVG / PNG / PDF exports
│   └── prototype/           # Interactive UX prototype and documentation
├── src/
│   ├── backend/app/         # FastAPI, GEE adapter, analysis pipeline and SQLite registry
│   ├── frontend/            # React + Vite + Leaflet application
│   └── processing/          # Algorithm implementations in feature branches
├── tests/
│   ├── fixtures/            # Small synthetic or sanitized test materials
│   └── unit/                # Algorithm and API tests
├── .gitignore               # Secret, data, build, and local-file exclusions
└── README.md
```

Keep editable diagram sources beside their exports. Add only synthetic or
sanitized materials to `tests/fixtures/`; keep credentials and private data
outside the repository. Real results depend on Sentinel-1 availability,
configured Earth Engine access and OpenStreetMap coverage for the selected AOI.

## 9. Setup, Execution, and Testing

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Earth Engine project with API access and suitable authentication
- Network access to Earth Engine, OpenStreetMap Overpass and OSM tile servers
- Docker + Docker Compose (optional)

### Setup

```bash
# 1. Clone
git clone https://github.com/mansurrv/sar-flood-isolation-platform.git
cd sar-flood-isolation-platform

# 2. Backend
python -m venv .venv
source .venv/bin/activate
pip3 install -r config/requirements.txt
cp config/.env.example config/.env
# Set GEE_PROJECT_ID. For a service account, set GEE_SERVICE_ACCOUNT and
# GEE_KEY_FILE to a key file stored outside the repository.
# Alternatively configure Google Application Default Credentials.

```

### Run the application

Start the API from the repository root (the API reads `config/.env`):

```bash
python -m uvicorn src.backend.app.main:app --reload --port 8000
```

In a second terminal, start the frontend:

```bash
cd src/frontend
npm install
npm run dev
```

Open the Vite URL (normally <http://localhost:5173>). Paste a valid GeoJSON
Polygon/MultiPolygon AOI, choose dates, polarisation and an algorithm, then run
the analysis. The frontend posts to `POST /api/runs` and polls
`GET /api/runs/{run_id}` every three seconds. Completed responses include
Earth Engine XYZ flood-mask tiles, GeoJSON layers and algorithm metrics when
available. DIP-16 derives an equal-length baseline window immediately before
the requested period. DIP-18 requires a reference-mask Earth Engine asset ID.
DIP-19 downloads OSM roads and place features and treats the largest remaining
connected road component as the connectivity reference.

Earth Engine computation, OSM data completeness and quota limits affect
results. Review the recorded parameters and provenance before interpreting
them; these research outputs are not certified for emergency operations.

Run the Python tests from the repository root:

```bash
python -m pytest tests/unit -q
```
