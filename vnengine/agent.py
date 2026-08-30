from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ai import AIProjectAPI
from .ai_builder import AIProjectBuilder
from .ai_schema import BUILDER_COMMANDS, command_schema


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    path: str | None = None
    suggestion: str | None = None
    def to_dict(self) -> dict[str, Any]:
        data={"severity":self.severity,"code":self.code,"message":self.message}
        if self.path is not None:data["path"]=self.path
        if self.suggestion is not None:data["suggestion"]=self.suggestion
        return data


class AIAgentInterface:
    """Stable agent facade for inspect, plan, mutate, validate and diagnose."""
    API_VERSION=12
    def __init__(self,root: str | Path,*,runtime: Any=None):
        self.root=Path(root).resolve();self.builder=AIProjectBuilder(self.root);self.runtime=runtime;self.runtime_api=AIProjectAPI(runtime) if runtime is not None else None
    def capabilities(self)->dict[str,Any]:
        return {"api_version":self.API_VERSION,"features":["inspect","plan","dry_run","apply","validate","diagnose","transactions","resources","asset_cache","performance_telemetry","components","systems","events","system_phases","runtime_state"],"commands":self.command_schema()}
    def inspect(self)->dict[str,Any]:
        result=self.builder.inspect()
        if self.runtime_api is not None:result["runtime"]=self.runtime_api.describe().get("runtime",{})
        for filename,key in (("resources.json","resource_ids"),("components.json","component_names"),("systems.json","system_names")):
            path=self.root/filename
            if path.is_file():
                try:data=self._read_json(path);result[key]=sorted(data) if isinstance(data,dict) else []
                except Exception:result[key]=[]
        if self.runtime is not None:
            assets=getattr(self.runtime,"assets",None)
            if assets is not None and callable(getattr(assets,"inspect",None)):result["asset_runtime"]=assets.inspect()
            profiler=getattr(self.runtime,"profiler",None)
            if profiler is not None and callable(getattr(profiler,"snapshot",None)):result["performance"]=profiler.snapshot()
            planner=getattr(self.runtime,"system_plan",None)
            if callable(planner):result["system_plan"]=planner()
            saver=getattr(self.runtime,"save_state",None)
            if callable(saver):
                try:result["runtime_state"]=saver()
                except Exception:result["runtime_state"]=None
        return result
    def plan(self,operations:list[dict[str,Any]])->dict[str,Any]:
        diagnostics=[];specs={spec.name:spec for spec in BUILDER_COMMANDS}
        for index,operation in enumerate(operations):
            location=f"operations[{index}]"
            if not isinstance(operation,dict):diagnostics.append(Diagnostic("error","invalid_operation","Operation must be an object.",location).to_dict());continue
            command=operation.get("command");spec=specs.get(command)
            if spec is None:diagnostics.append(Diagnostic("error","unknown_command",f"Unsupported builder command: {command}",f"{location}.command").to_dict());continue
            for name in spec.required:
                if name not in operation:diagnostics.append(Diagnostic("error","missing_argument",f"Missing required argument: {name}",f"{location}.{name}").to_dict())
            allowed=set(spec.required)|set(spec.optional)|{"command"}
            for name in operation:
                if name not in allowed:diagnostics.append(Diagnostic("error","unexpected_argument",f"Unexpected argument: {name}",f"{location}.{name}").to_dict())
        return {"valid":not diagnostics,"operations":len(operations),"diagnostics":diagnostics}
    def dry_run(self,operations:list[dict[str,Any]])->dict[str,Any]:
        plan=self.plan(operations);before=self.builder.document.inspect()
        if not plan["valid"]:return {"committed":False,"applied":0,"before":before,"preview":before,"plan":plan,"diagnostics":plan["diagnostics"]}
        self.builder.document.begin()
        try:results=[self.builder._dispatch(op) for op in operations];preview=self.builder.document.inspect()
        except Exception as exc:
            self.builder.document.rollback();return {"committed":False,"applied":0,"before":before,"preview":before,"plan":plan,"diagnostics":[self._exception_diagnostic(exc).to_dict()]}
        self.builder.document.rollback();return {"committed":False,"applied":len(results),"before":before,"preview":preview,"plan":plan,"diagnostics":[]}
    def apply(self,operations:list[dict[str,Any]],*,save:bool=True,validate:bool=True)->dict[str,Any]:
        plan=self.plan(operations)
        if not plan["valid"]:return {"committed":False,"applied":0,"plan":plan,"diagnostics":plan["diagnostics"]}
        try:result=self.builder.apply(operations,save=save)
        except Exception as exc:return {"committed":False,"applied":0,"plan":plan,"diagnostics":[self._exception_diagnostic(exc).to_dict()]}
        validation=self.validate() if validate else {"valid":True,"errors":[],"warnings":[]};result.update({"committed":True,"validation":validation,"diagnostics":validation["errors"]+validation["warnings"]});return result
    def execute(self,operations:list[dict[str,Any]],*,dry_run:bool=False,save:bool=True,validate:bool=True)->dict[str,Any]:return self.dry_run(operations) if dry_run else self.apply(operations,save=save,validate=validate)
    def validate(self)->dict[str,Any]:
        errors=[];warnings=[];manifest_path=self.root/"project.json"
        if not manifest_path.is_file():return {"valid":False,"errors":[Diagnostic("error","missing_manifest","Project manifest is missing.","project.json","Run create_project first.").to_dict()],"warnings":[]}
        try:manifest=self._read_json(manifest_path)
        except Exception as exc:return {"valid":False,"errors":[Diagnostic("error","invalid_manifest_json",str(exc),"project.json","Fix the JSON syntax.").to_dict()],"warnings":[]}
        legacy="scenario" in manifest and "map_path" not in manifest
        required=("name","version","scenario") if legacy else ("name","version","map_path","start_scene")
        for key in required:
            if key not in manifest:errors.append(Diagnostic("error","missing_manifest_field",f"Manifest field is missing: {key}","project.json").to_dict())
        if not legacy:
            map_path=self.root/str(manifest.get("map_path","map.json"))
            if not map_path.is_file():errors.append(Diagnostic("error","missing_map","Configured map file is missing.",str(map_path.relative_to(self.root)),"Create a map or correct map_path.").to_dict())
            else:self._validate_map(map_path,errors,warnings)
            scenes_path=self.root/"scenes.json"
            if scenes_path.is_file():self._validate_scenes(scenes_path,manifest.get("start_scene"),errors,warnings)
            elif manifest.get("start_scene") not in (None,"map"):errors.append(Diagnostic("error","missing_scenes","Non-map start scene requires scenes.json.","project.json","Create the start scene.").to_dict())
        else:
            scenario=self.root/str(manifest.get("scenario","game.vn"))
            if not scenario.is_file():warnings.append(Diagnostic("warning","missing_scenario",f"Legacy scenario file is missing: {manifest.get('scenario')}","project.json","Add the scenario file or migrate the project.").to_dict())
        self._validate_resources(errors,warnings);self._validate_components(errors,warnings);self._validate_systems(errors,warnings)
        return {"valid":not errors,"errors":errors,"warnings":warnings}
    def diagnose(self):
        validation=self.validate();return {"valid":validation["valid"],"diagnostics":validation["errors"]+validation["warnings"],"next":self._next_steps(validation)}
    def command_schema(self):return command_schema()
    def _next_steps(self,validation):
        if validation["valid"]:return ["Project passes validation."] if not validation["warnings"] else ["Resolve warnings before release."]
        return [item.get("suggestion") or item.get("message") for item in validation["errors"][:5]]
    def _exception_diagnostic(self,exc):return Diagnostic("error","operation_failed",str(exc),suggestion="Fix the reported operation and retry.")
    def _validate_map(self,path,errors,warnings):
        try:data=self._read_json(path)
        except Exception as exc:errors.append(Diagnostic("error","invalid_map_json",str(exc),str(path.relative_to(self.root))).to_dict());return
        if not isinstance(data,dict):errors.append(Diagnostic("error","invalid_map","Map root must be an object.",str(path.relative_to(self.root))).to_dict());return
        nodes=data.get("nodes",[]);connections=data.get("connections",[]);entities=data.get("entities",[])
        if not isinstance(nodes,list):errors.append(Diagnostic("error","invalid_nodes","nodes must be an array.","map.json.nodes").to_dict());nodes=[]
        if not isinstance(connections,list):errors.append(Diagnostic("error","invalid_connections","connections must be an array.","map.json.connections").to_dict());connections=[]
        if not isinstance(entities,list):errors.append(Diagnostic("error","invalid_entities","entities must be an array.","map.json.entities").to_dict());entities=[]
        node_ids=set();entity_ids=set()
        for i,node in enumerate(nodes):
            if not isinstance(node,dict) or not node.get("id"):errors.append(Diagnostic("error","invalid_node","Node requires an id.",f"map.json.nodes[{i}]").to_dict());continue
            nid=str(node["id"])
            if nid in node_ids:errors.append(Diagnostic("error","duplicate_node",f"Duplicate node id: {nid}",f"map.json.nodes[{i}]").to_dict())
            node_ids.add(nid)
        for i,connection in enumerate(connections):
            if not isinstance(connection,dict) or str(connection.get("source")) not in node_ids or str(connection.get("target")) not in node_ids:errors.append(Diagnostic("error","invalid_connection","Connection references an unknown node.",f"map.json.connections[{i}]").to_dict())
        for i,entity in enumerate(entities):
            if not isinstance(entity,dict) or not entity.get("id") or str(entity.get("node_id")) not in node_ids:errors.append(Diagnostic("error","invalid_entity","Entity requires an id and valid node_id.",f"map.json.entities[{i}]").to_dict());continue
            eid=str(entity["id"])
            if eid in entity_ids:errors.append(Diagnostic("error","duplicate_entity",f"Duplicate entity id: {eid}",f"map.json.entities[{i}]").to_dict())
            entity_ids.add(eid)
    def _validate_scenes(self,path,start,errors,warnings):
        try:scenes=self._read_json(path)
        except Exception as exc:errors.append(Diagnostic("error","invalid_scenes_json",str(exc),"scenes.json").to_dict());return
        if not isinstance(scenes,dict):errors.append(Diagnostic("error","invalid_scenes","scenes.json root must be an object.","scenes.json").to_dict());return
        if start and start!="map" and start not in scenes:errors.append(Diagnostic("error","unknown_start_scene",f"Start scene is not defined: {start}","project.json").to_dict())
        for scene_id,scene in scenes.items():
            if not isinstance(scene,dict):errors.append(Diagnostic("error","invalid_scene","Scene definition must be an object.",f"scenes.json.{scene_id}").to_dict());continue
            actions=scene.get("actions",[])
            if not isinstance(actions,list):errors.append(Diagnostic("error","invalid_scene_actions","Scene actions must be an array.",f"scenes.json.{scene_id}.actions").to_dict());continue
            labels=set()
            for index,action in enumerate(actions):
                if not isinstance(action,dict):errors.append(Diagnostic("error","invalid_action","Action must be an object.",f"scenes.json.{scene_id}.actions[{index}]").to_dict());continue
                kind=action.get("type")
                if kind=="label":
                    label=action.get("label")
                    if label in labels:errors.append(Diagnostic("error","duplicate_label",f"Duplicate label: {label}",f"scenes.json.{scene_id}.actions[{index}]").to_dict())
                    elif label:labels.add(str(label))
                if kind=="say" and not action.get("text"):warnings.append(Diagnostic("warning","empty_dialogue","Dialogue action has empty text.",f"scenes.json.{scene_id}.actions[{index}]").to_dict())
                if kind not in {"say","choice","set","change","emit","label","goto","character","if"}:errors.append(Diagnostic("error","unknown_action",f"Unknown action type: {kind}",f"scenes.json.{scene_id}.actions[{index}].type").to_dict())
    def _validate_components(self,errors,warnings):
        path=self.root/"components.json"
        if not path.is_file():return
        try:data=self._read_json(path)
        except Exception as exc:errors.append(Diagnostic("error","invalid_components_json",str(exc),"components.json").to_dict());return
        if not isinstance(data,dict):errors.append(Diagnostic("error","invalid_components","components.json root must be an object.","components.json").to_dict());return
        names=set(data)
        for name,raw in data.items():
            if not isinstance(raw,dict):errors.append(Diagnostic("error","invalid_component","Component definition must be an object.",f"components.json.{name}").to_dict());continue
            for req in raw.get("requires",[]):
                if req not in names and req not in {"transform","state","metadata"}:errors.append(Diagnostic("error","unknown_component_requirement",f"Component {name} requires unknown component: {req}",f"components.json.{name}.requires").to_dict())
    def _validate_systems(self,errors,warnings):
        path=self.root/"systems.json"
        if not path.is_file():return
        try:data=self._read_json(path)
        except Exception as exc:errors.append(Diagnostic("error","invalid_systems_json",str(exc),"systems.json").to_dict());return
        if not isinstance(data,dict):errors.append(Diagnostic("error","invalid_systems","systems.json root must be an object.","systems.json").to_dict());return
        names=set(data);edges={name:[] for name in names}
        for name,raw in data.items():
            if not isinstance(raw,dict):errors.append(Diagnostic("error","invalid_system","System definition must be an object.",f"systems.json.{name}").to_dict());continue
            for req in raw.get("requires",[]):
                if not req:errors.append(Diagnostic("error","invalid_system_requirement","System component requirement is empty.",f"systems.json.{name}.requires").to_dict())
            for target in list(raw.get("before",[]))+list(raw.get("after",[])):
                if target not in names:errors.append(Diagnostic("error","unknown_system_reference",f"System {name} references unknown system: {target}",f"systems.json.{name}").to_dict())
            for phase in raw.get("phases",["update"]):
                if phase not in {"input","update","render"}:errors.append(Diagnostic("error","invalid_system_phase",f"Invalid system phase: {phase}",f"systems.json.{name}.phases").to_dict())
            edges[name]=list(raw.get("before",[]));edges[name].extend(target for target in raw.get("after",[]) if target in names)
        def visit(node,active,done):
            if node in active:errors.append(Diagnostic("error","system_cycle","System dependency graph contains a cycle.","systems.json","Break the before/after cycle.").to_dict());return
            if node in done:return
            active.add(node)
            for target in edges.get(node,[]):
                if target in names:visit(target,active,done)
            active.remove(node);done.add(node)
        done=set()
        for name in sorted(names):visit(name,set(),done)
    def _validate_resources(self,errors,warnings):
        path=self.root/"resources.json"
        if not path.is_file():return
        try:resources=self._read_json(path)
        except Exception as exc:errors.append(Diagnostic("error","invalid_resources_json",str(exc),"resources.json","Fix the JSON syntax.").to_dict());return
        if not isinstance(resources,dict):errors.append(Diagnostic("error","invalid_resources","resources.json root must be an object.","resources.json").to_dict());return
        for resource_id,resource in resources.items():
            location=f"resources.json.{resource_id}"
            if not isinstance(resource,dict):errors.append(Diagnostic("error","invalid_resource","Resource definition must be an object.",location).to_dict());continue
            if not resource.get("path"):errors.append(Diagnostic("error","missing_resource_path","Resource requires a path.",location).to_dict());continue
            candidate=(self.root/str(resource["path"])).resolve()
            try:candidate.relative_to(self.root)
            except ValueError:errors.append(Diagnostic("error","resource_path_escape","Resource path escapes project root.",f"{location}.path").to_dict());continue
            if not candidate.is_file():warnings.append(Diagnostic("warning","missing_resource",f"Resource file is missing: {resource['path']}",f"{location}.path","Add the file or correct the path.").to_dict())
            if not resource.get("type"):warnings.append(Diagnostic("warning","missing_resource_type","Resource has no explicit type.",f"{location}.type").to_dict())
    @staticmethod
    def _read_json(path:Path)->Any:return json.loads(path.read_text(encoding="utf-8"))
