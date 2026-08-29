from __future__ import annotations
import copy, json
from pathlib import Path
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QTreeWidget,QTreeWidgetItem,QGraphicsView,QGraphicsScene,QGraphicsRectItem,QGraphicsTextItem,QFormLayout,QLineEdit,QComboBox,QSpinBox,QPushButton,QLabel,QSplitter,QInputDialog
from vnengine.ui.hierarchy import find_by_id, find_parent, iter_nodes, reparent, translate_nodes, set_z

WIDGET_TYPES=["panel","label","image","textbox","button"]
ANCHORS=["top-left","center","top-center","top-right","bottom-left","bottom-center","bottom-right"]
HANDLE=10

class UIEditor(QWidget):
    def __init__(self, project: str|Path):
        super().__init__(); self.setFocusPolicy(Qt.StrongFocus)
        self.project=Path(project); self.path=self.project/'ui.json'; self.current=None; self.selection=[]; self.items={}; self.labels={}; self.history=[]; self.future=[]; self._restoring=False
        self._drag_start=None; self._drag_origin=None; self._resize_origin=None; self._mode=None
        self.data={"type":"panel","id":"root","x":0,"y":0,"width":"100%","height":"100%","children":[]}
        root=QHBoxLayout(self); split=QSplitter(Qt.Horizontal); root.addWidget(split)
        left=QWidget(); ll=QVBoxLayout(left); ll.addWidget(QLabel('Widgets')); self.tree=QTreeWidget(); self.tree.setHeaderLabels(['ID','Type']); self.tree.setSelectionMode(QTreeWidget.ExtendedSelection); self.tree.itemSelectionChanged.connect(self.select_tree_multi); ll.addWidget(self.tree)
        addrow=QHBoxLayout(); add=QComboBox(); add.addItems(WIDGET_TYPES); addrow.addWidget(add); btn=QPushButton('Add'); btn.clicked.connect(lambda:self.add_widget(add.currentText())); addrow.addWidget(btn); ll.addLayout(addrow); reparent_btn=QPushButton('Reparent to Panel'); reparent_btn.clicked.connect(self.reparent_selected); ll.addWidget(reparent_btn); split.addWidget(left)
        self.scene=QGraphicsScene(0,0,1280,720); self.scene.setBackgroundBrush(QBrush(QColor(35,38,48))); self.view=QGraphicsView(self.scene); self.view.setSceneRect(0,0,1280,720); self.view.setMouseTracking(True); self.view.viewport().installEventFilter(self); split.addWidget(self.view)
        right=QWidget(); rl=QVBoxLayout(right); rl.addWidget(QLabel('Inspector')); form=QFormLayout(); self.id_edit=QLineEdit(); self.type_box=QComboBox(); self.type_box.addItems(WIDGET_TYPES); self.x=QSpinBox(); self.x.setRange(-5000,5000); self.y=QSpinBox(); self.y.setRange(-5000,5000); self.w=QSpinBox(); self.w.setRange(1,5000); self.h=QSpinBox(); self.h.setRange(1,5000); self.text=QLineEdit(); self.anchor=QComboBox(); self.anchor.addItems(ANCHORS); self.z=QSpinBox(); self.z.setRange(-9999,9999)
        for lab,widget in [('ID',self.id_edit),('Type',self.type_box),('X',self.x),('Y',self.y),('Width',self.w),('Height',self.h),('Text',self.text),('Anchor',self.anchor),('Z',self.z)]:form.addRow(lab,widget)
        rl.addLayout(form); apply=QPushButton('Apply'); apply.clicked.connect(self.apply_inspector); rl.addWidget(apply)
        actions=QHBoxLayout()
        for name,fn in [('Undo',self.undo),('Redo',self.redo),('Duplicate',self.duplicate_current),('Delete',self.delete_current)]: b=QPushButton(name); b.clicked.connect(fn); actions.addWidget(b)
        rl.addLayout(actions)
        align=QHBoxLayout()
        for name,fn in [('Center X',self.align_center_x),('Center Y',self.align_center_y),('Center',self.align_center),('Top',self.align_top),('Left',self.align_left),('Set Z',self.set_selected_z)]: b=QPushButton(name); b.clicked.connect(fn); align.addWidget(b)
        rl.addLayout(align); save=QPushButton('Save UI'); save.clicked.connect(self.save_file); rl.addWidget(save); rl.addStretch(); split.addWidget(right); split.setSizes([270,780,330]); self.load_file()

    def _selected_nodes(self): return [n for n in self.selection if isinstance(n,dict) and n is not self.data]
    def _set_selection(self,nodes): self.selection=list(dict.fromkeys(nodes)); self.current=self.selection[0] if self.selection else None; self.load_inspector(self.current); self.rebuild(preserve_current=True)
    def eventFilter(self,watched,event):
        if watched is self.view.viewport() and event.type()==event.MouseButtonPress:
            pos=self.view.mapToScene(event.pos()); item=self.scene.itemAt(pos,self.view.transform())
            if item is not None:
                data=item.data(0)
                if isinstance(data,dict):
                    ctrl=bool(event.modifiers() & Qt.ControlModifier)
                    if ctrl and data in self.selection:self.selection=[n for n in self.selection if n is not data]
                    elif ctrl:self.selection.append(data)
                    else:self.selection=[data]
                    self.current=data; self.load_inspector(data); self._record(); x,y,w,h=self.geom(data); self._drag_start=pos; self._drag_origin=(x,y); self._mode='drag'
                    if data is not self.data and abs(pos.x()-(x+w))<=HANDLE and abs(pos.y()-(y+h))<=HANDLE and len(self.selection)==1:self._mode='resize'; self._resize_origin=(w,h)
                    self.rebuild(preserve_current=True); return True
            elif not (event.modifiers() & Qt.ControlModifier): self.selection=[]; self.current=None; self.rebuild()
        elif watched is self.view.viewport() and event.type()==event.MouseMove and self.selection and self._drag_start is not None:
            pos=self.view.mapToScene(event.pos()); delta=pos-self._drag_start
            if self._mode=='resize' and self.current is not None:
                self.current['width']=max(8,int(self._resize_origin[0]+delta.x())); self.current['height']=max(8,int(self._resize_origin[1]+delta.y()))
            else: translate_nodes(self.selection,int(delta.x()),int(delta.y()))
            self.rebuild(preserve_current=True); return True
        elif watched is self.view.viewport() and event.type()==event.MouseButtonRelease:self._drag_start=None; self._drag_origin=None; self._resize_origin=None; self._mode=None; return False
        return super().eventFilter(watched,event)
    def _snapshot(self):return copy.deepcopy(self.data)
    def _record(self):
        if not self._restoring:self.history.append(self._snapshot()); self.future.clear(); self.history=self.history[-100:]
    def load_file(self):
        if self.path.exists():
            try:self.data=json.loads(self.path.read_text(encoding='utf-8'))
            except (OSError,ValueError):pass
        self.history.clear(); self.future.clear(); self.selection=[]; self.current=None; self.rebuild()
    def rebuild(self,preserve_current=False):
        selected_ids=[n.get('id') for n in self.selection] if preserve_current else []
        self.tree.clear(); self.scene.clear(); self.items={}; self.labels={}; self.populate_tree(self.tree.invisibleRootItem(),self.data); self.draw_widget(self.data)
        if selected_ids:
            self.selection=[n for n in (find_by_id(self.data,i) for i in selected_ids) if n]; self.current=self.selection[0] if self.selection else None
            if self.current:self.load_inspector(self.current)
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
        x,y,w,h=self.geom(data,parent_offset); selected=data in self.selection; pen=QPen(QColor(255,210,90) if selected else QColor(120,150,220),3 if selected else 2); item=QGraphicsRectItem(QRectF(x,y,w,h)); item.setZValue(data.get('z',0)); item.setPen(pen); item.setBrush(QBrush(QColor(90,95,115,70))); item.setData(0,data); self.scene.addItem(item); self.items[id(data)]=item
        label=QGraphicsTextItem(f"{data.get('id','widget')} [{data.get('type','panel')}]" ); label.setDefaultTextColor(QColor(240,240,245)); label.setFont(QFont('Sans',10)); label.setPos(x+4,y+4); label.setZValue(item.zValue()+0.1); self.scene.addItem(label); self.labels[id(data)]=label
        if selected and data is not self.data and len(self.selection)==1:
            handle=QGraphicsRectItem(QRectF(x+w-HANDLE/2,y+h-HANDLE/2,HANDLE,HANDLE)); handle.setPen(QPen(QColor(255,210,90),1)); handle.setBrush(QBrush(QColor(255,210,90))); handle.setData(0,data); handle.setZValue(item.zValue()+2); self.scene.addItem(handle)
        for child in data.get('children',[]):self.draw_widget(child,(x,y))
    def select_tree_multi(self):
        self.selection=[item.data(0,Qt.UserRole) for item in self.tree.selectedItems() if isinstance(item.data(0,Qt.UserRole),dict)]; self.current=self.selection[0] if self.selection else None; self.load_inspector(self.current); self.rebuild(preserve_current=True)
    def load_inspector(self,d):
        if not d:return
        self.id_edit.setText(str(d.get('id','')));self.type_box.setCurrentText(str(d.get('type','panel')));self.x.setValue(self.resolve(d.get('x',0),1280));self.y.setValue(self.resolve(d.get('y',0),720));self.w.setValue(self.resolve(d.get('width',120),1280));self.h.setValue(self.resolve(d.get('height',40),720));self.text.setText(str(d.get('text','')));self.anchor.setCurrentText(str(d.get('anchor','top-left')));self.z.setValue(int(d.get('z',0)))
    def apply_inspector(self):
        if self.current is None:return
        self._record();self.current.update({'id':self.id_edit.text().strip() or 'widget','type':self.type_box.currentText(),'x':self.x.value(),'y':self.y.value(),'width':self.w.value(),'height':self.h.value(),'anchor':self.anchor.currentText(),'z':self.z.value(),'text':self.text.text()});self.selection=[self.current];self.rebuild(preserve_current=True)
    def add_widget(self,typ):
        self._record();node={'type':typ,'id':f'{typ}_{len(self.data.get("children",[]))+1}','x':120,'y':120,'width':240,'height':56,'text':typ.title(),'children':[]};self.data.setdefault('children',[]).append(node);self.selection=[node];self.current=node;self.rebuild(preserve_current=True)
    def delete_current(self):
        nodes=self._selected_nodes()
        if not nodes:return
        self._record()
        for node in nodes:
            parent=find_parent(self.data,node.get('id'))
            if parent:parent.get('children',[]).remove(node)
        self.selection=[];self.current=None;self.rebuild()
    def duplicate_current(self):
        nodes=self._selected_nodes()
        if not nodes:return
        self._record();existing={n.get('id') for n in iter_nodes(self.data)};new=[]
        for node in nodes:
            parent=find_parent(self.data,node.get('id')) or self.data;clone=copy.deepcopy(node);base=str(clone.get('id','widget'));candidate=base+'_copy';i=1
            while candidate in existing:i+=1;candidate=f'{base}_copy{i}'
            existing.add(candidate);clone['id']=candidate;clone['x']=self.resolve(clone.get('x',0),1280)+20;clone['y']=self.resolve(clone.get('y',0),720)+20;parent.setdefault('children',[]).append(clone);new.append(clone)
        self.selection=new;self.current=new[0] if new else None;self.rebuild(preserve_current=True)
    def reparent_selected(self):
        nodes=self._selected_nodes()
        if not nodes:return
        panels=[n for n in iter_nodes(self.data) if n.get('type')=='panel' and n not in nodes];ids=[str(n.get('id')) for n in panels]
        target_id,ok=QInputDialog.getItem(self,'Reparent','Target Panel:',ids,0,False)
        if not ok:return
        self._record();moved=[]
        for node in nodes:
            if reparent(self.data,node.get('id'),target_id):moved.append(node)
        self.selection=moved;self.current=moved[0] if moved else None;self.rebuild(preserve_current=True)
    def set_selected_z(self):
        nodes=self._selected_nodes()
        if not nodes:return
        z,ok=QInputDialog.getInt(self,'Set Z','Start Z:',int(nodes[0].get('z',0)),-9999,9999,1)
        if ok:self._record();set_z(nodes,z);self.rebuild(preserve_current=True)
    def align_center_x(self):
        if self.current is None or len(self.selection)!=1:return
        self._record();_,_,w,_=self.geom(self.current);self.current['x']=640-w//2;self.current['anchor']='top-left';self.rebuild(preserve_current=True)
    def align_center_y(self):
        if self.current is None or len(self.selection)!=1:return
        self._record();_,_,_,h=self.geom(self.current);self.current['y']=360-h//2;self.current['anchor']='top-left';self.rebuild(preserve_current=True)
    def align_center(self):
        if self.current is None or len(self.selection)!=1:return
        self._record();_,_,w,h=self.geom(self.current);self.current['x']=640-w//2;self.current['y']=360-h//2;self.current['anchor']='top-left';self.rebuild(preserve_current=True)
    def align_top(self):
        if self.current is None or len(self.selection)!=1:return
        self._record();self.current['y']=0;self.current['anchor']='top-left';self.rebuild(preserve_current=True)
    def align_left(self):
        if self.current is None or len(self.selection)!=1:return
        self._record();self.current['x']=0;self.current['anchor']='top-left';self.rebuild(preserve_current=True)
    def undo(self):
        if not self.history:return
        self.future.append(self._snapshot());self._restoring=True
        try:self.data=self.history.pop();self.selection=[];self.current=None;self.rebuild()
        finally:self._restoring=False
    def redo(self):
        if not self.future:return
        self.history.append(self._snapshot());self._restoring=True
        try:self.data=self.future.pop();self.selection=[];self.current=None;self.rebuild()
        finally:self._restoring=False
    def save_file(self):
        self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding='utf-8')
    def keyPressEvent(self,event):
        if event.key()==Qt.Key_Delete:self.delete_current();return
        if event.modifiers() & Qt.ControlModifier and event.key()==Qt.Key_D:self.duplicate_current();return
        if event.modifiers() & Qt.ControlModifier and event.key()==Qt.Key_Z:self.undo();return
        if event.modifiers() & Qt.ControlModifier and event.key()==Qt.Key_Y:self.redo();return
        if event.modifiers() & Qt.ControlModifier and event.key()==Qt.Key_S:self.save_file();return
        if self.selection and event.key() in (Qt.Key_Left,Qt.Key_Right,Qt.Key_Up,Qt.Key_Down) and not (event.modifiers() & Qt.ControlModifier):
            self._record();step=10 if event.modifiers() & Qt.ShiftModifier else 1;dx=dy=0
            if event.key()==Qt.Key_Left:dx=-step
            elif event.key()==Qt.Key_Right:dx=step
            elif event.key()==Qt.Key_Up:dy=-step
            else:dy=step
            translate_nodes(self.selection,dx,dy);self.rebuild(preserve_current=True);return
        super().keyPressEvent(event)
