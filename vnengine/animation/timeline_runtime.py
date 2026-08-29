from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vnengine.animation.timeline import Timeline


class TimelinePlayer:
    """Runtime player for serialized animation timelines."""

    def __init__(self, project: str | Path):
        self.project = Path(project)
        self.timelines: dict[str, Timeline] = {}
        self.playing: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self, path: str | Path | None = None) -> None:
        source = Path(path) if path else self.project / "animation.json"
        if not source.is_absolute():
            source = self.project / source
        if not source.exists():
            self.timelines = {}
            return
        data = json.loads(source.read_text(encoding="utf-8"))
        raw = data.get("timelines", data if isinstance(data, dict) else {})
        self.timelines = {str(name): Timeline.from_dict(payload) for name, payload in raw.items()}

    def play(self, name: str) -> bool:
        timeline = self.timelines.get(name)
        if timeline is None:
            return False
        duration = timeline.duration
        self.playing[name] = {"time": 0.0, "duration": duration, "loop": timeline.loop}
        return True

    def stop(self, name: str) -> None:
        self.playing.pop(name, None)

    def seek(self, name: str, time: float) -> dict[str, float]:
        timeline = self.timelines.get(name)
        if timeline is None:
            return {}
        state = self.playing.setdefault(name, {"time": 0.0, "duration": timeline.duration, "loop": timeline.loop})
        state["time"] = max(0.0, min(float(time), timeline.duration))
        return timeline.sample(state["time"])

    def update(self, dt: float) -> dict[str, dict[str, float]]:
        updates: dict[str, dict[str, float]] = {}
        for name, state in list(self.playing.items()):
            timeline = self.timelines.get(name)
            if timeline is None:
                self.playing.pop(name, None)
                continue
            duration = timeline.duration
            state["time"] += max(0.0, dt)
            if duration <= 0:
                updates[name] = timeline.sample(0.0)
                if not state["loop"]:
                    self.playing.pop(name, None)
                continue
            if state["time"] >= duration:
                if state["loop"]:
                    state["time"] %= duration
                else:
                    state["time"] = duration
                    updates[name] = timeline.sample(state["time"])
                    self.playing.pop(name, None)
                    continue
            updates[name] = timeline.sample(state["time"])
        return updates
