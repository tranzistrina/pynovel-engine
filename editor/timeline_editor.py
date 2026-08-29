from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QDoubleSpinBox, QLineEdit, QLabel, QSlider, QFormLayout,
    QGroupBox, QMessageBox, QTextEdit, QSplitter, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPixmap

from vnengine.animation.timeline import Timeline
from vnengine.animation.preview import AnimationPreview


class AnimationPreviewCanvas(QGraphicsView):
    """Graphics preview of project characters at the current playhead."""

    def __init__(self, project: str | Path):
        super().__init__()
        self.project = Path(project)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor(18, 20, 28)))
        self._sprites: dict[str, QGraphicsPixmapItem] = {}
        self._base: dict[str, dict[str, float]] = {}
        self._resolution = (1280, 720)

    def load_scene(self) -> None:
        import json
        path = self.project / "scene.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        self.scene.clear(); self._sprites.clear(); self._base.clear()
        self._resolution = tuple(data.get("resolution", [1280, 720]))[:2]
        width, height = map(int, self._resolution)
        self.scene.addRect(0, 0, width, height, Qt.NoPen, QBrush(QColor(32, 38, 52)))
        for raw in data.get("characters", []):
            name = str(raw.get("name", "Character")); image = str(raw.get("image", ""))
            item = QGraphicsPixmapItem(QPixmap(str(self.project / image)))
            item.setTransformationMode(Qt.SmoothTransformation)
            self.scene.addItem(item); self._sprites[name] = item
            self._base[name] = {
                "x": float(raw.get("x", 50.0)), "y": float(raw.get("y", 100.0)),
                "scale": float(raw.get("scale", 1.0)), "opacity": float(raw.get("opacity", 1.0)),
                "rotation": float(raw.get("rotation", 0.0)),
            }
        self.scene.setSceneRect(0, 0, width, height)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def render_state(self, state: AnimationPreview) -> None:
        width, height = self._resolution
        for name, item in self._sprites.items():
            if item.pixmap().isNull():
                continue
            current = state.targets.get(name)
            values = {
                "x": current.x if current else self._base[name]["x"],
                "y": current.y if current else self._base[name]["y"],
                "scale": current.scale if current else self._base[name]["scale"],
                "opacity": current.opacity if current else self._base[name]["opacity"],
                "rotation": current.rotation if current else self._base[name]["rotation"],
            }
            item.setScale(values["scale"])
            item.setOpacity(max(0.0, min(1.0, values["opacity"])))
            item.setRotation(values["rotation"])
            rect = item.boundingRect()
            x = width * values["x"] / 100.0
            y = height * values["y"] / 100.0
            item.setPos(x - rect.width() * values["scale"] / 2.0, y - rect.height() * values["scale"])


