# Analysis Interface

## Application

The React/Vite frontend in [`../src/frontend/`](../src/frontend/) submits
Sentinel-1 analysis jobs to the FastAPI service in
[`../src/backend/app/`](../src/backend/app/). Users provide:

- An AOI as a GeoJSON `Polygon` or `MultiPolygon` in longitude/latitude.
- Inclusive Sentinel-1 start and end dates.
- A polarisation and one algorithm, DIP-14 through DIP-19.
- Algorithm-specific parameters; DIP-18 additionally requires a reference
  mask Earth Engine asset ID.

The UI polls the asynchronous run endpoint every three seconds, shows the
processing stage and progress, and creates layer toggles from layers actually
returned by the API. Earth Engine tile URLs render raster flood masks; GeoJSON
layers show polygons, roads and settlement access. Settlement popups show the
name and access classification.

## API

Create a run:

```http
POST /api/runs
Content-Type: application/json
```

```json
{
  "algorithm": "DIP-14",
  "aoi_coordinates": {
    "type": "Polygon",
    "coordinates": [[[71.0, 51.0], [71.1, 51.0], [71.1, 51.1], [71.0, 51.1], [71.0, 51.0]]]
  },
  "date_start": "2024-04-01",
  "date_end": "2024-04-05",
  "polarisation": "VV",
  "parameters": {"histogram_bins": 256}
}
```

Poll the returned run ID:

```http
GET /api/runs/{run_id}
```

The response contains `status`, `stage`, `progress`, the complete submitted
request for reproducibility, result layers, metrics and scene provenance.
Failures are returned as a terminal `failed` status with an error message.

## Processing behavior

- **DIP-14:** median Sentinel-1 GRD composite and global Otsu flood threshold.
- **DIP-15:** per-tile histograms, Otsu thresholds and Ashman’s D validation;
  falls back to global Otsu if no tile passes.
- **DIP-16:** compares the requested composite with an equal-length composite
  immediately preceding its start date.
- **DIP-17:** computes VV/VH Otsu masks, configurable AND/OR fusion and
  sensitivity offsets.
- **DIP-18:** evaluates the Otsu mask against a configured Earth Engine
  reference-mask asset.
- **DIP-19:** removes OSM road edges intersecting the Otsu flood polygons,
  builds connected components and classifies OSM settlements against the
  largest remaining component. This is the configured connectivity reference,
  not a routing analysis to named emergency hubs.

The Earth Engine Python API is isolated in `GeeClient`. Authentication uses
Application Default Credentials or service-account settings supplied through
`config/.env`; private key files must be mounted or stored outside the
repository. Run parameters, dates, asset/scene IDs and result metadata are
stored in the SQLite run registry.

## Scope and limitations

The interface and API execute remote Earth Engine and OpenStreetMap processing
when credentials and network access are configured. OSM coverage can be
incomplete; Earth Engine requests can fail due to quotas, timeouts or missing
imagery. DIP-16 uses a simple preceding-period baseline, DIP-18 requires a
compatible reference asset, and DIP-19 uses largest-component connectivity.
These outputs require research validation before any operational use.

[`prototype/index.html`](prototype/index.html) remains as a standalone,
static design artifact and is not connected to this API.
