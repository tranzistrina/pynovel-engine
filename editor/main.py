from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTreeWidget,
    QTreeWidgetItem, QPlainTextEdit, QLabel, QPushButton, QMessageBox,
    QFileDialog, QSplitter, QStatusBar, QTabWidget
)

from editor.scene_editor import SceneEditor
from vnengine.script.parser import VNParser, VNParseError

ASSET_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".wav", ".ogg", ".mp3", ".mp4", ".json", ".vn"}


class Editor(QMainWindow):
    def __init__(self, project: str | Path):
        super().__init__()
        self.project = Path(project)
        self.current: Path | None = None
        self.setWindowTitle(f"PyNovel Editor 0.4 — {self.project.name}")
        self.resize(1480, 900)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        bar = QHBoxLayout()
        root.addLayout(bar)
        for label, slot in (("Save", self.save_file), ("Validate", self.validate), ("Run", self.run_game), ("Open folder", self.open_folder)):
            button = QPushButton(label)
            button.clicked.connect(slot)
            bar.addWidget(button)
        bar.addStretch()

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        body = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Project")
        self.tree.itemClicked.connect(self.select_item)
        body.addWidget(self.tree)
        self.editor = QPlainTextEdit()
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        body.addWidget(self.editor)
        self.preview = QLabel("Asset preview / scenario stats")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setWordWrap(True)
        body.addWidget(self.preview)
        body.setSizes([260, 760, 360])

        script_tab = QWidget()
        st = QVBoxLayout(script_tab)
        st.addWidget(body)
        self.tabs.addTab(script_tab, "Script")
        self.scene_tab = SceneEditor(self.project)
        self.tabs.addTab(self.scene_tab, "Scene")
        self.reload()

        file_menu = self.menuBar().addMenu("File")
        action = QAction("Save", self)
        action.triggered.connect(self.save_file)
        file_menu.addAction(action)
        action = QAction("Quit", self)
        action.triggered.connect(self.close)
        file_menu.addAction(action)

    def reload(self):
        self.tree.clear()
        self._add_path(self.tree.invisibleRootItem(), self.project)
        self.scene_tab.project = self.project
        self.scene_tab.scene_path = self.project / "scene.json"
        self.scene_tab.canvas.project = self.project
        self.scene_tab.load_file()
        self.status.showMessage("Project loaded")

    def _add_path(self, parent, path: Path):
        children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())) if path.exists() else []
        for p in children:
            if p.name.startswith(".") or (p.is_file() and p.suffix.lower() not in ASSET_EXTS):
                continue
            item = QTreeWidgetItem([p.name])
            item.setData(0, Qt.UserRole, str(p))
            parent.addChild(item)
            if p.is_dir():
                self._add_path(item, p)

    def select_item(self, item, _column):
        p = Path(item.data(0, Qt.UserRole))
        self.current = p
        if p.is_file() and p.suffix.lower() in {".vn", ".json"}:
            self.editor.setPlainText(p.read_text(encoding="utf-8"))
            self._stats()
            self.preview.setText("Text asset")
            self.tabs.setCurrentIndex(0)
        elif p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            self.editor.clear()
            pix = QPixmap(str(p))
            self.preview.setPixmap(pix.scaled(420, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.tabs.setCurrentIndex(0)
        else:
            self.editor.clear()
            self.preview.setText(str(p.relative_to(self.project)))
            self.tabs.setCurrentIndex(0)

    def _stats(self):
        try:
            story = VNParser().parse(self.editor.toPlainText(), title=self.project.name)
            self.preview.setText(f"Actions: {len(story.actions)}\nLabels: {len(story.labels)}\n\nScript valid")
        except Exception as exc:
            self.preview.setText(f"Parser error\n{exc}")

    def save_file(self):
        if not self.current or not self.current.is_file() or self.current.suffix.lower() not in {".vn", ".json"}:
            return
        self.current.write_text(self.editor.toPlainText(), encoding="utf-8")
        self._stats()
        self.status.showMessage(f"Saved {self.current.name}")

    def validate(self):
        try:
            story = VNParser().parse_file(self.project / "game.vn")
            QMessageBox.information(self, "Valid script", f"{len(story.actions)} actions\n{len(story.labels)} labels")
        except VNParseError as exc:
            QMessageBox.critical(self, "Invalid script", str(exc))

    def run_game(self):
        self.save_file()
        from vnengine.runtime import Game
        self.hide()
        try:
            Game(self.project).run()
        except Exception as exc:
            QMessageBox.critical(self, "Runtime error", str(exc))
        finally:
            self.show()

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Choose project", str(self.project.parent))
        if path:
            self.project = Path(path)
            self.current = None
            self.setWindowTitle(f"PyNovel Editor 0.4 — {self.project.name}")
            self.reload()


def main():
    project = sys.argv[1] if len(sys.argv) > 1 else "examples/demo"
    app = QApplication(sys.argv)
    win = Editor(project)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
