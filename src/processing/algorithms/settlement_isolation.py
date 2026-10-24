"""Flood impact analysis for settlements on a road graph."""

from collections import deque
from dataclasses import dataclass
from math import hypot, isfinite
from typing import Hashable, Literal, Mapping, Protocol, Sequence


class PointLike(Protocol):
    x: float
    y: float


class GeometryLike(Protocol):
    def buffer(self, distance: float) -> "GeometryLike": ...

    def covers(self, other: PointLike) -> bool: ...

    def intersects(self, other: "GeometryLike") -> bool: ...


SettlementStatus = Literal[
    "isolated", "inundated", "connected", "no_road_access", "disconnected_before"
]


@dataclass(frozen=True)
class RoadEdge:
    """One road edge with geometry in a projected, metre-based CRS."""

    start: Hashable
    end: Hashable
    geometry: GeometryLike
    bidirectional: bool = True


@dataclass(frozen=True)
class Settlement:
    """Settlement point and stable source identifier."""

    settlement_id: str
    point: PointLike


@dataclass(frozen=True)
class SettlementIsolation:
    """Isolation classification and snapping diagnostics for one settlement."""

    settlement_id: str
    status: SettlementStatus
    node_id: Hashable | None
    snap_distance_m: float | None


@dataclass(frozen=True)
class IsolationAnalysis:
    """Sorted settlement results and total count of flood-blocked edges."""

    settlements: tuple[SettlementIsolation, ...]
    removed_edge_count: int


def analyze_settlement_isolation(
    nodes: Mapping[Hashable, tuple[float, float]],
    edges: Sequence[RoadEdge],
    settlements: Sequence[Settlement],
    hubs: set[Hashable] | frozenset[Hashable],
    flood_geometry: GeometryLike,
    *,
    flood_buffer_m: float = 10.0,
    maximum_snap_distance_m: float = 2_000.0,
) -> IsolationAnalysis:
    """Compare settlement reachability before and after flood-blocked roads.

    Coordinates must use a projected CRS whose units are metres. Flooded edges
    are removed when their geometry intersects the buffered flood polygon.
    Settlements are snapped to the nearest graph node by Euclidean distance.
    """
    if not nodes:
        raise ValueError("nodes must not be empty")
    if not hubs or not hubs.issubset(nodes):
        raise ValueError("hubs must be a non-empty subset of graph nodes")
    if (
        not isfinite(flood_buffer_m)
        or flood_buffer_m < 0
        or not isfinite(maximum_snap_distance_m)
        or maximum_snap_distance_m < 0
    ):
        raise ValueError("buffer and snap distances must be finite and non-negative")
    if len({item.settlement_id for item in settlements}) != len(settlements):
        raise ValueError("settlement IDs must be unique")
    for coordinates in nodes.values():
        if (
            len(coordinates) != 2
            or not isfinite(coordinates[0])
            or not isfinite(coordinates[1])
        ):
            raise ValueError("node coordinates must be finite x/y pairs")
    for settlement in settlements:
        if not isfinite(settlement.point.x) or not isfinite(settlement.point.y):
            raise ValueError("settlement coordinates must be finite")
    for edge in edges:
        if edge.start not in nodes or edge.end not in nodes:
            raise ValueError("every road edge endpoint must exist in nodes")

    flood_zone = flood_geometry.buffer(flood_buffer_m)
    baseline_reverse = _reverse_adjacency(nodes, edges, blocked_zone=None)
    affected_reverse = _reverse_adjacency(nodes, edges, blocked_zone=flood_zone)
    baseline_reachable = _reachable_from_hubs(baseline_reverse, hubs)
    affected_reachable = _reachable_from_hubs(affected_reverse, hubs)
    removed_edge_count = sum(
        flood_zone.intersects(edge.geometry) for edge in edges
    )

    node_order = sorted(nodes, key=str)
    results: list[SettlementIsolation] = []
    for settlement in settlements:
        if flood_geometry.covers(settlement.point):
            results.append(
                SettlementIsolation(
                    settlement.settlement_id, "inundated", None, None
                )
            )
            continue

        node_id, distance = min(
            (
                (
                    candidate,
                    hypot(
                        settlement.point.x - nodes[candidate][0],
                        settlement.point.y - nodes[candidate][1],
                    ),
                )
                for candidate in node_order
            ),
            key=lambda item: (item[1], str(item[0])),
        )
        if distance > maximum_snap_distance_m:
            status: SettlementStatus = "no_road_access"
        elif node_id not in baseline_reachable:
            status = "disconnected_before"
        elif node_id not in affected_reachable:
            status = "isolated"
        else:
            status = "connected"

        results.append(
            SettlementIsolation(
                settlement.settlement_id, status, node_id, float(distance)
            )
        )

    results.sort(key=lambda item: item.settlement_id)
    return IsolationAnalysis(tuple(results), int(removed_edge_count))


def _reverse_adjacency(
    nodes: Mapping[Hashable, tuple[float, float]],
    edges: Sequence[RoadEdge],
    *,
    blocked_zone: GeometryLike | None,
) -> dict[Hashable, set[Hashable]]:
    reverse: dict[Hashable, set[Hashable]] = {node: set() for node in nodes}
    for edge in edges:
        if blocked_zone is not None and blocked_zone.intersects(edge.geometry):
            continue
        reverse[edge.end].add(edge.start)
        if edge.bidirectional:
            reverse[edge.start].add(edge.end)
    return reverse


def _reachable_from_hubs(
    reverse_adjacency: Mapping[Hashable, set[Hashable]],
    hubs: set[Hashable] | frozenset[Hashable],
) -> set[Hashable]:
    reachable = set(hubs)
    queue = deque(hubs)
    while queue:
        node = queue.popleft()
        for predecessor in reverse_adjacency[node]:
            if predecessor not in reachable:
                reachable.add(predecessor)
                queue.append(predecessor)
    return reachable
