from __future__ import annotations
from dataclasses import dataclass
from typing import Any


def get_path(state: Any, path: str, default: Any = None) -> Any:
    """Safely resolve a dotted state path from mappings or objects."""
    value = state
    for part in str(path).split('.'):
        if not part:
            return default
        if isinstance(value, dict):
            if part not in value:
                return default
            value = value[part]
        else:
            if not hasattr(value, part):
                return default
            value = getattr(value, part)
    return value


def set_path(state: Any, path: str, value: Any) -> bool:
    parts = [p for p in str(path).split('.') if p]
    if not parts:
        return False
    target = state
    for part in parts[:-1]:
        if isinstance(target, dict):
            if part not in target or not isinstance(target[part], dict):
                target[part] = {}
            target = target[part]
        else:
            if not hasattr(target, part):
                return False
            target = getattr(target, part)
    if isinstance(target, dict):
        target[parts[-1]] = value
        return True
    if hasattr(target, parts[-1]):
        setattr(target, parts[-1], value)
        return True
    return False


@dataclass(frozen=True, slots=True)
class Binding:
    widget_id: str
    property: str
    state_path: str
    default: Any = None
    transform: str | None = None


class BindingRegistry:
    """Explicit one-way state -> UI property bindings."""

    def __init__(self, bindings: list[Binding] | None = None) -> None:
        self.bindings = list(bindings or [])

    @classmethod
    def from_data(cls, data: list[dict[str, Any]]) -> 'BindingRegistry':
        return cls([Binding(str(x['widget']), str(x['property']), str(x['state']), x.get('default'), x.get('transform')) for x in data])

    def apply(self, document: Any, state: Any) -> list[str]:
        changed: list[str] = []
        for binding in self.bindings:
            widget = document.find(binding.widget_id)
            if widget is None:
                continue
            value = get_path(state, binding.state_path, binding.default)
            value = self._transform(value, binding.transform)
            if hasattr(widget, binding.property):
                setattr(widget, binding.property, value)
                changed.append(f'{binding.widget_id}.{binding.property}')
        return changed

    @staticmethod
    def _transform(value: Any, name: str | None) -> Any:
        if not name:
            return value
        if name == 'str':
            return str(value)
        if name == 'int':
            return int(value)
        if name == 'float':
            return float(value)
        if name == 'percent':
            return f'{float(value) * 100:g}%'
        raise ValueError(f'unknown binding transform: {name}')
