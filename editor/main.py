from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QLabel,QPushButton,QMessageBox,QFileDialog,QSplitter,QStatusBar,QTabWidget
from editor.scene_editor import SceneEditor
from editor.dialogue_editor import DialogueEditor
from editor.ui_editor import UIEditor
from editor.asset_browser import AssetBrowser
from editor.asset_drop_bridge import UIAssetDropBridge
from vnengine.script.parser import VNParser,VNParseError
ASSET_EXTS={'.png','.jpg','.jpeg','.webp','.wav','.ogg','.mp3','.mp4','.json','.vn'}
class Editor(QMainWindow):
    def __init__(self,project:str|Path):
        super().__init__(); self.project=Path(project); self.current=None; self.setWindowTitle(f'PyNovel Editor 0.23 — {self.project.name}'); self.resize(1600,920); self.status=QStatusBar(); self.setStatusBar(self.status)
        central=QWidget(); self.setCentralWidget(central); root=QVBoxLayout(central); bar=QHBoxLayout(); root.addLayout(bar)
        for label,slot in [('Save',self.save_file),('Validate',self.validate),('Run',self.run_game),('Open folder',self.open_folder)]: b=QPushButton(label); b.clicked.connect(slot); bar.addWidget(b)
        bar.addStretch(); self.tabs=QTabWidget(); root.addWidget(self.tabs,1)
        body=QSplitter(Qt.Horizontal); self.tree=QTreeWidget(); self.tree.setHeaderLabel('Project'); self.tree.itemClicked.connect(self.select_item); body.addWidget(self.tree)
        self.editor=QPlainTextEdit(); self.editor.setLineWrapMode(QPlainTextEdit.NoWrap); body.addWidget(self.editor); self.preview=QLabel('Asset preview / scenario stats'); self.preview.setAlignment(Qt.AlignCenter); self.preview.setWordWrap(True); body.addWidget(self.preview); body.setSizes([260,760,360])
        script_tab=QWidget(); QVBoxLayout(script_tab).addWidget(body); self.tabs.addTab(script_tab,'Script')
        self.scene_tab=SceneEditor(self.project); self.tabs.addTab(self.scene_tab,'Scene'); self.dialogue_tab=DialogueEditor(self.project); self.tabs.addTab(self.dialogue_tab,'Dialogue'); self.ui_tab=UIEditor(self.project); self.tabs.addTab(self.ui_tab,'UI'); self.ui_asset_drop=UIAssetDropBridge(self.ui_tab); self.asset_tab=AssetBrowser(self.project); self.tabs.addTab(self.asset_tab,'Assets'); self.reload()
        menu=self.menuBar().addMenu('File'); a=QAction('Save',self); a.triggered.connect(self.save_file); menu.addAction(a); a=QAction('Quit',self); a.triggered.connect(self.close); menu.addAction(a)
    def reload(self):
        self.tree.clear(); self._add_path(self.tree.invisibleRootItem(),self.project); self.scene_tab.project=self.project; self.scene_tab.scene_path=self.project/'scene.json'; self.scene_tab.canvas.project=self.project; self.scene_tab.load_file(); self.dialogue_tab.project=self.project; self.dialogue_tab.dialogue_path=self.project/'dialogue.json'; self.dialogue_tab.load_file(); self.ui_tab.project=self.project; self.ui_tab.path=self.project/'ui.json'; self.ui_tab.load_file(); self.asset_tab.project=self.project; self.asset_tab.catalog.project=self.project; self.asset_tab.scan(); self.setWindowTitle(f'PyNovel Editor 0.23 — {self.project.name}'); self.status.showMessage('Project loaded')
    def _add_path(self,parent,path):
        for p in sorted(path.iterdir(),key=lambda x:(x.is_file(),x.name.lower())) if path.exists() else []:
            if p.name.startswith('.') or (p.is_file() and p.suffix.lower() not in ASSET_EXTS):continue
            item=QTreeWidgetItem([p.name]); item.setData(0,Qt.UserRole,str(p)); parent.addChild(item)
            if p.is_dir():self._add_path(item,p)
    def select_item(self,item,_column):
        p=Path(item.data(0,Qt.UserRole)); self.current=p
        if p.is_file() and p.suffix.lower() in {'.vn','.json'}: self.editor.setPlainText(p.read_text(encoding='utf-8')); self._stats(); self.preview.setText('Text asset'); self.tabs.setCurrentIndex(0)
        elif p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}: self.editor.clear(); self.preview.setPixmap(QPixmap(str(p)).scaled(420,700,Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.tabs.setCurrentIndex(0)
        else:self.editor.clear(); self.preview.setText(str(p.relative_to(self.project))); self.tabs.setCurrentIndex(0)
    def _stats(self):
        try:s=VNParser().parse(self.editor.toPlainText(),title=self.project.name); self.preview.setText(f'Actions: {len(s.actions)}\nLabels: {len(s.labels)}\n\nScript valid')
        except Exception as exc:self.preview.setText(f'Parser error\n{exc}')
    def save_file(self):
        if self.tabs.currentWidget() is self.ui_tab:self.ui_tab.save_file(); self.status.showMessage('UI saved'); return
        if not self.current or not self.current.is_file() or self.current.suffix.lower() not in {'.vn','.json'}:return
        self.current.write_text(self.editor.toPlainText(),encoding='utf-8'); self._stats(); self.status.showMessage(f'Saved {self.current.name}')
    def validate(self):
        try:s=VNParser().parse_file(self.project/'game.vn'); QMessageBox.information(self,'Valid script',f'{len(s.actions)} actions\n{len(s.labels)} labels')
        except VNParseError as exc:QMessageBox.critical(self,'Invalid script',str(exc))
    def run_game(self):
        self.save_file(); from vnengine.runtime import Game; self.hide()
        try:Game(self.project).run()
        except Exception as exc:QMessageBox.critical(self,'Runtime error',str(exc))
        finally:self.show()
    def open_folder(self):
        path=QFileDialog.getExistingDirectory(self,'Choose project',str(self.project.parent))
        if path:self.project=Path(path); self.current=None; self.ui_asset_drop.deleteLater(); self.ui_asset_drop=UIAssetDropBridge(self.ui_tab); self.reload()
def main():
    project=sys.argv[1] if len(sys.argv)>1 else 'examples/demo'; app=QApplication(sys.argv); win=Editor(project); win.show(); sys.exit(app.exec())
if __name__=='__main__':main()
