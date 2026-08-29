from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QDoubleSpinBox, QLineEdit, QLabel, QSlider, QFormLayout,
    QGroupBox, QMessageBox, QTextEdit
)

from vnengine.animation.timeline import Timeline, Keyframe
from vnengine.animation.preview import AnimationPreview, PreviewState


class TimelineEditor(QWidget):
    """Timeline editor with live lightweight transform preview."""

    def __init__(self, project: str | Path):
        super().__init__()
        self.project = Path(project)
        self.path = self.project / "animation.json"
        self.timeline = Timeline("Main")
        self.preview_model = AnimationPreview()
        self._building = False
        self._playing_timer = QTimer(self)
        self._playing_timer.setInterval(16)
        self._playing_timer.timeout.connect(self._tick_preview)
        self._build_ui()
        self.load_file()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        top = QHBoxLayout()
        self.name = QLineEdit("Main")
        top.addWidget(QLabel("Timeline"))
        top.addWidget(self.name)
        left.addLayout(top)

        self.tracks = QListWidget()
        self.tracks.currentItemChanged.connect(self.select_track)
        left.addWidget(self.tracks, 1)

        add = QPushButton("Add Track")
        add.clicked.connect(self.add_track)
        left.addWidget(add)
        root.addLayout(left, 2)

        center = QVBoxLayout()
        control = QHBoxLayout()
        self.playhead = QDoubleSpinBox()
        self.playhead.setRange(0, 99999)
        self.playhead.setSingleStep(0.05)
        self.playhead.valueChanged.connect(self.seek)
        control.addWidget(QLabel("Time"))
        control.addWidget(self.playhead)
        for label, fn in (("Play", self.play), ("Pause", self.pause), ("Stop", self.stop)):
            btn = QPushButton(label)
            btn.clicked.connect(fn)
            control.addWidget(btn)
        center.addLayout(control)

        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1000)
        self.timeline_slider.valueChanged.connect(self.slider_seek)
        center.addWidget(self.timeline_slider)

        self.keys = QListWidget()
        self.keys.currentItemChanged.connect(self.select_key)
        center.addWidget(self.keys, 1)
        root.addLayout(center, 4)

        right = QVBoxLayout()
        preview_box = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_box)
        self.preview_label = QLabel("No preview target")
        self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.preview_label.setMinimumHeight(180)
        preview_layout.addWidget(self.preview_label)
        self.preview_details = QTextEdit()
        self.preview_details.setReadOnly(True)
        self.preview_details.setMaximumHeight(170)
        preview_layout.addWidget(self.preview_details)
        right.addWidget(preview_box)

        box = QGroupBox("Keyframe")
        form = QFormLayout(box)
        self.target = QLineEdit()
        self.property = QLineEdit()
        self.time = QDoubleSpinBox(); self.time.setRange(0, 99999); self.time.setSingleStep(0.05)
        self.value = QDoubleSpinBox(); self.value.setRange(-99999, 99999); self.value.setDecimals(4)
        self.easing = QLineEdit("linear")
        for label, widget in (("Target", self.target), ("Property", self.property), ("Time", self.time), ("Value", self.value), ("Easing", self.easing)):
            form.addRow(label, widget)
        right.addWidget(box)
        apply = QPushButton("Add / Update Key")
        apply.clicked.connect(self.add_key)
        right.addWidget(apply)
        remove = QPushButton("Remove Key")
        remove.clicked.connect(self.remove_key)
        right.addWidget(remove)
        save = QPushButton("Save Animation")
        save.clicked.connect(self.save_file)
        right.addWidget(save)
        right.addStretch()
        root.addLayout(right, 2)

    def load_file(self) -> None:
        if self.path.exists():
            try:
                self.timeline = Timeline.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
            except (OSError, ValueError, TypeError) as exc:
                QMessageBox.warning(self, "Animation", f"Unable to read animation.json: {exc}")
        self.name.setText(self.timeline.name)
        self._sync_preview_targets()
        self.rebuild()

    def _sync_preview_targets(self) -> None:
        targets = sorted({track.target for track in self.timeline.tracks if track.target})
        for target in targets:
            self.preview_model.ensure_target(target)

    def _update_preview(self) -> None:
        self.preview_model.seek(self.timeline, self.timeline.time)
        targets = sorted(self.preview_model.targets)
        if not targets:
            self.preview_label.setText("No preview target")
            self.preview_details.clear()
            return
        lines = []
        for name in targets:
            state = self.preview_model.targets[name]
            lines.append(
                f"{name}:  X {state.x:.2f}%   Y {state.y:.2f}%   "
                f"Scale {state.scale:.3f}   Opacity {state.opacity:.3f}   "
                f"Rotation {state.rotation:.2f}°"
            )
        self.preview_label.setText(f"Playhead: {self.timeline.time:.3f}s")
        self.preview_details.setPlainText("\n".join(lines))

    def rebuild(self) -> None:
        self._building = True
        try:
            self.tracks.clear()
            for track in self.timeline.tracks:
                item = QListWidgetItem(f"{track.target}.{track.property} ({len(track.keys)} keys)")
                item.setData(Qt.UserRole, (track.target, track.property))
                self.tracks.addItem(item)
            duration = max(0.01, self.timeline.duration)
            self.timeline_slider.setValue(int(self.timeline.time / duration * 1000))
            self.playhead.setValue(self.timeline.time)
            self.rebuild_keys()
            self._update_preview()
        finally:
            self._building = False

    def rebuild_keys(self) -> None:
        self.keys.clear()
        item = self.tracks.currentItem()
        if item is None:
            return
        target, prop = item.data(Qt.UserRole)
        track = next((t for t in self.timeline.tracks if t.target == target and t.property == prop), None)
        if track is None:
            return
        for index, key in enumerate(track.keys):
            row = QListWidgetItem(f"{key.time:.3f}s  =  {key.value:g}  [{key.easing}]")
            row.setData(Qt.UserRole, index)
            self.keys.addItem(row)

    def select_track(self, current, _previous) -> None:
        self.rebuild_keys()

    def select_key(self, current, _previous) -> None:
        if current is None:
            return
        track_item = self.tracks.currentItem()
        if track_item is None:
            return
        target, prop = track_item.data(Qt.UserRole)
        track = next((t for t in self.timeline.tracks if t.target == target and t.property == prop), None)
        if track is None:
            return
        key = track.keys[int(current.data(Qt.UserRole))]
        self.target.setText(target); self.property.setText(prop)
        self.time.setValue(key.time); self.value.setValue(key.value); self.easing.setText(key.easing)

    def add_track(self) -> None:
        target = self.target.text().strip() or "Alice"
        prop = self.property.text().strip() or "x"
        if not any(t.target == target and t.property == prop for t in self.timeline.tracks):
            self.timeline.tracks.append(__import__("vnengine.animation.timeline", fromlist=["Track"]).Track(target, prop))
            self._sync_preview_targets()
        self.rebuild()

    def add_key(self) -> None:
        try:
            self.timeline.add_keyframe(self.target.text().strip(), self.property.text().strip(), self.time.value(), self.value.value(), self.easing.text().strip() or "linear")
        except ValueError as exc:
            QMessageBox.warning(self, "Keyframe", str(exc)); return
        self._sync_preview_targets()
        self.rebuild()

    def remove_key(self) -> None:
        track_item = self.tracks.currentItem(); key_item = self.keys.currentItem()
        if track_item is None or key_item is None: return
        target, prop = track_item.data(Qt.UserRole); track = next((t for t in self.timeline.tracks if t.target == target and t.property == prop), None)
        if track is None: return
        del track.keys[int(key_item.data(Qt.UserRole))]
        self.timeline.duration = max((t.duration for t in self.timeline.tracks), default=0.0)
        self.rebuild()

    def seek(self, value: float) -> None:
        if self._building: return
        self.timeline.seek(value); self._update_preview(); self.rebuild()

    def slider_seek(self, value: int) -> None:
        if self._building: return
        self.timeline.seek(self.timeline.duration * value / 1000.0 if self.timeline.duration else 0.0)
        self.playhead.blockSignals(True); self.playhead.setValue(self.timeline.time); self.playhead.blockSignals(False)
        self._update_preview()

    def play(self) -> None:
        self.timeline.play(); self._playing_timer.start()

    def pause(self) -> None:
        self.timeline.pause(); self._playing_timer.stop()

    def stop(self) -> None:
        self.timeline.stop(); self._playing_timer.stop(); self.rebuild()

    def _tick_preview(self) -> None:
        self.timeline.update(0.016)
        self._update_preview()
        if not self.timeline.playing:
            self._playing_timer.stop()
        else:
            self.playhead.blockSignals(True); self.playhead.setValue(self.timeline.time); self.playhead.blockSignals(False)

    def save_file(self) -> None:
        self.timeline.name = self.name.text().strip() or "Main"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.timeline.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
