from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import sqrt
from statistics import median
from typing import Any, Callable

from shapely.geometry import shape

from .gee_client import GeeClient, otsu_from_histogram
from .models import AlgorithmId, RunRequest

StageCallback = Callable[[str, int], None]
DEFAULT_BINS = 256


def execute_analysis(
    request: RunRequest,
    set_stage: StageCallback,
) -> dict[str, Any]:
    gee = GeeClient()
    set_stage("Querying Sentinel-1 GRD", 10)
    if request.algorithm == AlgorithmId.POLARIZATION_SENSITIVITY:
        polarization_option = str(
            request.parameters.get("polarizations", "VV + VH")
        )
        bands = (
            ("VV", "VH")
            if polarization_option == "VV + VH"
            else (polarization_option,)
        )
        if any(band not in {"VV", "VH"} for band in bands):
            raise ValueError("polarizations must be VV + VH, VV, or VH")
    else:
        bands = None
    image, scene_ids = gee.sentinel1_composite(
        request, request.date_start, request.date_end, bands=bands
    )
    aoi = gee.geometry(request.aoi_coordinates)
    provenance: dict[str, Any] = {
        "gee_collection": "COPERNICUS/S1_GRD",
        "scene_ids": scene_ids,
        "date_start": request.date_start.isoformat(),
        "date_end": request.date_end.isoformat(),
        "polarisation": (
            request.parameters.get("polarizations", "VV + VH")
            if request.algorithm == AlgorithmId.POLARIZATION_SENSITIVITY
            else request.polarisation
        ),
        "algorithm": request.algorithm.value,
    }
    set_stage("Computing flood mask", 35)

    if request.algorithm == AlgorithmId.GLOBAL_OTSU:
        bins = _positive_int(request.parameters.get("histogram_bins", DEFAULT_BINS), "histogram_bins")
        result = _global_otsu(gee, image, aoi, request.polarisation, bins)
    elif request.algorithm == AlgorithmId.LOCAL_ADAPTIVE_OTSU:
        result = _local_adaptive_otsu(gee, image, aoi, request)
    elif request.algorithm == AlgorithmId.BASELINE_CHANGE_DETECTION:
        result = _baseline_change(gee, image, aoi, request, provenance)
    elif request.algorithm == AlgorithmId.POLARIZATION_SENSITIVITY:
        result = _polarization_sensitivity(gee, image, aoi, request)
    elif request.algorithm == AlgorithmId.ACCURACY_METRICS:
        result = _accuracy_metrics(gee, image, aoi, request)
    elif request.algorithm == AlgorithmId.SETTLEMENT_ISOLATION:
        result = _settlement_isolation(
            gee, image, aoi, request, set_stage, provenance
        )
    else:
        raise ValueError(f"Unsupported algorithm: {request.algorithm.value}")

    result["provenance"] = provenance
    result["aoi_bounds"] = list(shape(request.aoi_coordinates).bounds)
    return result


def _global_otsu(
    gee: GeeClient,
    image: Any,
    aoi: Any,
    band: str,
    bins: int,
) -> dict[str, Any]:
    threshold = gee.otsu_threshold(image, band, aoi, bins=bins)
    mask = image.select(band).lt(threshold).rename("flood").toByte()
    return _mask_result(gee, mask, aoi, {"threshold_db": threshold, "band": band})


def _local_adaptive_otsu(
    gee: GeeClient,
    image: Any,
    aoi: Any,
    request: RunRequest,
) -> dict[str, Any]:
    ee = gee.ee
    band = request.polarisation
    bins = _positive_int(request.parameters.get("histogram_bins", DEFAULT_BINS), "histogram_bins")
    tile_size = _positive_int(request.parameters.get("tile_size", 256), "tile_size")
    minimum_ashman_d = float(request.parameters.get("minimum_ashman_d", 2.0))
    if minimum_ashman_d < 0:
        raise ValueError("minimum_ashman_d must be non-negative")

    grid = aoi.coveringGrid(ee.Projection("EPSG:3857"), tile_size * 10)
    histogram_rows = (
        image.select(band)
        .reduceRegions(
            collection=grid,
            reducer=ee.Reducer.histogram(maxBuckets=bins),
            scale=10,
            tileScale=4,
        )
        .getInfo()
        .get("features", [])
    )
    threshold_images = []
    accepted = []
    for row in histogram_rows:
        properties = row.get("properties", {})
        histogram = properties.get(band)
        if not histogram or not histogram.get("histogram"):
            continue
        threshold = otsu_from_histogram(histogram)
        ashman_d = _ashman_d(histogram, threshold)
        if ashman_d < minimum_ashman_d:
            continue
        geometry = ee.Geometry(row["geometry"])
        threshold_images.append(
            ee.Image.constant(threshold).rename("threshold").clip(geometry)
        )
        accepted.append(threshold)

    fallback = not threshold_images
    if fallback:
        global_threshold = gee.otsu_threshold(image, band, aoi, bins=bins)
        threshold_image = ee.Image.constant(global_threshold).rename("threshold")
    else:
        threshold_image = ee.ImageCollection.fromImages(threshold_images).mosaic()
    mask = (
        image.select(band)
        .lt(threshold_image)
        .rename("flood")
        .toByte()
        .clip(aoi)
    )
    metadata = {
        "accepted_tiles": len(accepted),
        "tested_tiles": len(histogram_rows),
        "median_threshold_db": float(median(accepted)) if accepted else global_threshold,
        "fallback_to_global": fallback,
        "band": band,
    }
    return _mask_result(gee, mask, aoi, metadata)


