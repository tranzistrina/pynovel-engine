from __future__ import annotations
import json
from pathlib import Path
from vnengine.core.model import SaveState

def write_save(path:str|Path,state:SaveState)->None:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({'action_index':state.action_index,'variables':state.variables,'history':state.history,'background':state.background,'characters':state.characters},ensure_ascii=False,indent=2),encoding='utf-8')

def read_save(path:str|Path)->SaveState:
    d=json.loads(Path(path).read_text(encoding='utf-8'))
    return SaveState(d['action_index'],d['variables'],[tuple(x) for x in d.get('history',[])],d.get('background'),d.get('characters',{}))
