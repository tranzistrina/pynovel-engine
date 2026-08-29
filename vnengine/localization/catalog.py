from __future__ import annotations
import json
from pathlib import Path

class Catalog:
    def __init__(self, root: str | Path, language: str = "ru"):
        self.root = Path(root); self.language = language; self.data = {}; self.reload()
    def reload(self):
        p=self.root/f"{self.language}.json"
        try:self.data=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        except (OSError,ValueError):self.data={}
    def set_language(self, language: str): self.language=language; self.reload()
    def get(self,key:str,default:str|None=None)->str: return self.data.get(key, default if default is not None else key)
    def languages(self)->list[str]: return sorted(p.stem for p in self.root.glob("*.json"))