def _baseline_change(
    gee: GeeClient,
    post_image: Any,
    aoi: Any,
    request: RunRequest,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    period_days = (request.date_end - request.date_start).days
    pre_end = request.date_start - timedelta(days=1)
    pre_start = pre_end - timedelta(days=period_days)
    pre_image, scene_ids = gee.sentinel1_composite(
        request, pre_start, pre_end, bands=(request.polarisation,)
    )
    provenance["baseline"] = {
        "date_start": pre_start.isoformat(),
        "date_end": pre_end.isoformat(),
        "scene_ids": scene_ids,
    }
    band = request.polarisation
    change_threshold = float(request.parameters.get("change_threshold_db", -3.0))
    post_cap = float(request.parameters.get("post_event_cap_db", -15.0))
    post_band = post_image.select(band)
    change = post_band.subtract(pre_image.select(band))
    mask = (
        change.lt(change_threshold)
        .And(post_band.lt(post_cap))
        .rename("flood")
        .toByte()
        .clip(aoi)
    )
    return _mask_result(
        gee,
        mask,
        aoi,
        {
            "change_threshold_db": change_threshold,
            "post_event_cap_db": post_cap,
            "baseline_period_days": period_days + 1,
        },
    )


def _polarization_sensitivity(
    gee: GeeClient,
    image: Any,
    aoi: Any,
    request: RunRequest,
) -> dict[str, Any]:
    ee = gee.ee
    bins = _positive_int(request.parameters.get("histogram_bins", DEFAULT_BINS), "histogram_bins")
    channel_option = str(request.parameters.get("polarizations", "VV + VH"))
    selected_bands = (
        ("VV", "VH")
        if channel_option == "VV + VH"
        else (channel_option,)
    )
    if any(band not in {"VV", "VH"} for band in selected_bands):
        raise ValueError("polarizations must be VV + VH, VV, or VH")
    thresholds = {
        band: gee.otsu_threshold(image, band, aoi, bins=bins)
        for band in selected_bands
    }
    mode = str(request.parameters.get("fusion_mode", "OR")).upper()
    if mode not in {"AND", "OR"}:
        raise ValueError("fusion_mode must be AND or OR")
    sensitivity = float(request.parameters.get("sensitivity_db", 1.0))
    if sensitivity < 0:
        raise ValueError("sensitivity_db must be non-negative")
    offsets = sorted(set((-sensitivity, 0.0, sensitivity)))
    layers: list[dict[str, Any]] = []
    counts: list[dict[str, float | int]] = []
    for offset in offsets:
        masks = [
            image.select(band).lt(thresholds[band] + offset)
            for band in selected_bands
        ]
        if len(masks) == 1:
            fused = masks[0]
        elif mode == "AND":
            fused = masks[0].And(masks[1])
        else:
            fused = masks[0].Or(masks[1])
        mask = fused.rename("flood").toByte().clip(aoi)
        count = (
            mask.selfMask()
            .reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=aoi,
                scale=10,
                maxPixels=1_000_000_000,
                tileScale=4,
            )
            .get("flood")
            .getInfo()
        )
        counts.append({"offset_db": offset, "flooded_pixels": int(count or 0)})
        layers.append(
            gee.mask_layer(mask, f"Polarisation fusion {offset:+g} dB")
        )
    return {
        "layers": layers,
        "metrics": {
            "thresholds_db": thresholds,
            "fusion_mode": mode,
            "sensitivity_counts": counts,
        },
    }


