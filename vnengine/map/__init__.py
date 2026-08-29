"""Generic data-driven 2D map primitives for strategy and non-linear scenes."""
from .box_controller import BoxSelectionController
from .box_selection import BoxSelector
from .controller import MapController, MapEvent
from .interaction import MapAction, MapInteraction
from .entities import EntityRegistry, MapEntity
from .model import Camera2D, MapConnection, MapDefinition, MapNode, MapPoint
from .movement import Movement, MovementController
from .movement_command import MovementCommand, MovementOrder
from .movement_policy import MovementPolicy, TerrainPolicy
from .terrain import TerrainRules, connection_terrain, terrain_for
from .multiselect import MultiSelection, SelectionChange
from .pathfinding import Route, shortest_path
from .route_builder import RouteBuilder, RouteRequest
from .selection import Selectable, SelectionModel
from .surface import MapMarker, MapSurface
from .world import MapWorld
from .world_controller import MapWorldController
from .playable import MapSelectionHit, PlayableMap
from .interaction_bridge import PlayableInteractionBridge
from .loader import load_map_definition, load_playable_map
from .commands import CommandResult, MapCommandDispatcher
__all__ = ["Camera2D","MapConnection","MapDefinition","MapNode","MapPoint","Route","shortest_path","RouteBuilder","RouteRequest","Movement","MovementController","MovementCommand","MovementOrder","MovementPolicy","TerrainPolicy","TerrainRules","terrain_for","connection_terrain","EntityRegistry","MapEntity","MapWorld","MapWorldController","MapSelectionHit","PlayableMap","PlayableInteractionBridge","load_map_definition","load_playable_map","CommandResult","MapCommandDispatcher","Selectable","SelectionModel","MultiSelection","SelectionChange","MapController","MapEvent","MapAction","MapInteraction","BoxSelector","BoxSelectionController","MapMarker","MapSurface"]
