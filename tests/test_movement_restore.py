import pytest
from vnengine.map.model import MapDefinition
from vnengine.map.movement import MovementController


def controller():
    return MovementController(MapDefinition.from_dict({"width": 100, "height": 100, "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 10, "y": 0}]}))


def test_restore_rejects_invalid_progress():
    with pytest.raises(ValueError, match="progress"):
        controller().restore({"e": {"route": ["a", "b"], "position": [1, 0], "progress": 2}})


def test_restore_rejects_unknown_route_node():
    with pytest.raises(ValueError, match="route"):
        controller().restore({"e": {"route": ["a", "missing"], "position": [1, 0]}})
