from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView

from vnengine.animation.timeline import Timeline


class AnimationPreviewCanvas(QGraphicsView):
    """Lightweight 1280x720 animation preview driven by timeline samples."""

    def __init__(self, project: str | Path):
        super().__init__()
        self.project = Path(project)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setMinimumSize(560, 320)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor(18, 20, 28)))
        self._sprites: dict[str, QGraphicsPixmapItem] = {}
        self._labels: dict[str, QGraphicsRectItem] = {}
        self._resolution = (1280, 720)
        self._base_state: dict[str, dict[str, float | str]] = {}

    def load_scene(self, scene_path: str | Path | None = None) -> None:
        path = Path(scene_path) if scene_path else self.project / "scene.json"
        if not path.is_absolute():
            path = self.project / path
        self.scene.clear()
        self._sprites.clear()
        self._labels.clear()
        self._base_state.clear()
        if path.exists():
            import json
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = {"resolution": [1280, 720], "characters": []}
        self._resolution = tuple(data.get("resolution", [1280, 720]))[:2]
        width, height = int(self._resolution[0]), int(self._resolution[1])
        self.scene.addRect(0, 0, width, height, Qt.NoPen, QBrush(QColor(32, 38, 52)))
        for raw in data.get("characters", []):
            name = str(raw.get("name", "Character"))
            image = str(raw.get("image", ""))
            item = QGraphicsPixmapItem()
            if image:
                pixmap = QPixmap(str(self.project / image))
                if not pixmap.isNull():
                    item.setPixmap(pixmap)
            item.setTransformationMode(Qt.SmoothTransformation)
            self.scene.addItem(item)
            self._sprites[name] = item
            self._base_state[name] = {
                "x": float(raw.get("x", 50.0)),
                "y": float(raw.get("y", 100.0)),
                "scale": float(raw.get("scale", 1.0)),
                "opacity": float(raw.get("opacity", 1.0)),
                "rotation": float(raw.get("rotation", 0.0)),
            }
        self.scene.setSceneRect(0, 0, width, height)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def apply_timeline(self, timeline: Timeline, time: float) -> dict[tuple[str, str], float]:
        values = timeline.sample(time)
        states = {name: dict(state) for name, state in self._base_state.items()}
        for (target, prop), value in values.items():
            if target in states:
                states[target][prop] = value
        width, height = self._resolution
        for name, item in self._sprites.items():
            state = states.get(name, {})
            if item.pixmap().isNull():
                continue
            scale = float(state.get("scale", 1.0))
            x = width * float(state.get("x", 50.0)) / 100.0
            y = height * float(state.get("y", 100.0)) / 100.0
            item.setScale(scale)
            item.setRotation(float(state.get("rotation", 0.0)))
            item.setOpacity(max(0.0, min(1.0, float(state.get("opacity", 1.0)))))
            rect = item.boundingRect()
            item.setPos(x - rect.width() * scale / 2.0, y - rect.height() * scale)
        self._base_state = states
        return values