def _accuracy_metrics(
    gee: GeeClient,
    image: Any,
    aoi: Any,
    request: RunRequest,
) -> dict[str, Any]:
    ee = gee.ee
    band = request.polarisation
    predicted_threshold = gee.otsu_threshold(image, band, aoi)
    predicted = image.select(band).lt(predicted_threshold).rename("predicted")
    reference_asset_id = str(request.parameters["reference_asset_id"]).strip()
    reference = ee.Image(reference_asset_id).select(0).gt(0).rename("reference")
    categories = predicted.multiply(2).add(reference).rename("category").uint8()
    histogram = (
        categories.reduceRegion(
            reducer=ee.Reducer.frequencyHistogram(),
            geometry=aoi,
            scale=10,
            maxPixels=1_000_000_000,
            tileScale=4,
        )
        .get("category")
        .getInfo()
    )
    counts = {int(key): int(value) for key, value in (histogram or {}).items()}
    tn, fn, fp, tp = (counts.get(key, 0) for key in range(4))
    total = tn + fp + fn + tp
    if total == 0:
        raise RuntimeError("Reference mask and Sentinel-1 data have no overlapping valid pixels.")
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    iou = _ratio(tp, tp + fp + fn)
    f1 = _ratio(2 * tp, 2 * tp + fp + fn)
    observed = (tp + tn) / total
    expected = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / total**2
    kappa = _ratio(observed - expected, 1 - expected) if expected != 1 else float(observed == 1)
    mask = predicted.rename("flood").toByte()
    result = _mask_result(
        gee,
        mask,
        aoi,
        {"threshold_db": predicted_threshold, "band": band},
    )
    result["metrics"] = {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "iou": iou,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "cohen_kappa": kappa,
        "reference_asset_id": reference_asset_id,
    }
    return result


