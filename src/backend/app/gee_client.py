import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .models import RunRequest


class GeeClient:
    """Google Earth Engine adapter used by the processing pipeline."""

    def __init__(self) -> None:
        import ee

        service_account = os.environ.get("GEE_SERVICE_ACCOUNT")
        key_file = os.environ.get("GEE_KEY_FILE")
        project = os.environ.get("GEE_PROJECT_ID")
        if not project:
            raise RuntimeError(
                "Set GEE_PROJECT_ID to a Google Cloud project enabled for Earth Engine."
            )
        if service_account or key_file:
            if not service_account or not key_file:
                raise RuntimeError(
                    "Set both GEE_SERVICE_ACCOUNT and GEE_KEY_FILE, or configure "
                    "Google Application Default Credentials."
                )
            key_path = Path(key_file).expanduser()
            if not key_path.is_file():
                raise RuntimeError("The configured GEE key file does not exist.")
            credentials = ee.ServiceAccountCredentials(service_account, str(key_path))
            ee.Initialize(credentials, project=project)
        else:
            ee.Initialize(project=project)
        self.ee = ee

    def geometry(self, geojson: dict[str, Any]) -> Any:
        return self.ee.Geometry(geojson, proj="EPSG:4326", geodesic=False)

    def sentinel1_composite(
        self,
        request: RunRequest,
        start: date,
        end: date,
        bands: tuple[str, ...] | None = None,
    ) -> tuple[Any, list[str]]:
        selected_bands = bands or (request.polarisation,)
        ee = self.ee
        aoi = self.geometry(request.aoi_coordinates)
        collection = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(aoi)
            .filterDate(start.isoformat(), (end + timedelta(days=1)).isoformat())
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.eq("resolution_meters", 10))
        )
        for band in selected_bands:
            collection = collection.filter(
                ee.Filter.listContains("transmitterReceiverPolarisation", band)
            )
        count = int(collection.size().getInfo())
        if count == 0:
            raise RuntimeError(
                "No Sentinel-1 GRD scenes match the AOI, date range, and "
                f"polarisation(s) {', '.join(selected_bands)}."
            )
        scene_ids = collection.aggregate_array("system:index").getInfo()
        composite = collection.select(list(selected_bands)).median().clip(aoi)
        return composite, scene_ids

    def otsu_threshold(
        self,
        image: Any,
        band: str,
        aoi: Any,
        *,
        bins: int = 256,
    ) -> float:
        histogram = (
            image.select(band)
            .reduceRegion(
                reducer=self.ee.Reducer.histogram(maxBuckets=bins),
                geometry=aoi,
                scale=10,
                maxPixels=1_000_000_000,
                tileScale=4,
            )
            .get(band)
            .getInfo()
        )
        if not histogram or not histogram.get("histogram"):
            raise RuntimeError(
                f"Sentinel-1 band {band} has no valid pixels in the supplied AOI."
            )
        return otsu_from_histogram(histogram)

    def mask_layer(self, mask: Any, name: str) -> dict[str, str]:
        visualized = mask.selfMask().visualize(
            min=0,
            max=1,
            palette=["ffffff", "2563eb"],
            opacity=0.65,
        )
        map_info = visualized.getMapId()
        tile_fetcher = map_info.get("tile_fetcher")
        if tile_fetcher is None or not tile_fetcher.url_format:
            raise RuntimeError(f"Earth Engine did not return tiles for {name}.")
        return {
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "type": "xyz",
            "url": tile_fetcher.url_format,
        }

    def vectorize(self, mask: Any, aoi: Any) -> dict[str, Any]:
        features = (
            mask.selfMask()
            .toByte()
            .rename("flood")
            .reduceToVectors(
                geometry=aoi,
                scale=10,
                geometryType="polygon",
                eightConnected=False,
                labelProperty="flood",
                maxPixels=1_000_000_000,
                tileScale=4,
            )
            .map(lambda feature: feature.simplify(10))
        )
        return features.getInfo()


def otsu_from_histogram(histogram: dict[str, Any]) -> float:
    counts = histogram.get("histogram")
    means = histogram.get("bucketMeans")
    if not counts or not means or len(counts) != len(means):
        raise RuntimeError("Earth Engine returned an invalid histogram.")
    total = sum(counts)
    if total <= 0:
        raise RuntimeError("Earth Engine returned an empty histogram.")

    cumulative_count = 0.0
    cumulative_sum = 0.0
    total_sum = sum(count * mean for count, mean in zip(counts, means))
    best_variance = -1.0
    best_threshold: float | None = None
    for index in range(len(counts) - 1):
        cumulative_count += counts[index]
        cumulative_sum += counts[index] * means[index]
        right_count = total - cumulative_count
        if cumulative_count <= 0 or right_count <= 0:
            continue
        left_mean = cumulative_sum / cumulative_count
        right_mean = (total_sum - cumulative_sum) / right_count
        variance = cumulative_count * right_count * (left_mean - right_mean) ** 2
        if variance > best_variance:
            best_variance = variance
            best_threshold = (means[index] + means[index + 1]) / 2
    if best_threshold is None:
        raise RuntimeError("Otsu threshold cannot be determined from this histogram.")
    return float(best_threshold)
