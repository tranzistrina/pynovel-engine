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
