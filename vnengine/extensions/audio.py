from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AudioChannel:
    name: str
    volume: float = 1.0
    muted: bool = False
    loop: bool = False
    current: str | None = None
    paused: bool = False

    def serialize(self) -> dict[str, Any]: return asdict(self)


class AudioChannels:
    """Named audio buses with persistent declarative playback state."""
    DEFAULTS = ("music", "ambience", "effects", "ui", "voice")

    def __init__(self, mixer: Any = None, asset_resolver=None) -> None:
        self._mixer = mixer
        self._asset_resolver = asset_resolver or (lambda path: Path(path))
        self._channels: dict[str, AudioChannel] = {name: AudioChannel(name) for name in self.DEFAULTS}
        self._pygame_channels: dict[str, Any] = {}

    def channel(self, name: str) -> AudioChannel:
        if not isinstance(name, str) or not name: raise ValueError("audio channel name must be a non-empty string")
        return self._channels.setdefault(name, AudioChannel(name))

    def set_volume(self, name: str, volume: float) -> None:
        channel = self.channel(name); channel.volume = max(0.0, min(1.0, float(volume))); self._apply_volume(name)

    def set_muted(self, name: str, muted: bool) -> None:
        channel = self.channel(name); channel.muted = bool(muted); self._apply_volume(name)

    def play(self, name: str, path: str, *, loop: bool = False) -> bool:
        channel = self.channel(name); mixer = self._ensure_mixer()
        try:
            sound = mixer.Sound(str(self._asset_resolver(path)))
            pygame_channel = self._pygame_channels.get(name)
            if pygame_channel is None:
                pygame_channel = mixer.Channel(len(self._pygame_channels)); self._pygame_channels[name] = pygame_channel
            pygame_channel.set_volume(0.0 if channel.muted else channel.volume); pygame_channel.play(sound, loops=-1 if loop else 0)
        except (OSError, RuntimeError, ValueError): return False
        channel.current = str(path); channel.loop = bool(loop); channel.paused = False; return True

    def stop(self, name: str, fade_ms: int = 0) -> None:
        channel = self.channel(name); pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None:
            if fade_ms > 0: pygame_channel.fadeout(int(fade_ms))
            else: pygame_channel.stop()
        channel.current = None; channel.loop = False; channel.paused = False

    def pause(self, name: str) -> None:
        channel = self.channel(name); pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None: pygame_channel.pause()
        channel.paused = True

    def resume(self, name: str) -> None:
        channel = self.channel(name); pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None: pygame_channel.unpause()
        channel.paused = False

    def serialize(self) -> dict[str, dict[str, Any]]: return {name: channel.serialize() for name, channel in sorted(self._channels.items())}

    def deserialize(self, data: dict[str, dict[str, Any]] | None) -> None:
        for name, values in (data or {}).items():
            if not isinstance(values, dict): continue
            channel = self.channel(name); channel.volume = max(0.0, min(1.0, float(values.get("volume", 1.0)))); channel.muted = bool(values.get("muted", False)); channel.loop = bool(values.get("loop", False)); channel.current = values.get("current"); channel.paused = bool(values.get("paused", False)); self._apply_volume(name)

    def restore_playback(self) -> None:
        for name, channel in self._channels.items():
            if channel.current is not None and self.play(name, channel.current, loop=channel.loop) and channel.paused: self.pause(name)

    def _ensure_mixer(self):
        if self._mixer is None:
            import pygame
            self._mixer = pygame.mixer
        return self._mixer

    def _apply_volume(self, name: str) -> None:
        pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None:
            channel = self.channel(name); pygame_channel.set_volume(0.0 if channel.muted else channel.volume)
