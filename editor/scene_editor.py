from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel,
    QDoubleSpinBox, QFormLayout, QGroupBox, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem,
)


@dataclass
class SceneObject:
    name: str
    image: str
    x: float = 50.0
    y: float = 100.0
    scale: float = 1.0
    visible: bool = True


class SceneCanvas(QGraphicsView):
    object_moved = Signal(str, float, float)

    def __init__(self, project: Path):
        super().__init__()
        self.project = project
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setMinimumSize(600, 400)
        self._items: dict[str, QGraphicsPixmapItem] = {}

    def load(self, scene_data: dict):
        self.scene.clear(); self._items.clear()
        width, height = scene_data.get("resolution", [1280, 720])
        bg = scene_data.get("background")
        if bg:
            pix = QPixmap(str(self.project / bg))
            if not pix.isNull():
                pix = pix.scaled(int(width), int(height), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                item = QGraphicsPixmapItem(pix); item.setZValue(-100); self.scene.addItem(item)
        else:
            rect = self.scene.addRect(0, 0, width, height, QPen(Qt.NoPen), QBrush(QColor(32, 40, 60)))
            rect.setZValue(-100)
        for raw in scene_data.get("characters", []):
            defaults = asdict(SceneObject(name="", image=""))
            data = {k: raw.get(k, v) for k, v in defaults.items()}
            obj = SceneObject(**data)
            if not obj.visible:
                continue
            pix = QPixmap(str(self.project / obj.image))
            if pix.isNull():
                continue
            item = QGraphicsPixmapItem(pix)
            item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
            item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
            item.setScale(obj.scale)
            item.setPos(width * obj.x / 100.0 - pix.width() * obj.scale / 2, height * obj.y / 100.0 - pix.height() * obj.scale)
            item.setZValue(10)
            item.setData(0, obj.name)
            self.scene.addItem(item); self._items[obj.name] = item
        self.setSceneRect(0, 0, width, height)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        item = self.scene.itemAt(self.mapToScene(event.position().toPoint()), self.transform())
        if isinstance(item, QGraphicsPixmapItem):
            name = item.data(0)
            if name:
                rect = self.scene.sceneRect()
                x = max(0.0, min(100.0, item.sceneBoundingRect().center().x() / max(1.0, rect.width()) * 100))
                y = max(0.0, min(100.0, item.sceneBoundingRect().bottom() / max(1.0, rect.height()) * 100))
                self.object_moved.emit(str(name), x, y)


class SceneEditor(QWidget):
    scene_changed = Signal(dict)

    def __init__(self, project: str | Path):
        super().__init__(); self.project = Path(project); self.scene_path = self.project / "scene.json"; self.data = {}; self._build_ui(); self.load_file()

    def _build_ui(self):
        root = QVBoxLayout(self); top = QHBoxLayout(); root.addLayout(top)
        self.scene_name = QLabel("Scene"); self.save_btn = QPushButton("Save scene"); self.reset_btn = QPushButton("Reload")
        top.addWidget(self.scene_name); top.addStretch(); top.addWidget(self.reset_btn); top.addWidget(self.save_btn)
        body = QHBoxLayout(); root.addLayout(body, 1); self.canvas = SceneCanvas(self.project); self.canvas.object_moved.connect(self.on_moved); body.addWidget(self.canvas, 4)
        side = QVBoxLayout(); body.addLayout(side, 1)
        group = QGroupBox("Characters"); gl = QVBoxLayout(group); self.list = QListWidget(); self.list.currentItemChanged.connect(self.select_character); gl.addWidget(self.list); side.addWidget(group)
        inspector = QGroupBox("Inspector"); form = QFormLayout(inspector)
        self.x_spin = QDoubleSpinBox(); self.x_spin.setRange(0, 100); self.x_spin.setSuffix(" %")
        self.y_spin = QDoubleSpinBox(); self.y_spin.setRange(0, 100); self.y_spin.setSuffix(" %")
        self.scale_spin = QDoubleSpinBox(); self.scale_spin.setRange(0.05, 5); self.scale_spin.setSingleStep(0.05)
        for w in (self.x_spin, self.y_spin, self.scale_spin): w.valueChanged.connect(self.apply_inspector)
        form.addRow("X", self.x_spin); form.addRow("Y", self.y_spin); form.addRow("Scale", self.scale_spin); side.addWidget(inspector); side.addStretch()
        self.save_btn.clicked.connect(self.save_file); self.reset_btn.clicked.connect(self.load_file)

    def load_file(self):
        if self.scene_path.exists(): self.data = json.loads(self.scene_path.read_text(encoding="utf-8"))
        else: self.data = {"name": self.project.name, "resolution": [1280, 720], "background": None, "characters": []}
        self.scene_name.setText(str(self.data.get("name", "Scene"))); self.list.clear()
        for obj in self.data.get("characters", []): self.list.addItem(obj.get("name", "Character"))
        self.canvas.project = self.project; self.canvas.load(self.data)

    def _selected(self):
        item = self.list.currentItem()
        if not item: return None
        return next((x for x in self.data.get("characters", []) if x.get("name") == item.text()), None)

    def select_character(self, current, _previous):
        obj = self._selected()
        if not obj: return
        for spin, key in ((self.x_spin, "x"), (self.y_spin, "y"), (self.scale_spin, "scale")):
            spin.blockSignals(True); spin.setValue(float(obj.get(key, 0))); spin.blockSignals(False)

    def apply_inspector(self):
        obj = self._selected()
        if not obj: return
        obj["x"], obj["y"], obj["scale"] = self.x_spin.value(), self.y_spin.value(), self.scale_spin.value(); self.canvas.load(self.data); self.scene_changed.emit(self.data)

    def on_moved(self, name: str, x: float, y: float):
        for obj in self.data.get("characters", []):
            if obj.get("name") == name: obj["x"], obj["y"] = round(x, 2), round(y, 2); break
        self.scene_changed.emit(self.data); self.select_character(self.list.currentItem(), None)

    def save_file(self):
        self.scene_path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"); self.scene_changed.emit(self.data)
