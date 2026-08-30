from __future__ import annotations
from pathlib import Path
from typing import Any
from .project_document import ProjectDocument

class AIProjectBuilder:
    """High-level, transactional project authoring API for coding agents."""
    def __init__(self, root: str | Path, *, document: ProjectDocument | None = None): self.document=document or ProjectDocument(root); self.root=self.document.root
    @property
    def manifest_path(self): return self.root/"project.json"
    @property
    def map_path(self): return self.root/str(self.document.data.get("map_path","map.json"))
    def create_project(self,name,*,version="1.0",map_path="map.json",start_scene="map",variables=None):
        self.document.data.update({"name":str(name),"version":str(version),"map_path":str(map_path),"start_scene":str(start_scene)}); 
        if variables is not None:self.document.data["variables"]=dict(variables)
        return self.document.manifest()
    def set_variable(self,key,value):return self.document.set_variable(key,value)
    def create_map(self,*,width,height,background=None):
        payload=self.document.ensure_map(); payload.update({"width":float(width),"height":float(height),"nodes":[],"connections":[],"entities":[]})
        if background is not None:payload["background"]=background
        return payload
    def add_component(self,component,*,requires=(),defaults=None,metadata=None):return self.document.add_component(component,requires=requires,defaults=defaults,metadata=metadata)
    def remove_component(self,component):return self.document.remove_component(component)
    def add_system(self,system,*,kind="generic",requires=(),before=(),after=(),phases=("update",),events=(),enabled=True,priority=0,settings=None):return self.document.add_system(system,kind=kind,requires=requires,before=before,after=after,phases=phases,events=events,enabled=enabled,priority=priority,settings=settings)
    def remove_system(self,system):return self.document.remove_system(system)
    def add_resource(self,resource_id,path,resource_type,*,metadata=None):return self.document.add_resource(resource_id,path,resource_type,metadata=metadata)
    def remove_resource(self,resource_id):return self.document.remove_resource(resource_id)
    def add_scene(self,scene_id,*,background=None):return self.document.add_scene(scene_id,background=background)
    def remove_scene(self,scene_id):return self.document.remove_scene(scene_id)
    def add_scene_action(self,scene_id,action_type,**data):return self.document.add_scene_action(scene_id,{"type":action_type,**data})
    def say(self,scene_id,speaker,text):return self.add_scene_action(scene_id,"say",speaker=speaker,text=text)
    def choice(self,scene_id,text,target,*,condition=None):
        data={"text":text,"target":target}
        if condition is not None:data["condition"]=condition
        return self.add_scene_action(scene_id,"choice",**data)
    def set_action(self,scene_id,variable,value):return self.add_scene_action(scene_id,"set",variable=variable,value=value)
    def change_action(self,scene_id,variable,amount=1):return self.add_scene_action(scene_id,"change",variable=variable,amount=amount)
    def goto(self,scene_id,target):return self.add_scene_action(scene_id,"goto",target=target)
    def label(self,scene_id,name):return self.add_scene_action(scene_id,"label",label=name)
    def add_node(self,node_id,x,y,*,label="",metadata=None):return self.document.add_node(node_id,x,y,label=label,metadata=metadata)
    def add_connection(self,source,target,*,cost=1.0,blocked=False,metadata=None):return self.document.add_connection(source,target,cost=cost,blocked=blocked,metadata=metadata)
    def add_entity(self,entity_id,node_id,*,components=None):return self.document.add_entity(entity_id,node_id,components=components)
    def set_entity_component(self,entity_id,component,value=None):
        entity=self.document._find_by_id(self.document.ensure_map()["entities"],entity_id)
        if entity is None:raise ValueError(f"Unknown entity: {entity_id}")
        if not str(component):raise ValueError("Component name must not be empty")
        comps=entity.setdefault("components",{})
        if not isinstance(comps,dict):raise ValueError(f"Entity components must be an object: {entity_id}")
        comps[str(component)]=value; return value
    def remove_entity_component(self,entity_id,component):
        entity=self.document._find_by_id(self.document.ensure_map()["entities"],entity_id)
        if entity is None:raise ValueError(f"Unknown entity: {entity_id}")
        comps=entity.get("components",{})
        if not isinstance(comps,dict):raise ValueError(f"Entity components must be an object: {entity_id}")
        return comps.pop(str(component),None)
    def apply_entity_components(self,entity_id,components,*,replace=False):
        entity=self.document._find_by_id(self.document.ensure_map()["entities"],entity_id)
        if entity is None:raise ValueError(f"Unknown entity: {entity_id}")
        current=entity.setdefault("components",{})
        if not isinstance(current,dict):raise ValueError(f"Entity components must be an object: {entity_id}")
        entity["components"]=dict(components) if replace else {**current,**components}; return entity["components"]
    def set_map_property(self,key,value):
        if key in {"nodes","connections","entities"}:raise ValueError(f"Map collection cannot be replaced: {key}")
        self.document.ensure_map()[str(key)]=value; return value
    def set_entity_property(self,entity_id,key,value):
        entity=self.document._find_by_id(self.document.ensure_map()["entities"],entity_id)
        if entity is None:raise ValueError(f"Unknown entity: {entity_id}")
        if key=="id":raise ValueError("Entity id cannot be changed")
        entity[str(key)]=value; return value
    def remove_node(self,node_id):
        payload=self.document.ensure_map(); node=self.document._find_by_id(payload["nodes"],node_id)
        if node is None:raise ValueError(f"Unknown node: {node_id}")
        if any(c.get("source")==node_id or c.get("target")==node_id for c in payload["connections"]):raise ValueError(f"Cannot remove node with connections: {node_id}")
        if any(e.get("node_id")==node_id for e in payload["entities"]):raise ValueError(f"Cannot remove node with entities: {node_id}")
        payload["nodes"].remove(node); return node
    def remove_entity(self,entity_id):
        entities=self.document.ensure_map()["entities"];entity=self.document._find_by_id(entities,entity_id)
        if entity is None:raise ValueError(f"Unknown entity: {entity_id}")
        entities.remove(entity); return entity
    def transaction(self):return self.document.begin()
    def commit(self,*,save=True):
        self.document.commit()
        if save:self.document.save()
    def rollback(self):self.document.rollback()
    def apply(self,operations,*,save=True):
        self.document.begin()
        try:results=[self._dispatch(operation) for operation in operations]
        except Exception:self.document.rollback();raise
        self.document.commit()
        if save:self.document.save()
        return {"applied":len(results),"results":results,"project":self.inspect()}
    def _dispatch(self,operation):
        payload=dict(operation);command=payload.pop("command",None)
        if not isinstance(command,str):raise ValueError("Operation requires a string 'command'")
        names=("create_project","set_variable","create_map","add_component","remove_component","add_system","remove_system","add_resource","remove_resource","add_scene","remove_scene","add_scene_action","say","choice","set_action","change_action","goto","label","add_node","add_connection","add_entity","set_entity_component","remove_entity_component","apply_entity_components","set_map_property","set_entity_property","remove_node","remove_entity")
        handler=getattr(self,command,None) if command in names else None
        if handler is None:raise ValueError(f"Unsupported builder command: {command}")
        return handler(**payload)
    def inspect(self):return {"root":str(self.root),**self.document.inspect(),"variables":dict(self.document.data.get("variables",{}))}
