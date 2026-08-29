from vnengine.assets.dragdrop import decode_asset_path, encode_asset_path


def test_asset_dragdrop_roundtrip():
    path = r"assets\characters\alice.png"
    payload = encode_asset_path(path)
    assert payload.startswith("pynovel-asset:")
    assert decode_asset_path(payload) == "assets/characters/alice.png"


def test_asset_dragdrop_rejects_other_payload():
    assert decode_asset_path("text/plain:assets/a.png") is None
