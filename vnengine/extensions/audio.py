from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AudioChannel:
    """Named audio bus with independent volume and mute state."""

    name: str
    volume: float = 1.0
    muted: bool = False
    loop: bool = False
    current: str | None = None


class AudioChannels:
    """Reusable named audio-channel abstraction over pygame's mixer."""

    DEFAULTS = ("music", "ambience", "effects", "ui", "voice")

    def __init__(self, mixer: Any = None, asset_resolver=None) -> None:
        self._mixer = mixer
        self._asset_resolver = asset_resolver or (lambda path: Path(path))
        self._channels: dict[str, AudioChannel] = {name: AudioChannel(name) for name in self.DEFAULTS}
        self._pygame_channels: dict[str, Any] = {}

    def channel(self, name: str) -> AudioChannel:
        if not name or not isinstance(name, str):
            raise ValueError("audio channel name must be a non-empty string")
        if name not in self._channels:
            self._channels[name] = AudioChannel(name)
        return self._channels[name]

    def set_volume(self, name: str, volume: float) -> None:
        channel = self.channel(name)
        channel.volume = max(0.0, min(1.0, float(volume)))
        self._apply_volume(name)

    def set_muted(self, name: str, muted: bool) -> None:
        channel = self.channel(name)
        channel.muted = bool(muted)
        self._apply_volume(name)

    def play(self, name: str, path: str, *, loop: bool = False) -> None:
        channel = self.channel(name)
        mixer = self._ensure_mixer()
        try:
            sound = mixer.Sound(str(self._asset_resolver(path)))
            pygame_channel = self._pygame_channels.get(name)
            if pygame_channel is None:
                pygame_channel = mixer.Channel(len(self._pygame_channels))
                self._pygame_channels[name] = pygame_channel
            pygame_channel.set_volume(0.0 if channel.muted else channel.volume)
            pygame_channel.play(sound, loops=-1 if loop else 0)
            channel.current = path
            channel.loop = bool(loop)
        except (OSError, RuntimeError, ValueError):
            return

    def stop(self, name: str, fade_ms: int = 0) -> None:
        channel = self.channel(name)
        pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None:
            if fade_ms > 0:
                pygame_channel.fadeout(int(fade_ms))
            else:
                pygame_channel.stop()
        channel.current = None
        channel.loop = False

    def pause(self, name: str) -> None:
        pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None:
            pygame_channel.pause()

    def resume(self, name: str) -> None:
        pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None:
            pygame_channel.unpause()

    def serialize(self) -> dict[str, dict[str, Any]]:
        return {name: {"volume": item.volume, "muted": item.muted} for name, item in self._channels.items()}

    def deserialize(self, data: dict[str, dict[str, Any]] | None) -> None:
        for name, values in (data or {}).items():
            channel = self.channel(name)
            channel.volume = max(0.0, min(1.0, float(values.get("volume", 1.0))))
            channel.muted = bool(values.get("muted", False))
            self._apply_volume(name)

    def _ensure_mixer(self):
        if self._mixer is None:
            import pygame
            self._mixer = pygame.mixer
        return self._mixer

    def _apply_volume(self, name: str) -> None:
        pygame_channel = self._pygame_channels.get(name)
        if pygame_channel is not None:
            channel = self.channel(name)
            pygame_channel.set_volume(0.0 if channel.muted else channel.volume)