def _settlement_isolation(
    gee: GeeClient,
    image: Any,
    aoi: Any,
    request: RunRequest,
    set_stage: StageCallback,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    import geopandas as gpd
    import networkx as nx
    import osmnx as ox
    from shapely.geometry import shape
    from shapely.ops import unary_union

    band = request.polarisation
    threshold = gee.otsu_threshold(image, band, aoi)
    mask = image.select(band).lt(threshold).rename("flood").toByte().clip(aoi)
    flood_geojson = gee.vectorize(mask, aoi)
    flood_shapes = [
        shape(feature["geometry"])
        for feature in flood_geojson.get("features", [])
        if feature.get("geometry")
    ]
    flood_union = unary_union(flood_shapes) if flood_shapes else None

    set_stage("Downloading OSM road graph and settlements", 55)
    aoi_shape = shape(request.aoi_coordinates)
    graph = ox.graph_from_polygon(
        aoi_shape,
        network_type="drive",
        simplify=True,
        retain_all=True,
        truncate_by_edge=True,
    )
    if graph.number_of_nodes() == 0:
        raise RuntimeError("OpenStreetMap returned no drivable road graph for this AOI.")
    projected_graph = ox.project_graph(graph)
    provenance["osm_query_timestamp"] = datetime.now(timezone.utc).isoformat()
    provenance["osm_projected_crs"] = str(projected_graph.graph.get("crs"))
    _, edges = ox.graph_to_gdfs(projected_graph, nodes=True, edges=True)
    projected_crs = edges.crs
    if flood_union is not None:
        flood_projected = gpd.GeoSeries([flood_union], crs="EPSG:4326").to_crs(projected_crs).iloc[0]
    else:
        flood_projected = None

    connectivity = nx.Graph()
    connectivity.add_nodes_from(projected_graph.nodes(data=True))
    removed_edges: list[tuple[Any, Any, Any]] = []
    for start, end, key, data in projected_graph.edges(keys=True, data=True):
        edge_geometry = data.get("geometry")
        if edge_geometry is None:
            start_data, end_data = projected_graph.nodes[start], projected_graph.nodes[end]
            from shapely.geometry import LineString

            edge_geometry = LineString(
                [(start_data["x"], start_data["y"]), (end_data["x"], end_data["y"])]
            )
        if flood_projected is not None and edge_geometry.intersects(flood_projected):
            removed_edges.append((start, end, key))
        else:
            connectivity.add_edge(start, end, **data)
    components = list(nx.connected_components(connectivity))
    if not components:
        raise RuntimeError("No connected road components remain after flood-edge removal.")
    largest_component = max(components, key=len)

    set_stage("Classifying settlement connectivity", 78)
    places = ox.features_from_polygon(
        aoi_shape,
        tags={"place": ["city", "town", "village", "hamlet", "isolated_dwelling"]},
    )
    if places.empty:
        raise RuntimeError("OpenStreetMap returned no settlement features for this AOI.")
    places = places[places.geometry.notna()].copy().to_crs(projected_crs)
    places["geometry"] = places.geometry.centroid
    settlement_features = []
    snap_distance = float(request.parameters.get("snap_distance_m", 1000))
    for index, place in places.iterrows():
        point = place.geometry
        name = str(place.get("name") or f"OSM settlement {index}")
        if flood_projected is not None and flood_projected.covers(point):
            access = "inundated"
            node = None
            distance = None
        else:
            node = ox.distance.nearest_nodes(
                projected_graph,
                X=float(point.x),
                Y=float(point.y),
            )
            node_data = projected_graph.nodes[node]
            distance = sqrt(
                (float(node_data["x"]) - point.x) ** 2
                + (float(node_data["y"]) - point.y) ** 2
            )
            if distance > snap_distance:
                access = "no_road_access"
            elif node in largest_component:
                access = "connected"
            else:
                access = "isolated"
        settlement_features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": list(
                        gpd.GeoSeries([point], crs=projected_crs)
                        .to_crs("EPSG:4326")
                        .iloc[0]
                        .coords[0]
                    ),
                },
                "properties": {
                    "osm_id": str(index),
                    "name": name,
                    "place": str(place.get("place", "")),
                    "access": access,
                    "nearest_node": str(node) if node is not None else None,
                    "snap_distance_m": distance,
                },
            }
        )

    retained = projected_graph.copy()
    retained.remove_edges_from(removed_edges)
    if retained.number_of_edges():
        _, retained_edges = ox.graph_to_gdfs(retained, nodes=True, edges=True)
        road_features = retained_edges.to_crs("EPSG:4326").__geo_interface__
    else:
        road_features = {"type": "FeatureCollection", "features": []}
    road_features["features"] = [
        {
            **feature,
            "properties": {
                **feature.get("properties", {}),
                "kind": "road",
            },
        }
        for feature in road_features.get("features", [])
    ]
    return {
        "layers": [
            gee.mask_layer(mask, "Flood mask"),
            _geojson_layer("flood_polygons", "Flood polygons", flood_geojson),
            _geojson_layer("road_network", "Road network", road_features),
            _geojson_layer(
                "settlements",
                "Settlement access",
                {"type": "FeatureCollection", "features": settlement_features},
            ),
        ],
        "metrics": {
            "otsu_threshold_db": threshold,
            "road_nodes": projected_graph.number_of_nodes(),
            "road_edges": projected_graph.number_of_edges(),
            "removed_flooded_edges": len(removed_edges),
            "largest_component_nodes": len(largest_component),
            "settlement_count": len(settlement_features),
            "isolated_count": sum(
                feature["properties"]["access"] == "isolated"
                for feature in settlement_features
            ),
            "inundated_count": sum(
                feature["properties"]["access"] == "inundated"
                for feature in settlement_features
            ),
            "connected_reference": "largest connected road-network component",
        },
    }


def _mask_result(
    gee: GeeClient,
    mask: Any,
    aoi: Any,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "layers": [
            gee.mask_layer(mask, "Flood mask"),
            _geojson_layer("flood_polygons", "Flood polygons", gee.vectorize(mask, aoi)),
        ],
        "metrics": metadata,
    }


def _geojson_layer(
    layer_id: str,
    name: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    if data.get("type") == "Feature":
        data = {"type": "FeatureCollection", "features": [data]}
    return {"id": layer_id, "name": name, "type": "geojson", "data": data}


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _ashman_d(histogram: dict[str, Any], threshold: float) -> float:
    counts = histogram["histogram"]
    means = histogram["bucketMeans"]
    lower = [(count, mean) for count, mean in zip(counts, means) if mean < threshold]
    upper = [(count, mean) for count, mean in zip(counts, means) if mean >= threshold]
    if not lower or not upper:
        return 0.0

    def moments(items: list[tuple[float, float]]) -> tuple[float, float]:
        weight = sum(count for count, _ in items)
        mean = sum(count * value for count, value in items) / weight
        variance = sum(count * (value - mean) ** 2 for count, value in items) / weight
        return mean, sqrt(variance)

    lower_mean, lower_std = moments(lower)
    upper_mean, upper_std = moments(upper)
    denominator = sqrt(lower_std**2 + upper_std**2)
    return (
        float("inf")
        if denominator == 0
        else sqrt(2.0) * abs(lower_mean - upper_mean) / denominator
    )


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0
