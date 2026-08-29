from __future__ import annotations

import json
import re
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView,
    QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QListWidget, QListWidgetItem, QSplitter, QLineEdit, QLabel, QMessageBox,
    QComboBox, QFormLayout, QGroupBox
)
from vnengine.script.dialogue_graph import DialogueGraph, DialogueNode

class DialogueCanvas(QGraphicsView):
    def __init__(self, editor):
        super().__init__(); self.editor = editor; self.graph_scene = QGraphicsScene(self); self.setScene(self.graph_scene)
        self.setDragMode(QGraphicsView.RubberBandDrag); self.setSceneRect(0, 0, 1800, 1100); self.items_by_id = {}
        self.graph_scene.selectionChanged.connect(self._selection_changed)
    def _selection_changed(self):
        selected = self.graph_scene.selectedItems(); self.editor.select_node(str(selected[0].data(0)) if selected else None)
    def render_graph(self):
        self.graph_scene.clear(); self.items_by_id.clear(); nodes = self.editor.graph.by_id()
        for node in self.editor.graph.nodes:
            w, h = ((270, 155) if node.kind == 'choice' else (240, 115))
            item = QGraphicsRectItem(0, 0, w, h); item.setPos(node.x, node.y); item.setBrush(QBrush(QColor('#202638'))); item.setPen(QPen(QColor('#8fa7d8'), 2))
            item.setFlag(QGraphicsRectItem.ItemIsMovable, True); item.setFlag(QGraphicsRectItem.ItemIsSelectable, True); item.setData(0, node.id)
            text = QGraphicsTextItem(self._label(node), item); text.setDefaultTextColor(QColor('#f3f5fb')); text.setPos(12, 10); text.setTextWidth(w - 24)
            self.graph_scene.addItem(item); self.items_by_id[node.id] = item
        for node in self.editor.graph.nodes:
            source = self.items_by_id.get(node.id)
            if not source: continue
            targets = ([node.target] if node.target else []) + ([o.get('target', '') for o in node.options] if node.kind == 'choice' else [])
            for target_id in targets:
                target = self.items_by_id.get(target_id)
                if not target: continue
                p1, p2 = source.sceneBoundingRect().center(), target.sceneBoundingRect().center(); line = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
                line.setPen(QPen(QColor('#596b92'), 2)); line.setZValue(-10); self.graph_scene.addItem(line)
        if self.graph_scene.items(): self.fitInView(self.graph_scene.itemsBoundingRect().adjusted(-60, -60, 60, 60), Qt.KeepAspectRatio)
    @staticmethod
    def _label(node):
        if node.kind == 'say': return f'SAY\n{node.speaker}:\n{node.text[:90]}'
        if node.kind == 'choice': return 'CHOICE\n' + '\n'.join(f"• {o.get('text','')} → {o.get('target','')}" for o in node.options[:5])
        if node.kind == 'jump': return f'JUMP\n→ {node.target}'
        if node.kind == 'condition': return f'IF\n{node.text}\n→ {node.target}'
        return 'END'
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event); changed = False
        for node_id, item in self.items_by_id.items():
            node = self.editor.graph.by_id().get(node_id)
            if node and (node.x, node.y) != (item.x(), item.y()): node.x, node.y = round(item.x(), 1), round(item.y(), 1); changed = True
        if changed: self.editor.dirty = True; self.render_graph()

