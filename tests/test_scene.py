import json
from pathlib import Path


def test_demo_scene_manifest():
    path = Path(__file__).parents[1] / "examples/demo/scene.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["resolution"] == [1280, 720]
    assert data["characters"][0]["name"] == "Alice"
    assert 0 <= data["characters"][0]["x"] <= 100
