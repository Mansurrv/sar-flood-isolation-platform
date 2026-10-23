# UX Prototype

## Purpose

The prototype demonstrates how emergency services, local authorities, and GIS
analysts could compare SAR-derived flood extents and inspect possible loss of
road access to settlements. The case study is the 2024 spring floods in
Kazakhstan. It is a user-interface concept, not an operational mapping tool.

Open [`prototype/index.html`](prototype/index.html) in a browser. It is a
standalone responsive mockup and does not require a frontend build, account,
backend service, or geospatial data.

> **Important:** The map is schematic and every result is a placeholder. The
> prototype does not load Sentinel-1 scenes, call Google Earth Engine,
> calculate flood masks, or identify real isolated settlements. Do not use it
> for evacuation or emergency-response decisions.

## Intended users and scenarios

### Emergency services and local authorities

1. Select an area of interest and an available Sentinel-1 scene.
2. Choose a threshold method and request a comparison.
3. Review flood extent together with roads and settlements.
4. Identify access routes that need further review and verify them against
   reference data before using results for planning.

### GIS analysts and researchers

1. Select the same study area and scene for each comparison.
2. Compare Otsu, local/adaptive, and baseline-calibrated methods.
3. Select a method in the comparison table to highlight it and update the
   selected-method label.
4. Compare flood extent, settlement isolation, and reference agreement after
   a real processing service is connected.

## Interface and interaction

The standalone page at [`prototype/index.html`](prototype/index.html) contains:

- **Analysis controls:** area-of-interest and Sentinel-1 scene selectors, three
  threshold-method choices, and a comparison action.
- **Map concept:** candidate flood extent, road network, and settlement marker
  with a legend. The illustration is deliberately labelled as schematic and
  has no real geographic coordinates.
- **Summary indicators:** space for flood area, potentially isolated
  settlements, and agreement with reference data. Values remain blank until
  validated analysis is available.
- **Method comparison:** a table for comparing the three methods and selecting
  which method to inspect.
- **Input and processing feedback:** missing inputs are identified; submitting
  selected sample inputs explains that the static prototype does not perform
  processing.

The layout adapts to narrow screens. Controls use native form elements and
visible labels, and status messages are announced through a live region.

## Proposed API interaction

The controls represent the following example service contract. These routes
are proposals only; no API implementation is currently included in this
repository.

```http
POST /api/v1/analyses
Content-Type: application/json
```

```json
{
  "area_of_interest_id": "sample-area",
  "sentinel1_scene_id": "sample-scene",
  "methods": ["otsu", "local", "baseline_calibrated"],
  "road_network_source": "openstreetmap"
}
```

Example accepted response:

```json
{
  "analysis_id": "example-analysis-id",
  "status": "queued",
  "message": "Results will be available when processing is complete."
}
```

```http
GET /api/v1/analyses/{analysis_id}
```

Example result shape (values are illustrative, not measured):

```json
{
  "analysis_id": "example-analysis-id",
  "status": "completed",
  "results": [
    {
      "method": "otsu",
      "flood_extent_area_km2": null,
      "isolated_settlement_count": null,
      "reference_agreement": null,
      "flood_mask_url": null
    }
  ],
  "limitations": ["Example response shape only; values are not measured."]
}
```

An emergency planner would use the map and summary to identify areas for
review, while an analyst would compare method outputs and validate them
against reference data. Neither user should treat missing OpenStreetMap roads
or settlements as proof that a real route or settlement does not exist.

## Acceptance checklist

- [x] Show the workflow from area and scene selection to method comparison.
- [x] Include flood-extent, road-network, and settlement concepts.
- [x] Represent both planning and analyst scenarios.
- [x] Provide an example request and response for future API integration.
- [x] Clearly label schematic map content and avoid presenting fake results.
- [x] Work responsively as a standalone HTML page without external assets.
- [ ] Connect the controls to a real API and validated study-area data in a
      later implementation phase.
