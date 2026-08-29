"""Generic data-driven 2D map primitives for strategy and non-linear scenes."""

from .box_controller import BoxSelectionController
from .box_selection import BoxSelector
from .controller import MapController, MapEvent
from .interaction import MapAction, MapInteraction
from .model import Camera2D, MapConnection, MapDefinition, MapNode, MapPoint
from .multiselect import MultiSelection, SelectionChange
from .pathfinding import Route, shortest_path
from .route_builder import RouteBuilder, RouteRequest
from .selection import Selectable, SelectionModel
from .surface import MapMarker, MapSurface

__all__ = [
    "Camera2D", "MapConnection", "MapDefinition", "MapNode", "MapPoint",
    "Route", "shortest_path", "RouteBuilder", "RouteRequest",
    "Selectable", "SelectionModel", "MultiSelection", "SelectionChange",
    "MapController", "MapEvent", "MapAction", "MapInteraction",
    "BoxSelector", "BoxSelectionController", "MapMarker", "MapSurface",
]
