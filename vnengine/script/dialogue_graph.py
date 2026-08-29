from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

@dataclass
class DialogueNode:
    id: str
    kind: str = "say"
    speaker: str = "Narrator"
    text: str = ""
    target: str = ""
    x: float = 80.0
    y: float = 80.0
    options: list[dict[str, str]] = field(default_factory=list)

@dataclass
class DialogueGraph:
    title: str = "Dialogue"
    start: str = "start"
    nodes: list[DialogueNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DialogueGraph":
        return cls(title=raw.get("title", "Dialogue"), start=raw.get("start", "start"), nodes=[DialogueNode(**node) for node in raw.get("nodes", [])])

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "start": self.start, "nodes": [{"id":n.id,"kind":n.kind,"speaker":n.speaker,"text":n.text,"target":n.target,"x":n.x,"y":n.y,"options":n.options} for n in self.nodes]}

    def by_id(self) -> dict[str, DialogueNode]:
        return {n.id: n for n in self.nodes}

    def compile(self) -> str:
        nodes = self.by_id()
        if self.start not in nodes: raise ValueError(f"Start node '{self.start}' does not exist")
        lines = [f'title {json.dumps(self.title, ensure_ascii=False)}']
        visited: set[str] = set()
        def emit(node_id: str) -> None:
            if not node_id or node_id in visited: return
            node = nodes.get(node_id)
            if node is None: raise ValueError(f"Missing node target: {node_id}")
            visited.add(node_id); lines.append(f"label {node.id}")
            if node.kind == "say":
                lines.append(f"say {node.speaker or 'Narrator'} {json.dumps(node.text, ensure_ascii=False)}")
                if node.target: emit(node.target)
            elif node.kind == "jump":
                if not node.target: raise ValueError(f"Jump '{node.id}' needs a target")
                lines.append(f"jump {node.target}"); emit(node.target)
            elif node.kind == "condition":
                if not node.text: raise ValueError(f"Condition '{node.id}' needs an expression")
                if not node.target: raise ValueError(f"Condition '{node.id}' needs a target")
                lines.extend([f"if {node.text}", f"jump {node.target}", "endif"]); emit(node.target)
            elif node.kind == "choice":
                if not node.options: raise ValueError(f"Choice '{node.id}' has no options")
                lines.append("choice")
                for option in node.options:
                    text, target = option.get("text", "Option"), option.get("target", "")
                    if not target: raise ValueError(f"Choice '{node.id}' contains an option without a target")
                    lines.append(f"{json.dumps(text, ensure_ascii=False)}: {target}"); emit(target)
            elif node.kind == "end":
                lines.append("end")
            else: raise ValueError(f"Unsupported dialogue node kind: {node.kind}")
        emit(self.start)
        unreachable = sorted(set(nodes) - visited)
        if unreachable: lines.append("# Unreachable nodes: " + ", ".join(unreachable))
        return "\n".join(lines) + "\n"
