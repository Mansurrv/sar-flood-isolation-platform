from fastapi.testclient import TestClient

from src.backend.app import main, registry
from src.backend.app.models import AlgorithmId

client = TestClient(main.app)
AOI = {
    "type": "Polygon",
    "coordinates": [[
        [71.0, 51.0],
        [71.1, 51.0],
        [71.1, 51.1],
        [71.0, 51.1],
        [71.0, 51.0],
    ]],
}
VALID_REQUEST = {
    "algorithm": "DIP-14",
    "aoi_coordinates": AOI,
    "date_start": "2024-04-01",
    "date_end": "2024-04-05",
    "polarisation": "VV",
    "parameters": {"histogram_bins": 256},
}


def test_run_request_is_persisted_and_processing_failure_is_visible(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("SAR_RUNS_DB", str(tmp_path / "runs.sqlite3"))

    def fail_without_gee(request, set_stage):
        assert request.algorithm.value == "DIP-14"
        assert callable(set_stage)
        raise RuntimeError("GEE_PROJECT_ID is not configured")

    monkeypatch.setattr(main, "execute_analysis", fail_without_gee)
    response = client.post("/api/runs", json=VALID_REQUEST)

    assert response.status_code == 202
    run_id = response.json()["run_id"]
    status = client.get(f"/api/runs/{run_id}")
    assert status.status_code == 200
    assert status.json()["status"] == "failed"
    assert status.json()["stage"] == "Failed"
    assert status.json()["error"] == "GEE_PROJECT_ID is not configured"

    saved_request = registry.get_request(run_id)
    assert saved_request.algorithm.value == "DIP-14"
    assert saved_request.aoi_coordinates == AOI
    assert saved_request.parameters == {"histogram_bins": 256}


def test_request_rejects_non_polygon_or_invalid_dates():
    invalid_aoi = {**VALID_REQUEST, "aoi_coordinates": {"type": "Point", "coordinates": [0, 0]}}
    invalid_dates = {**VALID_REQUEST, "date_start": "2024-04-06"}

    assert client.post("/api/runs", json=invalid_aoi).status_code == 422
    assert client.post("/api/runs", json=invalid_dates).status_code == 422


def test_request_rejects_self_intersecting_aoi(monkeypatch, tmp_path):
    monkeypatch.setenv("SAR_RUNS_DB", str(tmp_path / "runs.sqlite3"))
    bow_tie = {
        "type": "Polygon",
        "coordinates": [[
            [0, 0],
            [1, 1],
            [0, 1],
            [1, 0],
            [0, 0],
        ]],
    }
    response = client.post(
        "/api/runs",
        json={**VALID_REQUEST, "aoi_coordinates": bow_tie},
    )
    assert response.status_code == 422


def test_dip18_requires_reference_asset():
    request = {**VALID_REQUEST, "algorithm": "DIP-18", "parameters": {}}
    response = client.post("/api/runs", json=request)
    assert response.status_code == 422


def test_all_six_algorithm_identifiers_are_supported():
    supported = {algorithm.value for algorithm in AlgorithmId}
    assert supported == {f"DIP-{number}" for number in range(14, 20)}


def test_missing_gee_project_fails_run_without_fabricating_results(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("SAR_RUNS_DB", str(tmp_path / "runs.sqlite3"))
    monkeypatch.delenv("GEE_PROJECT_ID", raising=False)
    monkeypatch.delenv("GEE_SERVICE_ACCOUNT", raising=False)
    monkeypatch.delenv("GEE_KEY_FILE", raising=False)

    response = client.post("/api/runs", json=VALID_REQUEST)
    assert response.status_code == 202
    run = client.get(f"/api/runs/{response.json()['run_id']}").json()
    assert run["status"] == "failed"
    assert run["result"] is None
    assert "GEE_PROJECT_ID" in run["error"]


def test_unknown_run_returns_not_found(monkeypatch, tmp_path):
    monkeypatch.setenv("SAR_RUNS_DB", str(tmp_path / "runs.sqlite3"))
    assert client.get("/api/runs/not-a-run").status_code == 404
