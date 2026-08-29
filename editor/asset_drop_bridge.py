from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QEvent, Qt

from vnengine.assets.dragdrop import MIME_TYPE, decode_asset_path


class UIAssetDropBridge(QObject):
    """Accept Asset Browser drags on an existing UIEditor canvas."""

    IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

    def __init__(self, ui_editor):
        super().__init__(ui_editor)
        self.ui_editor = ui_editor
        self.viewport = ui_editor.view.viewport()
        self.viewport.setAcceptDrops(True)
        self.viewport.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is not self.viewport:
            return super().eventFilter(watched, event)
        if event.type() == QEvent.DragEnter:
            if event.mimeData().hasFormat(MIME_TYPE):
                event.acceptProposedAction()
                return True
        if event.type() == QEvent.Drop and event.mimeData().hasFormat(MIME_TYPE):
            payload = bytes(event.mimeData().data(MIME_TYPE)).decode("utf-8")
            path = decode_asset_path(payload)
            if path and Path(path).suffix.lower() in self.IMAGE_SUFFIXES:
                point = self.ui_editor.view.mapToScene(event.position().toPoint())
                self._add_image(path, point.x(), point.y())
                event.acceptProposedAction()
                return True
        return super().eventFilter(watched, event)

    def _add_image(self, path: str, scene_x: float, scene_y: float) -> None:
        editor = self.ui_editor
        editor._record()
        existing = {node.get("id") for node in editor.iter_nodes(editor.data)}
        stem = Path(path).stem or "image"
        candidate = stem
        index = 2
        while candidate in existing:
            candidate = f"{stem}_{index}"
            index += 1
        node = {
            "type": "image",
            "id": candidate,
            "x": int(scene_x),
            "y": int(scene_y),
            "width": 240,
            "height": 160,
            "anchor": "center",
            "z": 0,
            "image": path.replace("\\", "/"),
            "text": "",
            "children": [],
        }
        editor.data.setdefault("children", []).append(node)
        editor.selection = [node]
        editor.current = node
        editor.rebuild(preserve_current=True)
