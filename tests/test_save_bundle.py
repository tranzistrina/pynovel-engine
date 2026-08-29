import json
from vnengine.core.save_bundle import SaveBundle


def test_save_bundle_round_trip(tmp_path):
    bundle = SaveBundle("0.31.0", "inhRPG-0.1")
    bundle.state = {"campaign": {"day": 12}}
    bundle.extensions = {"factions": {"red": {"relation": 4}}}
    bundle.rng = {"seed": 7, "state": [1, 2, 3]}
    path = tmp_path / "save.json"
    bundle.save(path)
    restored = SaveBundle.load(path)
    assert restored.engine_version == "0.31.0"
    assert restored.project_version == "inhRPG-0.1"
    assert restored.state["campaign"]["day"] == 12
    assert restored.extensions["factions"]["red"]["relation"] == 4


def test_save_bundle_rejects_tampering(tmp_path):
    bundle = SaveBundle("0.31.0")
    path = tmp_path / "save.json"
    bundle.save(path)
    data = json.loads(path.read_text())
    data["state"] = {"campaign": {"day": 999}}
    path.write_text(json.dumps(data))
    try:
        SaveBundle.load(path)
    except ValueError as exc:
        assert "checksum" in str(exc)
    else:
        raise AssertionError("tampered save was accepted")
