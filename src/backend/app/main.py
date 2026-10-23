import logging
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shapely.geometry import shape
from shapely.validation import explain_validity

from . import registry
from .models import RunRequest, RunResponse, RunStatus
from .processing import execute_analysis

load_dotenv("config/.env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAR Flood Isolation Platform API",
    description="Asynchronous Sentinel-1 flood mapping and road isolation API.",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def process_run(run_id: str) -> None:
    try:
        request = registry.get_request(run_id)
        geometry = shape(request.aoi_coordinates)
        if geometry.is_empty or not geometry.is_valid:
            raise ValueError(f"Invalid AOI geometry: {explain_validity(geometry)}")
        if geometry.geom_type not in {"Polygon", "MultiPolygon"}:
            raise ValueError("AOI must be a Polygon or MultiPolygon.")

        registry.update_run(
            run_id,
            status=RunStatus.PROCESSING,
            stage="Initializing Google Earth Engine",
            progress=3,
        )

        def set_stage(stage: str, progress: int) -> None:
            registry.update_run(
                run_id,
                status=RunStatus.PROCESSING,
                stage=stage,
                progress=progress,
            )

        result = execute_analysis(request, set_stage)
        registry.update_run(
            run_id,
            status=RunStatus.COMPLETED,
            stage="Completed",
            progress=100,
            result=result,
        )
        logger.info(
            "Completed run %s algorithm=%s scenes=%s dates=%s..%s",
            run_id,
            request.algorithm.value,
            result.get("provenance", {}).get("scene_ids"),
            request.date_start,
            request.date_end,
        )
    except Exception as error:
        logger.exception("Analysis run %s failed", run_id)
        message = str(error).strip() or "Processing failed."
        lowered_message = message.lower()
        if any(
            marker in lowered_message
            for marker in ("timed out", "timeout", "quota", "deadline exceeded", "resource exhausted")
        ):
            message = (
                "Google Earth Engine timed out or exceeded a quota. "
                "Try a smaller AOI or date window and retry."
            )
        try:
            registry.update_run(
                run_id,
                status=RunStatus.FAILED,
                stage="Failed",
                progress=100,
                error=message,
            )
        except Exception:
            logger.exception("Could not persist failure state for run %s", run_id)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/runs", response_model=RunResponse, status_code=202)
async def create_run(
    request: RunRequest,
    background_tasks: BackgroundTasks,
) -> RunResponse:
    try:
        geometry = shape(request.aoi_coordinates)
    except (TypeError, ValueError, KeyError) as error:
        raise HTTPException(
            status_code=422,
            detail="aoi_coordinates is not valid GeoJSON geometry.",
        ) from error
    if geometry.is_empty or not geometry.is_valid:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid AOI geometry: {explain_validity(geometry)}",
        )
    min_lon, min_lat, max_lon, max_lat = geometry.bounds
    if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
        raise HTTPException(
            status_code=422,
            detail="AOI coordinates must be longitude/latitude in EPSG:4326.",
        )
    run_id = str(uuid4())
    try:
        run = registry.create_run(run_id, request)
    except Exception as error:
        logger.exception("Could not create analysis run")
        raise HTTPException(
            status_code=500,
            detail="Could not persist the analysis request in the run registry.",
        ) from error
    background_tasks.add_task(process_run, run_id)
    return run


@app.get("/api/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str) -> RunResponse:
    try:
        return registry.get_run(run_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Analysis run not found.") from error
