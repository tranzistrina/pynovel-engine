from pathlib import Path

from vnengine import __version__
from vnengine.core.save_bundle import SaveBundle
from vnengine.extensions.input import InputMap
from vnengine.extensions.system import SystemRegistry
from vnengine.headless import HeadlessHarness


def test_package_version_matches_current_engine_release():
    assert __version__ == "0.40.0"


def test_system_registry_exposes_mapping_and_serialization_api():
    registry = SystemRegistry()
    assert registry.items() == ()
    assert registry.names() == ()
    assert registry.serialize() == {}


def test_input_map_roundtrip_preserves_binding_shape():
    mapping = InputMap()
    mapping.bind("confirm", "KEYDOWN", 13)
    assert mapping.actions_for("KEYDOWN", 13) == ("confirm",)
    restored = InputMap.deserialize(mapping.serialize())
    assert restored.actions_for("KEYDOWN", 13) == ("confirm",)


def test_save_bundle_roundtrip_keeps_checksum_valid(tmp_path: Path):
    path = tmp_path / "slot.save"
    bundle = SaveBundle("0.40.0", "1")
    bundle.state = {"answer": 42}
    bundle.save(path)
    loaded = SaveBundle.load(path)
    assert loaded.state == {"answer": 42}


def test_headless_harness_can_boot_a_data_project():
    harness = HeadlessHarness(str(Path(__file__).parents[1] / "examples" / "data"))
    snapshot = harness.start()
    try:
        assert snapshot.scene == "map"
        assert snapshot.running is True
    finally:
        harness.stop()
