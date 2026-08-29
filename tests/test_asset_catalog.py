from pathlib import Path

from vnengine.assets.catalog import AssetCatalog, AssetType, classify


def test_classify_common_assets(tmp_path: Path):
    assert classify(Path('hero.png')) == AssetType.IMAGE
    assert classify(Path('theme.ogg')) == AssetType.AUDIO
    assert classify(Path('opening.mp4')) == AssetType.VIDEO
    assert classify(Path('font.ttf')) == AssetType.FONT
    assert classify(Path('scene.vn')) == AssetType.SCRIPT


def test_scan_and_missing(tmp_path: Path):
    (tmp_path / 'assets').mkdir()
    (tmp_path / 'assets' / 'hero.png').write_bytes(b'png')
    (tmp_path / 'assets' / 'theme.ogg').write_bytes(b'ogg')
    hidden = tmp_path / '.pynovel'
    hidden.mkdir()
    (hidden / 'assets.json').write_text('{}', encoding='utf-8')

    catalog = AssetCatalog(tmp_path)
    entries = catalog.scan()
    assert [entry.path for entry in entries] == ['assets/hero.png', 'assets/theme.ogg']
    assert catalog.find('assets/hero.png').asset_type == AssetType.IMAGE
    assert catalog.missing(['assets/hero.png', 'assets/nope.png']) == ['assets/nope.png']

    index = catalog.write_index()
    assert index == tmp_path / '.pynovel' / 'assets.json'
    assert index.exists()
