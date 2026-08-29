from __future__ import annotations

from pathlib import Path
from vnengine.assets.catalog import AssetCatalog, AssetType
from vnengine.assets.dragdrop import MIME_TYPE, encode_asset_path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QDrag
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QPlainTextEdit
)


class AssetList(QListWidget):
    """Asset list that advertises project-relative paths for drag-and-drop targets."""

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item is None:
            return
        payload = encode_asset_path(str(item.data(Qt.UserRole)))
        mime = self.mimeData([item])
        mime.setData(MIME_TYPE, payload.encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)


class AssetBrowser(QWidget):
    """Project asset browser with filtering, preview, path copy and drag support."""

    def __init__(self, project: str | Path):
        super().__init__()
        self.project = Path(project)
        self.catalog = AssetCatalog(self.project)
        self.entries = []
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search assets...")
        self.search.textChanged.connect(self.refresh_list)
        toolbar.addWidget(self.search)
        self.type_filter = QComboBox()
        self.type_filter.addItem("All", None)
        for asset_type in AssetType:
            self.type_filter.addItem(asset_type.value.title(), asset_type)
        self.type_filter.currentIndexChanged.connect(self.refresh_list)
        toolbar.addWidget(self.type_filter)
        scan = QPushButton("Scan")
        scan.clicked.connect(self.scan)
        toolbar.addWidget(scan)
        left.addLayout(toolbar)
        self.list = AssetList()
        self.list.setDragEnabled(True)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.itemSelectionChanged.connect(self.preview_selected)
        left.addWidget(self.list, 1)
        root.addLayout(left, 2)
        right = QVBoxLayout()
        self.preview = QLabel("Select an asset")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(320, 240)
        self.preview.setWordWrap(True)
        right.addWidget(self.preview, 1)
        self.meta = QPlainTextEdit()
        self.meta.setReadOnly(True)
        self.meta.setMaximumHeight(130)
        right.addWidget(self.meta)
        copy_btn = QPushButton("Copy path")
        copy_btn.clicked.connect(self.copy_selected_path)
        right.addWidget(copy_btn)
        right.addWidget(QLabel("Drag an asset onto Scene or UI canvas."))
        root.addLayout(right, 1)
        self.scan()

    def scan(self) -> None:
        self.entries = self.catalog.scan()
        self.catalog.write_index()
        self.refresh_list()

    def refresh_list(self) -> None:
        query = self.search.text().strip().lower()
        selected_type = self.type_filter.currentData()
        self.list.clear()
        for entry in self.entries:
            if query and query not in entry.path.lower():
                continue
            if selected_type is not None and entry.asset_type != selected_type:
                continue
            item = QListWidgetItem(f"{entry.path}  [{entry.asset_type.value}]")
            item.setData(Qt.UserRole, entry.path)
            self.list.addItem(item)
        self.preview.setText("Select an asset")
        self.meta.clear()

    def preview_selected(self) -> None:
        items = self.list.selectedItems()
        if not items:
            return
        path = items[0].data(Qt.UserRole)
        entry = self.catalog.find(path)
        if entry is None:
            return
        absolute = self.project / entry.path
        self.meta.setPlainText(f"Path: {entry.path}\nType: {entry.asset_type.value}\nSize: {entry.size} bytes")
        if entry.asset_type == AssetType.IMAGE:
            pixmap = QPixmap(str(absolute))
            if not pixmap.isNull():
                self.preview.setPixmap(pixmap.scaled(520, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        if entry.asset_type in {AssetType.SCRIPT, AssetType.DATA}:
            try:
                text = absolute.read_text(encoding="utf-8")
                self.preview.setText(text[:5000])
                return
            except (OSError, UnicodeDecodeError):
                pass
        self.preview.setText(f"{entry.asset_type.value.title()}\n\n{entry.path}")

    def copy_selected_path(self) -> None:
        items = self.list.selectedItems()
        if not items:
            return
        QApplication.clipboard().setText(str(items[0].data(Qt.UserRole)))
