from dataclasses import dataclass

import pytest

from src.processing.algorithms.settlement_isolation import (
    RoadEdge,
    Settlement,
    analyze_settlement_isolation,
)


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Line:
    start: Point
    end: Point


@dataclass(frozen=True)
class Box:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def buffer(self, distance):
        return Box(
            self.min_x - distance,
            self.min_y - distance,
            self.max_x + distance,
            self.max_y + distance,
        )

    def covers(self, point):
        return (
            self.min_x <= point.x <= self.max_x
            and self.min_y <= point.y <= self.max_y
        )

    def intersects(self, other):
        if isinstance(other, Box):
            return not (
                self.max_x < other.min_x
                or other.max_x < self.min_x
                or self.max_y < other.min_y
                or other.max_y < self.min_y
            )
        return not (
            max(other.start.x, other.end.x) < self.min_x
            or min(other.start.x, other.end.x) > self.max_x
            or max(other.start.y, other.end.y) < self.min_y
            or min(other.start.y, other.end.y) > self.max_y
        )


def test_detects_new_isolation_and_preserves_other_statuses():
    nodes = {
        "hub": (0.0, 0.0),
        "west": (1.0, 0.0),
        "east": (2.0, 0.0),
        "far": (3.0, 0.0),
        "disconnected": (10.0, 0.0),
    }
    edges = [
        RoadEdge("hub", "west", Line(Point(0, 0), Point(1, 0))),
        RoadEdge("west", "east", Line(Point(1, 0), Point(2, 0))),
        RoadEdge("east", "far", Line(Point(2, 0), Point(3, 0))),
    ]
    settlements = [
        Settlement("isolated", Point(3.0, 0.0)),
        Settlement("connected", Point(1.0, 0.0)),
        Settlement("flooded", Point(1.5, 0.0)),
        Settlement("already-cut-off", Point(10.0, 0.0)),
        Settlement("remote", Point(100.0, 0.0)),
    ]

    result = analyze_settlement_isolation(
        nodes,
        edges,
        settlements,
        {"hub"},
        Box(1.4, -0.2, 1.6, 0.2),
        flood_buffer_m=0.0,
        maximum_snap_distance_m=2.0,
    )

    statuses = {item.settlement_id: item.status for item in result.settlements}
    assert statuses == {
        "already-cut-off": "disconnected_before",
        "connected": "connected",
        "flooded": "inundated",
        "isolated": "isolated",
        "remote": "no_road_access",
    }
    assert result.removed_edge_count == 1
    assert [item.settlement_id for item in result.settlements] == sorted(statuses)


def test_directed_roads_require_a_route_toward_a_hub():
    nodes = {"hub": (0.0, 0.0), "settlement": (1.0, 0.0)}
    edge = RoadEdge(
        "settlement",
        "hub",
        Line(Point(1, 0), Point(0, 0)),
        bidirectional=False,
    )
    flood = Box(10.0, 10.0, 11.0, 11.0)

    result = analyze_settlement_isolation(
        nodes,
        [edge],
        [Settlement("village", Point(1.0, 0.0))],
        {"hub"},
        flood,
        flood_buffer_m=0,
    )

    assert result.settlements[0].status == "connected"


@pytest.mark.parametrize(
    ("nodes", "edges", "settlements", "hubs", "kwargs", "message"),
    [
        ({}, [], [], set(), {}, "nodes must not be empty"),
        ({"a": (0, 0)}, [], [], set(), {}, "non-empty subset"),
        (
            {"a": (0, 0)},
            [],
            [],
            {"a"},
            {"flood_buffer_m": -1},
            "non-negative",
        ),
        (
            {"a": (0, 0), "b": (1, 0)},
            [RoadEdge("a", "missing", Line(Point(0, 0), Point(1, 0)))],
            [],
            {"a"},
            {},
            "endpoint must exist",
        ),
    ],
)
def test_rejects_invalid_graph_inputs(nodes, edges, settlements, hubs, kwargs, message):
    with pytest.raises(ValueError, match=message):
        analyze_settlement_isolation(
            nodes, edges, settlements, hubs, Box(5, 5, 6, 6), **kwargs
        )


def test_duplicate_settlement_ids_are_rejected():
    settlements = [
        Settlement("same", Point(0.0, 0.0)),
        Settlement("same", Point(1.0, 0.0)),
    ]
    with pytest.raises(ValueError, match="unique"):
        analyze_settlement_isolation(
            {"hub": (0.0, 0.0)},
            [],
            settlements,
            {"hub"},
            Box(5, 5, 6, 6),
        )
