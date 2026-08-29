from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTextEdit, QLabel, QPushButton

class Editor(QMainWindow):
    def __init__(self, project: str | Path):
        super().__init__(); self.project = Path(project); self.setWindowTitle("PyNovel Editor")
        central=QWidget(); self.setCentralWidget(central); root=QHBoxLayout(central)
        self.files=QListWidget(); self.preview=QTextEdit(); self.preview.setReadOnly(True)
        self.inspector=QLabel("Project\n\nSelect game.vn to inspect the scenario.")
        root.addWidget(self.files, 1)
        mid=QVBoxLayout(); mid.addWidget(QLabel("Scenario")); mid.addWidget(self.preview, 4)
        root.addLayout(mid, 4)
        side=QVBoxLayout(); side.addWidget(self.inspector, 2); run=QPushButton("Run game"); run.clicked.connect(self.run_game); side.addWidget(run); root.addLayout(side, 1)
        self.reload()
    def reload(self):
        self.files.clear()
        for p in self.project.rglob("*"):
            if p.is_file() and (p.suffix in {".vn", ".json", ".png", ".jpg", ".jpeg", ".wav", ".ogg"}): self.files.addItem(str(p.relative_to(self.project)))
        self.files.currentTextChanged.connect(self.open_file)
    def open_file(self, rel):
        if not rel: return
        p=self.project/rel
        try: text=p.read_text(encoding="utf-8")
        except Exception: text=f"{rel}\n(binary asset)"
        self.preview.setPlainText(text)
    def run_game(self):
        from vnengine.runtime import Game
        self.hide(); Game(self.project).run(); self.show()

def main():
    project=sys.argv[1] if len(sys.argv)>1 else "examples/demo"
    app=QApplication(sys.argv); win=Editor(project); win.resize(1200,720); win.show(); sys.exit(app.exec())
if __name__ == "__main__": main()
