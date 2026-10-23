from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AlgorithmId(str, Enum):
    GLOBAL_OTSU = "DIP-14"
    LOCAL_ADAPTIVE_OTSU = "DIP-15"
    BASELINE_CHANGE_DETECTION = "DIP-16"
    POLARIZATION_SENSITIVITY = "DIP-17"
    ACCURACY_METRICS = "DIP-18"
    SETTLEMENT_ISOLATION = "DIP-19"


class RunStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    algorithm: AlgorithmId
    aoi_coordinates: dict[str, Any]
    date_start: date
    date_end: date
    polarisation: str = "VV"
    parameters: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_run_inputs(self) -> "RunRequest":
        if self.date_start >= self.date_end:
            raise ValueError("date_end must be later than date_start")
        if self.polarisation not in {"VV", "VH"}:
            raise ValueError("polarisation must be VV or VH")
        if self.aoi_coordinates.get("type") not in {"Polygon", "MultiPolygon"}:
            raise ValueError("aoi_coordinates must be a GeoJSON Polygon or MultiPolygon")
        coordinates = self.aoi_coordinates.get("coordinates")
        if not isinstance(coordinates, list) or not coordinates:
            raise ValueError("aoi_coordinates must include polygon coordinates")
        return self

    @model_validator(mode="after")
    def validate_algorithm_parameters(self) -> "RunRequest":
        if self.algorithm == AlgorithmId.ACCURACY_METRICS:
            asset_id = self.parameters.get("reference_asset_id")
            if not isinstance(asset_id, str) or not asset_id.strip():
                raise ValueError("DIP-18 requires parameters.reference_asset_id")
        return self

    def to_registry_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class RunResponse(BaseModel):
    run_id: str
    algorithm: AlgorithmId
    status: RunStatus
    stage: str
    progress: int
    created_at: datetime
    updated_at: datetime
    request: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
