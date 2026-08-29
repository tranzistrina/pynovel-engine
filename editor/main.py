from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QListWidget,QTextEdit,QLabel,QPushButton,QMessageBox
from vnengine.script.parser import VNParser, VNParseError

class Editor(QMainWindow):
    def __init__(self,project:str|Path):
        super().__init__(); self.project=Path(project); self.setWindowTitle('PyNovel Editor 0.2'); self.resize(1280,760)
        central=QWidget(); self.setCentralWidget(central); root=QHBoxLayout(central)
        self.files=QListWidget(); self.preview=QTextEdit(); self.preview.setReadOnly(True); self.stats=QLabel()
        root.addWidget(self.files,1); mid=QVBoxLayout(); mid.addWidget(QLabel('Scenario / Asset Preview')); mid.addWidget(self.preview,1); root.addLayout(mid,4)
        side=QVBoxLayout(); side.addWidget(self.stats); run=QPushButton('Run game'); run.clicked.connect(self.run_game); side.addWidget(run); validate=QPushButton('Validate script'); validate.clicked.connect(self.validate); side.addWidget(validate); side.addStretch(); root.addLayout(side,1)
        self.files.currentTextChanged.connect(self.open_file); self.reload()
    def reload(self):
        self.files.clear()
        for p in sorted(self.project.rglob('*')):
            if p.is_file() and p.suffix.lower() in {'.vn','.json','.png','.jpg','.jpeg','.wav','.ogg','.mp3','.mp4'}:self.files.addItem(str(p.relative_to(self.project)))
        try:
            story=VNParser().parse_file(self.project/'game.vn'); self.stats.setText(f'Actions: {len(story.actions)}\nLabels: {len(story.labels)}')
        except Exception as exc:self.stats.setText(f'Parser error:\n{exc}')
    def open_file(self,rel):
        if not rel:return
        try:self.preview.setPlainText((self.project/rel).read_text(encoding='utf-8'))
        except Exception:self.preview.setPlainText(f'{rel}\n\n(binary asset)')
    def validate(self):
        try:s=VNParser().parse_file(self.project/'game.vn'); QMessageBox.information(self,'Valid',f'Valid script. {len(s.actions)} actions, {len(s.labels)} labels.')
        except VNParseError as exc:QMessageBox.critical(self,'Invalid script',str(exc))
    def run_game(self):
        from vnengine.runtime import Game
        self.hide()
        try:Game(self.project).run()
        finally:self.show()

def main():
    project=sys.argv[1] if len(sys.argv)>1 else 'examples/demo'; app=QApplication(sys.argv); win=Editor(project); win.show(); sys.exit(app.exec())
if __name__=='__main__':main()
