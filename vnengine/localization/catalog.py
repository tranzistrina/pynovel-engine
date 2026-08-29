from __future__ import annotations
import json
from pathlib import Path

class Catalog:
    def __init__(self,root:str|Path,language:str='ru'):
        self.root=Path(root); self.language=language; self.data={}; self.reload()
    def reload(self):
        p=self.root/f'{self.language}.json'
        self.data=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    def get(self,key:str,default:str|None=None):
        return self.data.get(key, default if default is not None else key)
