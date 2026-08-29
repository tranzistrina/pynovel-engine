from pathlib import Path

from vnengine.assets.catalog import AssetCatalog, AssetType, classify


def test_classify_known_extensions():
    assert classify(Path("hero.png")) == AssetType.IMAGE
    assert classify(Path("theme.ogg")) == AssetType.AUDIO
    assert classify(Path("intro.mp4")) == AssetType.VIDEO
    assert classify(Path("main.vn")) == AssetType.SCRIPT
    assert classify(Path("unknown.bin")) == AssetType.OTHER


def test_scan_and_missing(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "hero.png").write_bytes(b"123")
    (tmp_path / "assets" / "theme.ogg").write_bytes(b"12345")
    catalog = AssetCatalog(tmp_path)
    entries = catalog.scan()
    assert [entry.path for entry in entries] == ["assets/hero.png", "assets/theme.ogg"]
    assert catalog.find("assets/hero.png").size == 3
    assert catalog.missing(["assets/hero.png", "assets/missing.png"]) == ["assets/missing.png"]


def test_write_index(tmp_path):
    (tmp_path / "hero.webp").write_bytes(b"abc")
    catalog = AssetCatalog(tmp_path)
    index = catalog.write_index()
    assert index == tmp_path / ".pynovel" / "assets.json"
    assert index.exists()
    assert '"asset_type": "image"' in index.read_text(encoding="utf-8")
