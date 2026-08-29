from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Character:
    name: str
    image: str
    position: str = "center"
    visible: bool = True
    x: float = 50.0
    y: float = 100.0
    scale: float = 1.0
    opacity: float = 1.0
    expression: str = "neutral"
    rotation: float = 0.0

@dataclass
class ChoiceOption:
    text: str
    target: str

@dataclass
class Action:
    kind: str
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class Story:
    actions: list[Action]
    labels: dict[str, int]
    title: str = "PyNovel Game"
    variables: dict[str, Any] = field(default_factory=dict)

@dataclass
class SaveState:
    action_index: int
    variables: dict[str, Any]
    history: list[tuple[str, str]]
    background: str | None = None
    characters: dict[str, dict[str, Any]] = field(default_factory=dict)

@dataclass
class GameState:
    """Compatibility state container expected by vnengine.core imports and runtime."""
    running: bool = True
    dialogue: tuple[str, str] | None = None
    choice_options: list[ChoiceOption] = field(default_factory=list)
    text_progress: float = 0.0
    settings: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    background: str | None = None
    characters: dict[str, dict[str, Any]] = field(default_factory=dict)
    choice_index: int = 0
    scene: str | None = None
    def set(self, key: str, value: Any) -> None:
        setattr(self, key, value)
