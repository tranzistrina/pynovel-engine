from __future__ import annotations
import json
from typing import Any
from .asset_runtime import AssetRuntime
from .builtin_systems import BUILTIN_SYSTEM_FACTORIES
from .components import ComponentRegistry, ComponentSystem
from .event_bus import EventBus
from .expression import ExpressionEvaluator
from .game_logic import GameLogic
from .project import ProjectLoader
from .resources import ResourceRegistry
from .scene_registry import SceneContext, SceneRegistry
from .scene_stack import SceneStack
from .systems import SystemRegistry
from .transition import TransitionManager


class ProjectRuntime:
    """Runtime for data-driven games with scenes, ECS components, systems and events."""
    def __init__(self, project: str, *, emit=None, scenes: SceneRegistry | None = None, viewport: Any = None, frontend: Any = None):
        self.project=ProjectLoader(project); self.emit=emit or (lambda name,data:None); self.events=EventBus(); self.scenes=scenes or SceneRegistry(); self.stack=SceneStack(); self.transitions=TransitionManager()
        initial_variables=getattr(self.project.manifest,"variables",{}); self.logic=GameLogic(initial_variables if isinstance(initial_variables,dict) else {}); self.expression=ExpressionEvaluator(self.logic.state)
        self.components=ComponentRegistry(); self._register_builtin_components(); self._load_components(); self.resources=ResourceRegistry(self.project.root); self._load_resources(); self.frontend=frontend
        loader=None
        if frontend is not None and getattr(frontend,"_pygame",None) is not None:
            from .pygame_assets import PygameAssetLoader; loader=PygameAssetLoader(frontend._pygame)
        self.assets=AssetRuntime(self.resources,loader=loader); self.viewport=viewport; self.world=None; self.scene_id=None; self.scene=None; self.running=False
        self.systems=SystemRegistry(); self.component_systems=[]; self._system_instances={}; self._subscriptions=[]; self._register_builtin_system_factories(); self._load_systems()
        if not self.scenes.has("map"): self.scenes.register("map",self._create_map_scene)
        self._register_project_scenes()

    def _register_builtin_components(self):
        self.components.register("transform",defaults={"x":0.0,"y":0.0}); self.components.register("state",defaults={}); self.components.register("metadata",defaults={}); self.components.register("velocity",defaults={"x":0.0,"y":0.0})
    def _register_builtin_system_factories(self):
        for kind,factory in BUILTIN_SYSTEM_FACTORIES.items(): self.systems.register_factory(kind,factory)
    def _load_components(self):
        path=self.project.root/"components.json"
        if not path.is_file(): return
        try:data=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return
        if not isinstance(data,dict):return
        try:self.components.register_data(data,replace=False)
        except (ValueError,KeyError):return
    def _load_systems(self):
        path=self.project.root/"systems.json"
        if not path.is_file(): return
        try:data=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return
        if not isinstance(data,dict):return
        try:self.systems.register_data(data,replace=False)
        except (ValueError,KeyError):return
        self._instantiate_systems()
    def _instantiate_systems(self):
        for name in self.systems.order():
            if name in self._system_instances: continue
            runtime_system=self.systems.instantiate(name)
            if runtime_system is not None:self._system_instances[name]=runtime_system
            if isinstance(runtime_system,ComponentSystem): self.register_component_system(runtime_system)
            spec=self.systems.get(name); handler=getattr(runtime_system,"on_event",None) if runtime_system is not None else None
            if callable(handler):
                for event in spec.events:self._subscriptions.append(self.events.subscribe(event,lambda data, event_name=event, handler=handler: handler(event_name,data)))
    def register_component(self,name,*,factory=None,requires=(),defaults=None,metadata=None,replace=False):return self.components.register(name,factory=factory,requires=requires,defaults=defaults,metadata=metadata,replace=replace)
    def register_component_system(self,system:ComponentSystem):
        if any(item.name==system.name for item in self.component_systems):raise ValueError(f"Component system already registered: {system.name}")
        missing=[name for name in system.requires if not self.components.has(name)]
        if missing:raise ValueError(f"Unknown component requirements for {system.name}: {missing}")
        self.component_systems.append(system);return system
    def unregister_component_system(self,name):self.component_systems=[item for item in self.component_systems if item.name!=str(name)];self._system_instances.pop(str(name),None)
    def register_system_definition(self,name,**kwargs):
        spec=self.systems.register(name,**kwargs);runtime_system=self.systems.instantiate(spec.name)
        if runtime_system is not None:self._system_instances[spec.name]=runtime_system
        if isinstance(runtime_system,ComponentSystem):self.register_component_system(runtime_system)
        handler=getattr(runtime_system,"on_event",None) if runtime_system is not None else None
        if callable(handler):
            for event in spec.events:self._subscriptions.append(self.events.subscribe(event,lambda data,event_name=event,handler=handler: handler(event_name,data)))
        return spec
    def system_plan(self,phase=None):
        specs=self.systems.enabled_specs(phase); return {"phase":phase,"order":[s.name for s in specs],"systems":[s.to_dict()|{"name":s.name} for s in specs],"instances":[name for name in self._system_instances if name in {s.name for s in specs}]}
    def emit_event(self,event,data=None):return self.events.emit(event,data)
    def queue_event(self,event,data=None):self.events.queue(event,data)
    def subscribe(self,event,handler):return self.events.subscribe(event,handler)
    def _load_resources(self):
        path=self.project.root/"resources.json"
        if not path.is_file():return
        try:data=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return
        if not isinstance(data,dict):return
        for rid,definition in data.items():
            if not isinstance(definition,dict) or definition.get("path") is None:continue
            try:self.resources.register(str(rid),str(definition["path"]),str(definition.get("type","other")),metadata=definition.get("metadata"))
            except ValueError:continue
    def _register_project_scenes(self):
        try:definitions=self.project.load_scenes()
        except (OSError,json.JSONDecodeError):return
        for scene_id,definition in definitions.items():
            if isinstance(scene_id,str) and isinstance(definition,dict) and not self.scenes.has(scene_id):self.scenes.register(scene_id,lambda context,definition=definition:self._create_declarative_scene(definition,context))
    @staticmethod
    def _create_declarative_scene(definition,context):
        from .declarative_scene import DeclarativeScene;return DeclarativeScene(definition,context.runtime)
    def _create_map_scene(self,context):
        from .map.scene import MapScene
        game_map=context.runtime.project.load_map(emit=context.runtime.emit);viewport=context.runtime.viewport
        if viewport is None and context.runtime.frontend is not None:
            screen=getattr(context.runtime.frontend,"screen",None)
            if screen is not None:viewport=screen.get_rect()
        if viewport is None:raise RuntimeError("Map scene requires a viewport")
        game_map.world.entities.component_registry=context.runtime.components
        return MapScene(game_map,viewport,pygame_module=getattr(context.runtime.frontend,"_pygame",None),emit=context.runtime.emit)
    def get(self,key,default=None):return self.logic.get(key,default)
    def set(self,key,value):return self.logic.set(str(key),value)
    def change(self,key,amount=1):return self.logic.change(str(key),amount)
    def evaluate(self,expression):return self.expression.evaluate(expression)
    def start(self,*,transition=None):self.running=True;self.switch_scene(self.project.manifest.start_scene,transition=transition);self.emit("runtime.started",{"scene":self.scene_id})
    def switch_scene(self,scene_id,*,transition=None):
        previous=self.scene_id
        if transition:self.transitions.start(*transition)
        if self.scene is not None:self._call(self.scene,"exit")
        scene=self.scenes.create(scene_id,self);self.stack.clear();self.stack.push(scene_id,scene);self.scene_id=scene_id;self.scene=scene;self.world=getattr(scene,"world",scene)
        try:self._call(scene,"enter")
        except Exception:self.stack.clear();self.scene=self.scene_id=self.world=None;raise
        self.emit("scene.changed",{"from":previous,"to":scene_id});self.events.emit("scene.changed",{"from":previous,"to":scene_id});return scene
    def push_scene(self,scene_id,*,transition=None):
        if transition:self.transitions.start(*transition)
        if self.scene is not None:self._call(self.scene,"pause")
        scene=self.scenes.create(scene_id,self);self.stack.push(scene_id,scene);self.scene_id=scene_id;self.scene=scene;self.world=getattr(scene,"world",scene)
        try:self._call(scene,"enter")
        except Exception:
            self.stack.pop()
            if self.stack.current is not None:self.scene_id=self.stack.current_id;self.scene=self.stack.current;self.world=getattr(self.scene,"world",self.scene);self._call(self.scene,"resume")
            raise
        self.emit("scene.pushed",{"scene":scene_id});self.events.emit("scene.pushed",{"scene":scene_id});return scene
    def pop_scene(self,*,transition=None):
        if len(self.stack)<=1:raise IndexError("Cannot pop the root scene")
        if transition:self.transitions.start(*transition)
        self._call(self.scene,"exit");self.stack.pop();self.scene_id=self.stack.current_id;self.scene=self.stack.current;self.world=getattr(self.scene,"world",self.scene);self._call(self.scene,"resume");self.emit("scene.popped",{"scene":self.scene_id});self.events.emit("scene.popped",{"scene":self.scene_id});return self.scene
    def handle_input(self,event):
        if not self.running or self.scene is None:return False
        self.events.emit("input.raw",event);self.events.flush();handler=getattr(self.scene,"handle_input",None);handled=bool(handler(event)) if callable(handler) else False;self.events.emit("input.handled",{"event":event,"handled":handled});
        for spec in self.systems.enabled_specs("input"):
            system=self._system_instances.get(spec.name)
            if system is not None and hasattr(system,"handle_input"):system.handle_input(event,self.world,self.logic)
        return handled
    def render(self,target):
        if self.scene is None:return
        self.events.emit("phase.render",{"target":target});renderer=getattr(self.scene,"render",getattr(self.scene,"draw",None));
        if callable(renderer):renderer(target)
        for spec in self.systems.enabled_specs("render"):
            system=self._system_instances.get(spec.name)
            if system is not None and hasattr(system,"render"):system.render(target,self.world,self.logic)
    def update(self,dt):
        if not self.running or self.scene is None:return
        value=max(0.0,float(dt));self.events.emit("phase.update",{"dt":value});self.events.flush();self.transitions.update(value);update=getattr(self.scene,"update",None)
        if callable(update):update(value)
        entities=self.world.entities if self.world is not None and hasattr(self.world,"entities") else None
        if entities is not None:
            for spec in self.systems.enabled_specs("update"):
                system=self._system_instances.get(spec.name)
                if isinstance(system,ComponentSystem):system.run(value,entities,self.logic)
        self.events.flush()
    def stop(self):
        if self.scene is not None:self._call(self.scene,"exit")
        for subscription in tuple(self._subscriptions):self.events.unsubscribe(subscription)
        self._subscriptions.clear();self._system_instances.clear();self.events.clear();self.assets.clear();self.running=False;self.emit("runtime.stopped",{})
    def save_state(self):
        saver=getattr(self.scene,"serialize",None);world=saver() if callable(saver) else (self.world.serialize() if self.world is not None else None);return {"scene_stack":list(self.stack.ids()),"scene":self.scene_id,"logic":self.logic.serialize(),"world":world}
    def load_state(self,state):
        ids=state.get("scene_stack") or [state.get("scene",self.project.manifest.start_scene)]
        if not isinstance(ids,list) or not ids:raise ValueError("save state must contain a non-empty scene stack")
        self.switch_scene(str(ids[0]));[self.push_scene(str(scene_id)) for scene_id in ids[1:]];self.logic.deserialize(state.get("logic",{}));self.expression=ExpressionEvaluator(self.logic.state)
        if state.get("world") is not None and self.world is not None:self.world.deserialize(state["world"])
        refresh=getattr(self.scene,"refresh",None)
        if callable(refresh):refresh()
        self.running=True;self.emit("runtime.loaded",{"scene":self.scene_id});self.events.emit("runtime.loaded",{"scene":self.scene_id})
    @staticmethod
    def _call(scene,method):
        callback=getattr(scene,method,None)
        if callable(callback):callback()