class TimelineEditor(QWidget):
    """Animation editor with live graphical project preview."""

    def __init__(self, project: str | Path):
        super().__init__()
        self.project = Path(project)
        self.path = self.project / "animation.json"
        self.timeline = Timeline("Main")
        self.preview_model = AnimationPreview()
        self._building = False
        self._playing_timer = QTimer(self); self._playing_timer.setInterval(16); self._playing_timer.timeout.connect(self._tick_preview)
        self._build_ui(); self.load_file()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self); split = QSplitter(Qt.Horizontal); root.addWidget(split)
        left = QWidget(); ll = QVBoxLayout(left)
        top = QHBoxLayout(); self.name = QLineEdit("Main"); top.addWidget(QLabel("Timeline")); top.addWidget(self.name); ll.addLayout(top)
        self.tracks = QListWidget(); self.tracks.currentItemChanged.connect(self.select_track); ll.addWidget(self.tracks, 1)
        add = QPushButton("Add Track"); add.clicked.connect(self.add_track); ll.addWidget(add); split.addWidget(left)

        center = QWidget(); cl = QVBoxLayout(center)
        controls = QHBoxLayout(); self.playhead = QDoubleSpinBox(); self.playhead.setRange(0, 99999); self.playhead.setSingleStep(0.05); self.playhead.valueChanged.connect(self.seek)
        controls.addWidget(QLabel("Time")); controls.addWidget(self.playhead)
        for text, fn in (("Play", self.play), ("Pause", self.pause), ("Stop", self.stop)):
            btn = QPushButton(text); btn.clicked.connect(fn); controls.addWidget(btn)
        cl.addLayout(controls)
        self.timeline_slider = QSlider(Qt.Horizontal); self.timeline_slider.setRange(0, 1000); self.timeline_slider.valueChanged.connect(self.slider_seek); cl.addWidget(self.timeline_slider)
        self.canvas = AnimationPreviewCanvas(self.project); cl.addWidget(self.canvas, 4)
        self.keys = QListWidget(); self.keys.currentItemChanged.connect(self.select_key); cl.addWidget(self.keys, 2)
        split.addWidget(center)

        right = QWidget(); rl = QVBoxLayout(right)
        box = QGroupBox("Live Preview"); bl = QVBoxLayout(box); self.preview_label = QLabel("No preview target"); bl.addWidget(self.preview_label); self.preview_details = QTextEdit(); self.preview_details.setReadOnly(True); self.preview_details.setMaximumHeight(180); bl.addWidget(self.preview_details); rl.addWidget(box)
        kbox = QGroupBox("Keyframe"); form = QFormLayout(kbox)
        self.target = QLineEdit(); self.property = QLineEdit(); self.time = QDoubleSpinBox(); self.time.setRange(0, 99999); self.time.setSingleStep(0.05); self.value = QDoubleSpinBox(); self.value.setRange(-99999, 99999); self.value.setDecimals(4); self.easing = QLineEdit("linear")
        for label, widget in (("Target", self.target), ("Property", self.property), ("Time", self.time), ("Value", self.value), ("Easing", self.easing)): form.addRow(label, widget)
        rl.addWidget(kbox); add_key = QPushButton("Add / Update Key"); add_key.clicked.connect(self.add_key); rl.addWidget(add_key); remove = QPushButton("Remove Key"); remove.clicked.connect(self.remove_key); rl.addWidget(remove); save = QPushButton("Save Animation"); save.clicked.connect(self.save_file); rl.addWidget(save); rl.addStretch(); split.addWidget(right); split.setSizes([280, 850, 320])

    def load_file(self) -> None:
        if self.path.exists():
            try: self.timeline = Timeline.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
            except (OSError, ValueError, TypeError) as exc: QMessageBox.warning(self, "Animation", f"Unable to read animation.json: {exc}")
        self.name.setText(self.timeline.name); self._sync_preview_targets(); self.canvas.load_scene(); self.rebuild()

    def _sync_preview_targets(self) -> None:
        for target in {track.target for track in self.timeline.tracks if track.target}: self.preview_model.ensure_target(target)

    def _update_preview(self) -> None:
        self.preview_model.seek(self.timeline, self.timeline.time); self.canvas.render_state(self.preview_model)
        lines = []
        for name in sorted(self.preview_model.targets):
            s = self.preview_model.targets[name]
            lines.append(f"{name}: X {s.x:.2f}%  Y {s.y:.2f}%  Scale {s.scale:.3f}  Opacity {s.opacity:.3f}  Rotation {s.rotation:.2f}°")
        self.preview_label.setText(f"Playhead: {self.timeline.time:.3f}s" if lines else "No preview target"); self.preview_details.setPlainText("\n".join(lines))

    def rebuild(self) -> None:
        self._building = True
        try:
            self.tracks.clear()
            for track in self.timeline.tracks:
                item = QListWidgetItem(f"{track.target}.{track.property} ({len(track.keys)} keys)"); item.setData(Qt.UserRole, (track.target, track.property)); self.tracks.addItem(item)
            duration = max(0.01, self.timeline.duration); self.timeline_slider.setValue(int(self.timeline.time / duration * 1000)); self.playhead.setValue(self.timeline.time); self.rebuild_keys(); self._update_preview()
        finally: self._building = False

    def rebuild_keys(self) -> None:
        self.keys.clear(); item = self.tracks.currentItem()
        if item is None: return
        target, prop = item.data(Qt.UserRole); track = next((t for t in self.timeline.tracks if t.target == target and t.property == prop), None)
        if track is None: return
        for index, key in enumerate(track.keys):
            row = QListWidgetItem(f"{key.time:.3f}s  =  {key.value:g}  [{key.easing}]"); row.setData(Qt.UserRole, index); self.keys.addItem(row)

    def select_track(self, current, _previous) -> None: self.rebuild_keys()
    def select_key(self, current, _previous) -> None:
        if current is None or self.tracks.currentItem() is None: return
        target, prop = self.tracks.currentItem().data(Qt.UserRole); track = next((t for t in self.timeline.tracks if t.target == target and t.property == prop), None)
        if track is None: return
        key = track.keys[int(current.data(Qt.UserRole))]; self.target.setText(target); self.property.setText(prop); self.time.setValue(key.time); self.value.setValue(key.value); self.easing.setText(key.easing)

    def add_track(self) -> None:
        target = self.target.text().strip() or "Alice"; prop = self.property.text().strip() or "x"
        if not any(t.target == target and t.property == prop for t in self.timeline.tracks):
            from vnengine.animation.timeline import Track
            self.timeline.add_track(Track(target, prop)); self._sync_preview_targets(); self.rebuild()

    def add_key(self) -> None:
        try: self.timeline.add_keyframe(self.target.text().strip(), self.property.text().strip(), self.time.value(), self.value.value(), self.easing.text().strip() or "linear")
        except ValueError as exc: QMessageBox.warning(self, "Keyframe", str(exc)); return
        self._sync_preview_targets(); self.rebuild()

    def remove_key(self) -> None:
        track_item = self.tracks.currentItem(); key_item = self.keys.currentItem()
        if track_item is None or key_item is None: return
        target, prop = track_item.data(Qt.UserRole); track = next((t for t in self.timeline.tracks if t.target == target and t.property == prop), None)
        if track is None: return
        del track.keys[int(key_item.data(Qt.UserRole))]; self.timeline.duration = max((t.duration for t in self.timeline.tracks), default=0.0); self.rebuild()

    def seek(self, value: float) -> None:
        if self._building: return
        self.timeline.seek(value); self._update_preview(); self.timeline_slider.blockSignals(True); self.timeline_slider.setValue(int(self.timeline.time / max(0.01, self.timeline.duration) * 1000)); self.timeline_slider.blockSignals(False)

    def slider_seek(self, value: int) -> None:
        if self._building: return
        self.seek(self.timeline.duration * value / 1000.0 if self.timeline.duration else 0.0)

    def play(self) -> None: self.timeline.play(); self._playing_timer.start()
    def pause(self) -> None: self.timeline.pause(); self._playing_timer.stop()
    def stop(self) -> None: self.timeline.stop(); self._playing_timer.stop(); self.rebuild()
    def _tick_preview(self) -> None:
        self.timeline.update(0.016); self._update_preview(); self.playhead.blockSignals(True); self.playhead.setValue(self.timeline.time); self.playhead.blockSignals(False)
        if not self.timeline.playing: self._playing_timer.stop()

    def save_file(self) -> None:
        self.timeline.name = self.name.text().strip() or "Main"; self.path.parent.mkdir(parents=True, exist_ok=True); self.path.write_text(json.dumps(self.timeline.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
