from vnengine.extensions.audio import AudioChannels


class FakeChannel:
    def __init__(self):
        self.volume = None
        self.played = []
        self.stopped = False
        self.paused = False

    def set_volume(self, value): self.volume = value
    def play(self, sound, loops=0): self.played.append((sound, loops))
    def stop(self): self.stopped = True
    def fadeout(self, ms): self.stopped = ms
    def pause(self): self.paused = True
    def unpause(self): self.paused = False


class FakeMixer:
    def __init__(self): self.channels = []
    def Sound(self, path): return path
    def Channel(self, index):
        channel = FakeChannel(); self.channels.append(channel); return channel


def test_named_channels_have_independent_volume_and_mute():
    mixer = FakeMixer(); audio = AudioChannels(mixer, lambda path: f"assets/{path}")
    audio.set_volume("music", 0.35); audio.set_muted("ui", True)
    assert audio.channel("music").volume == 0.35
    assert audio.channel("ui").muted is True
    assert audio.channel("effects").volume == 1.0


def test_play_uses_named_mixer_channel_and_loop_state():
    mixer = FakeMixer(); audio = AudioChannels(mixer, lambda path: f"assets/{path}")
    audio.play("voice", "voice.ogg", loop=True)
    assert mixer.channels[0].played == [("assets/voice.ogg", -1)]
    assert audio.channel("voice").current == "voice.ogg"
    assert audio.channel("voice").loop is True


def test_audio_state_round_trips_without_current_playback():
    audio = AudioChannels(FakeMixer())
    audio.set_volume("music", 0.2); audio.set_muted("effects", True)
    restored = AudioChannels(FakeMixer()); restored.deserialize(audio.serialize())
    assert restored.channel("music").volume == 0.2
    assert restored.channel("effects").muted is True


def test_stop_pause_resume_clear_runtime_state():
    mixer = FakeMixer(); audio = AudioChannels(mixer)
    audio.play("ui", "click.wav")
    audio.pause("ui"); assert mixer.channels[0].paused is True
    audio.resume("ui"); assert mixer.channels[0].paused is False
    audio.stop("ui"); assert audio.channel("ui").current is None
