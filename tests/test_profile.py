from vnengine.ui.profile import PlayerProfile, ProfileStore

def test_profile_roundtrip(tmp_path):
    store=ProfileStore(tmp_path); profile=PlayerProfile('en',88,0.5,True); store.save(profile)
    assert store.load()==profile