class DialogueEditor(QWidget):
    def __init__(self, project: str | Path):
        super().__init__(); self.project = Path(project); self.dialogue_path = self.project / 'dialogue.json'; self.graph = DialogueGraph(); self.selected_id = None; self.dirty = False; self._build_ui(); self.load_file()
    def _build_ui(self):
        root = QVBoxLayout(self); toolbar = QHBoxLayout(); root.addLayout(toolbar)
        for label, kind in (('+ Say','say'),('+ Choice','choice'),('+ Jump','jump'),('+ If','condition'),('+ End','end')):
            b = QPushButton(label); b.clicked.connect(lambda _=False, k=kind: self.add_node(k)); toolbar.addWidget(b)
        b = QPushButton('Save graph'); b.clicked.connect(self.save_file); toolbar.addWidget(b)
        b = QPushButton('Compile to game.vn'); b.clicked.connect(self.compile_to_vn); toolbar.addWidget(b); toolbar.addStretch()
        body = QSplitter(Qt.Horizontal); self.canvas = DialogueCanvas(self); body.addWidget(self.canvas)
        side = QWidget(); layout = QVBoxLayout(side); formbox = QGroupBox('Node inspector'); form = QFormLayout(formbox)
        self.kind = QComboBox(); self.kind.addItems(['say','choice','jump','condition','end']); self.node_id = QLineEdit(); self.speaker = QLineEdit(); self.text = QLineEdit(); self.target = QLineEdit()
        for label, w in (('Kind',self.kind),('ID',self.node_id),('Speaker',self.speaker),('Text / expression',self.text),('Target',self.target)): form.addRow(label,w)
        layout.addWidget(formbox); self.node_list = QListWidget(); self.node_list.currentRowChanged.connect(self._row_selected); layout.addWidget(self.node_list,1); self.status = QLabel('Select a node'); self.status.setWordWrap(True); layout.addWidget(self.status); body.addWidget(side); body.setSizes([1050,360]); root.addWidget(body,1)
        self.node_id.textChanged.connect(self.apply_fields); self.speaker.textChanged.connect(self.apply_fields); self.text.textChanged.connect(self.apply_fields); self.target.textChanged.connect(self.apply_fields); self.kind.currentTextChanged.connect(self.apply_fields)
    def load_file(self):
        if self.dialogue_path.exists(): self.graph = DialogueGraph.from_dict(json.loads(self.dialogue_path.read_text(encoding='utf-8')))
        self.refresh(); self.dirty = False
    def refresh(self):
        self.node_list.blockSignals(True); self.node_list.clear()
        for n in self.graph.nodes: self.node_list.addItem(QListWidgetItem(f'{n.id} [{n.kind}]'))
        self.node_list.blockSignals(False); self.canvas.render_graph()
    def _row_selected(self,row): self.select_node(self.graph.nodes[row].id if 0 <= row < len(self.graph.nodes) else None)
    def select_node(self,node_id):
        self.selected_id=node_id; node=self.graph.by_id().get(node_id) if node_id else None
        for w in (self.kind,self.node_id,self.speaker,self.text,self.target): w.blockSignals(True)
        if node:
            self.kind.setCurrentText(node.kind); self.node_id.setText(node.id); self.speaker.setText(node.speaker); self.text.setText(node.text); self.target.setText(node.target); self.status.setText(f'Node {node.id}\n{node.kind}')
        else: self.status.setText('Select a node')
        for w in (self.kind,self.node_id,self.speaker,self.text,self.target): w.blockSignals(False)
    def apply_fields(self):
        node=self.graph.by_id().get(self.selected_id) if self.selected_id else None
        if not node:return
        candidate=re.sub(r'[^A-Za-z0-9_-]','_',self.node_id.text().strip()) or node.id; ids=set(self.graph.by_id())
        if candidate != node.id and candidate in ids:return
        node.id=candidate; node.kind=self.kind.currentText(); node.speaker=self.speaker.text(); node.text=self.text.text(); node.target=self.target.text(); self.dirty=True; self.refresh()
    def add_node(self,kind):
        prefixes={'say':'say','choice':'choice','jump':'jump','condition':'if','end':'end'}; base=prefixes[kind]; i=1; ids=set(self.graph.by_id())
        while f'{base}_{i}' in ids:i+=1
        node=DialogueNode(id=f'{base}_{i}',kind=kind,speaker='Narrator' if kind=='say' else '',text='New dialogue' if kind=='say' else ('visited == True' if kind=='condition' else ''),x=80+(len(self.graph.nodes)%4)*300,y=80+(len(self.graph.nodes)//4)*190)
        self.graph.nodes.append(node); self.selected_id=node.id; self.dirty=True; self.refresh(); self.select_node(node.id)
    def save_file(self):
        self.dialogue_path.write_text(json.dumps(self.graph.to_dict(),ensure_ascii=False,indent=2),encoding='utf-8'); self.dirty=False; self.status.setText(f'Saved {self.dialogue_path.name}')
    def compile_to_vn(self):
        try:
            (self.project/'game.vn').write_text(self.graph.compile(),encoding='utf-8'); self.save_file(); QMessageBox.information(self,'Compiled','Dialogue graph compiled to game.vn')
        except ValueError as exc: QMessageBox.critical(self,'Cannot compile',str(exc))
