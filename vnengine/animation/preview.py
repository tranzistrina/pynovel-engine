from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vnengine.animation.timeline import Timeline


@dataclass(slots=True)
class PreviewState:
    """Editable preview transform for one timeline target."""
    x: float = 50.0
    y: float = 100.0
    scale: float = 1.0
    opacity: float = 1.0
    rotation: float = 0.0


class AnimationPreview:
    """Apply timeline samples to lightweight preview objects without Qt/Pygame."""

    PROPERTIES = {"x", "y", "scale", "opacity", "rotation"}

    def __init__(self, initial: dict[str, PreviewState] | None = None):
        self.targets: dict[str, PreviewState] = initial or {}

    def ensure_target(self, name: str) -> PreviewState:
        return self.targets.setdefault(name, PreviewState())

    def seek(self, timeline: Timeline, time: float) -> dict[str, PreviewState]:
        values = timeline.sample(time)
        for (target, prop), value in values.items():
            if prop in self.PROPERTIES:
                setattr(self.ensure_target(target), prop, float(value))
        return self.targets

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {name: {
            "x": state.x,
            "y": state.y,
            "scale": state.scale,
            "opacity": state.opacity,
            "rotation": state.rotation,
        } for name, state in self.targets.items()}
