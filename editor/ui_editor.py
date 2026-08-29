from __future__ import annotations
import copy, json
from pathlib import Path
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QTreeWidget,QTreeWidgetItem,QGraphicsView,QGraphicsScene,QGraphicsRectItem,QGraphicsTextItem,QFormLayout,QLineEdit,QComboBox,QSpinBox,QPushButton,QLabel,QSplitter

WIDGET_TYPES=["panel","label","image","textbox","button"]
ANCHORS=["top-left","center","top-center","top-right","bottom-left","bottom-center","bottom-right"]

class UIEditor(QWidget):
    def __init__(self, project: str|Path):
        super().__init__(); self.project=Path(project); self.path=self.project/'ui.json'; self.current=None; self.items={}; self.history=[]; self.future=[]; self._restoring=False
        self.data={"type":"panel","id":"root","x":0,"y":0,"width":"100%","height":"100%","children":[]}
        root=QHBoxLayout(self); split=QSplitter(Qt.Horizontal); root.addWidget(split)
        left=QWidget(); ll=QVBoxLayout(left); ll.addWidget(QLabel('Widgets')); self.tree=QTreeWidget(); self.tree.setHeaderLabels(['ID','Type']); self.tree.itemClicked.connect(self.select_tree); ll.addWidget(self.tree)
        addrow=QHBoxLayout(); add=QComboBox(); add.addItems(WIDGET_TYPES); addrow.addWidget(add); btn=QPushButton('Add'); btn.clicked.connect(lambda:self.add_widget(add.currentText())); addrow.addWidget(btn); ll.addLayout(addrow); split.addWidget(left)
        self.scene=QGraphicsScene(0,0,1280,720); self.scene.setBackgroundBrush(QBrush(QColor(35,38,48))); self.view=QGraphicsView(self.scene); self.view.setSceneRect(0,0,1280,720); split.addWidget(self.view)
        right=QWidget(); rl=QVBoxLayout(right); rl.addWidget(QLabel('Inspector')); form=QFormLayout(); self.id_edit=QLineEdit(); self.type_box=QComboBox(); self.type_box.addItems(WIDGET_TYPES); self.x=QSpinBox(); self.x.setRange(-5000,5000); self.y=QSpinBox(); self.y.setRange(-5000,5000); self.w=QSpinBox(); self.w.setRange(1,5000); self.h=QSpinBox(); self.h.setRange(1,5000); self.text=QLineEdit(); self.anchor=QComboBox(); self.anchor.addItems(ANCHORS); self.z=QSpinBox(); self.z.setRange(-9999,9999)
        for lab,widget in [('ID',self.id_edit),('Type',self.type_box),('X',self.x),('Y',self.y),('Width',self.w),('Height',self.h),('Text',self.text),('Anchor',self.anchor),('Z',self.z)]: form.addRow(lab,widget)
        rl.addLayout(form); apply=QPushButton('Apply'); apply.clicked.connect(self.apply_inspector); rl.addWidget(apply)
        actions=QHBoxLayout(); undo=QPushButton('Undo'); undo.clicked.connect(self.undo); redo=QPushButton('Redo'); redo.clicked.connect(self.redo); dup=QPushButton('Duplicate'); dup.clicked.connect(self.duplicate_current); delete=QPushButton('Delete'); delete.clicked.connect(self.delete_current); [actions.addWidget(b) for b in (undo,redo,dup,delete)]; rl.addLayout(actions)
        save=QPushButton('Save UI'); save.clicked.connect(self.save_file); rl.addWidget(save); rl.addStretch(); split.addWidget(right); split.setSizes([260,780,320]); self.load_file()
    def _snapshot(self): return copy.deepcopy(self.data)
    def _record(self):
        if self._restoring:return
        self.history.append(self._snapshot()); self.future.clear(); self.history=self.history[-100:]
    def load_file(self):
        if self.path.exists():
            try:self.data=json.loads(self.path.read_text(encoding='utf-8'))
            except (OSError,ValueError):pass
        self.history.clear(); self.future.clear(); self.rebuild()
    def rebuild(self):
        self.tree.clear(); self.scene.clear(); self.items={}; self.current=None; self.populate_tree(self.tree.invisibleRootItem(),self.data); self.draw_widget(self.data)
    def populate_tree(self,parent,data):
        item=QTreeWidgetItem([str(data.get('id','widget')),str(data.get('type','panel'))]); item.setData(0,Qt.UserRole,data); parent.addChild(item)
        for child in data.get('children',[]):self.populate_tree(item,child)
    def resolve(self,value,total):
        if isinstance(value,str) and value.endswith('%'):
            try:return int(total*float(value[:-1])/100)
            except ValueError:return 0
        try:return int(value or 0)
        except (TypeError,ValueError):return 0
    def geom(self,data,parent_offset=(0,0)):
        x=self.resolve(data.get('x',0),1280)+parent_offset[0]; y=self.resolve(data.get('y',0),720)+parent_offset[1]; w=self.resolve(data.get('width',120),1280); h=self.resolve(data.get('height',40),720); a=data.get('anchor','top-left')
        if a=='center':x-=w//2;y-=h//2
        elif a=='top-center':x-=w//2
        elif a=='top-right':x=1280-x-w
        elif a=='bottom-left':y=720-y-h
        elif a=='bottom-center':x-=w//2;y=720-y-h
        elif a=='bottom-right':x=1280-x-w;y=720-y-h
        return x,y,max(1,w),max(1,h)
    def draw_widget(self,data,parent_offset=(0,0)):
        x,y,w,h=self.geom(data,parent_offset); item=QGraphicsRectItem(QRectF(x,y,w,h)); item.setZValue(data.get('z',0)); item.setPen(QPen(QColor(120,150,220),2)); item.setBrush(QBrush(QColor(70,75,92,70))); item.setData(0,data); self.scene.addItem(item); self.items[id(data)]=item
        label=QGraphicsTextItem(f"{data.get('id','widget')} [{data.get('type','panel')}]"); label.setDefaultTextColor(QColor(240,240,245)); label.setFont(QFont('Sans',10)); label.setPos(x+4,y+4); label.setZValue(item.zValue()+0.1); self.scene.addItem(label)
        for child in data.get('children',[]):self.draw_widget(child,(x,y))
    def select_tree(self,item,_):self.current=item.data(0,Qt.UserRole);self.load_inspector(self.current)
    def load_inspector(self,d):
        self.id_edit.setText(str(d.get('id',''))); self.type_box.setCurrentText(str(d.get('type','panel'))); self.x.setValue(self.resolve(d.get('x',0),1280)); self.y.setValue(self.resolve(d.get('y',0),720)); self.w.setValue(self.resolve(d.get('width',120),1280)); self.h.setValue(self.resolve(d.get('height',40),720)); self.text.setText(str(d.get('text',''))); self.anchor.setCurrentText(str(d.get('anchor','top-left'))); self.z.setValue(int(d.get('z',0)))
    def apply_inspector(self):
        if self.current is None:return
        self._record(); self.current.update({'id':self.id_edit.text().strip() or 'widget','type':self.type_box.currentText(),'x':self.x.value(),'y':self.y.value(),'width':self.w.value(),'height':self.h.value(),'anchor':self.anchor.currentText(),'z':self.z.value(),'text':self.text.text()}); self.rebuild()
    def add_widget(self,typ):
        self._record(); node={'type':typ,'id':f'{typ}_{len(self.data.get("children",[]))+1}','x':120,'y':120,'width':240,'height':56,'text':typ.title(),'children':[]}; self.data.setdefault('children',[]).append(node); self.rebuild()
    def find_parent(self,target,data=None):
        data=data or self.data
        for child in data.get('children',[]):
            if child is target:return data
            found=self.find_parent(target,child)
            if found:return found
        return None
    def delete_current(self):
        if self.current is None or self.current is self.data:return
        parent=self.find_parent(self.current)
        if parent:
            self._record(); parent['children'].remove(self.current); self.rebuild()
    def duplicate_current(self):
        if self.current is None:return
        parent=self.find_parent(self.current) or self.data; self._record(); clone=copy.deepcopy(self.current); clone['id']=str(clone.get('id','widget'))+'_copy'; clone['x']=self.resolve(clone.get('x',0),1280)+20; clone['y']=self.resolve(clone.get('y',0),720)+20; parent.setdefault('children',[]).append(clone); self.rebuild()
    def undo(self):
        if not self.history:return
        self.future.append(self._snapshot()); self._restoring=True
        try:self.data=self.history.pop(); self.rebuild()
        finally:self._restoring=False
    def redo(self):
        if not self.future:return
        self.history.append(self._snapshot()); self._restoring=True
        try:self.data=self.future.pop(); self.rebuild()
        finally:self._restoring=False
    def save_file(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding='utf-8')
