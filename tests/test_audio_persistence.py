from vnengine.extensions.audio import AudioChannels


class FakeChannel:
    def __init__(self):
        self.calls = []
    def set_volume(self, value): self.calls.append(("volume", value))
    def play(self, sound, loops=0): self.calls.append(("play", sound, loops))
    def pause(self): self.calls.append(("pause",))
    def unpause(self): self.calls.append(("resume",))
    def stop(self): self.calls.append(("stop",))


class FakeMixer:
    def __init__(self): self.channels = []
    def Sound(self, path): return f"sound:{path}"
    def Channel(self, index):
        channel = FakeChannel(); self.channels.append(channel); return channel


def test_audio_state_roundtrips_and_restores_playback():
    mixer = FakeMixer()
    audio = AudioChannels(mixer=mixer, asset_resolver=lambda path: path)
    assert audio.play("music", "theme.ogg", loop=True)
    audio.set_volume("music", 0.4)
    audio.pause("music")

    payload = audio.serialize()
    restored = AudioChannels(mixer=FakeMixer(), asset_resolver=lambda path: path)
    restored.deserialize(payload)
    assert restored.channel("music").current == "theme.ogg"
    assert restored.channel("music").loop is True
    assert restored.channel("music").paused is True
    restored.restore_playback()
    calls = restored._pygame_channels["music"].calls
    assert ("play", "sound:theme.ogg", -1) in calls
    assert ("pause",) in calls
