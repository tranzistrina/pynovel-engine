from __future__ import annotations
from dataclasses import dataclass

def ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

@dataclass
class Tween:
    start: float
    end: float
    duration: float
    elapsed: float = 0.0

    def step(self, dt: float) -> float:
        self.elapsed = min(self.duration, self.elapsed + max(0.0, dt))
        if self.duration <= 0:
            return self.end
        return self.start + (self.end - self.start) * ease_in_out(self.elapsed / self.duration)

    @property
    def done(self) -> bool:
        return self.elapsed >= self.duration
