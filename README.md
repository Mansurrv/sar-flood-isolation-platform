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
| Runnable code / web platform | ⏳ next phase |

> ⚠️ **Note:** Full application is **not required** at Pre-defense 1. The
> repository demonstrates that analysis, design, planning, and management have
> already taken place. Code and runnable setup will be added in the next phase.

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
│   ├── adr/                 # Architecture decision records
│   ├── diagrams/
│   │   ├── source/          # Editable Mermaid / draw.io sources
│   │   └── exports/         # Readable SVG / PNG / PDF exports
│   └── prototype/           # Interactive UX prototype and documentation
├── src/
│   ├── backend/             # FastAPI application
│   ├── frontend/            # React application
│   └── processing/          # SAR and road-network processing components
├── tests/
│   ├── fixtures/            # Small synthetic or sanitized test materials
│   └── unit/                # Unit tests
├── .gitignore               # Secret, data, build, and local-file exclusions
└── README.md
```

Keep editable diagram sources beside their exports. Add only synthetic or
sanitized materials to `tests/fixtures/`; keep credentials and private data
outside the repository. The current `src/` and `tests/` directories are
scaffolding; runnable application code and automated tests have not been added.

## 9. Setup, Execution, and Testing

> ⚠️ **Note:** These instructions will be fully activated **as soon as
> runnable code is available**. Currently only the environment skeleton
> exists.

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Earth Engine account
- Docker + Docker Compose (optional)

### Setup

```bash
# 1. Clone
git clone https://github.com/mansurrv/sar-flood-isolation-platform.git
cd sar-flood-isolation-platform

# 2. Backend
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt

# 3. Environment (placeholder values only)
cp config/.env.example config/.env
# Replace placeholders locally; never commit config/.env or credential files.

```

The backend and frontend commands become runnable after their application
manifests and code are added. Run automated tests with `pytest` once tests are
present.
