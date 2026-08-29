import json
from pathlib import Path


def test_ui_json_roundtrip(tmp_path: Path):
    data = {
        "type": "panel",
        "id": "root",
        "width": "100%",
        "height": "100%",
        "children": [
            {"type": "button", "id": "start", "x": "50%", "y": "50%", "anchor": "center", "width": 240, "height": 56, "text": "Start"}
        ],
    }
    path = tmp_path / "ui.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["children"][0]["id"] == "start"
    assert loaded["children"][0]["anchor"] == "center"
