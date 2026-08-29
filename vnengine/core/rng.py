from __future__ import annotations
import random
from typing import Any


class DeterministicRNG:
    """Serializable seeded RNG for reproducible gameplay simulation."""

    def __init__(self, seed: int | str = 0) -> None:
        self._rng = random.Random()
        self.seed(seed)

    def seed(self, value: int | str) -> None:
        self._seed = value
        self._rng.seed(value)

    def random(self) -> float:
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, sequence):
        if not sequence:
            raise IndexError("cannot choose from an empty sequence")
        return self._rng.choice(sequence)

    def chance(self, probability: float) -> bool:
        if not 0.0 <= probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")
        return self.random() < probability

    def get_state(self) -> tuple[Any, ...]:
        return self._rng.getstate()

    def set_state(self, state: tuple[Any, ...]) -> None:
        self._rng.setstate(state)

    def serialize(self) -> dict[str, Any]:
        return {"seed": self._seed, "state": self._rng.getstate()}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self._seed = payload.get("seed", 0)
        state = payload.get("state")
        if state is None:
            self._rng.seed(self._seed)
        else:
            self._rng.setstate(_to_tuple(state))


def _to_tuple(value):
    if isinstance(value, list):
        return tuple(_to_tuple(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_to_tuple(item) for item in value)
    return value
