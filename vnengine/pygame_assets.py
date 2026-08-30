from __future__ import annotations

from pathlib import Path
from typing import Any


class PygameAssetLoader:
    """pygame-ce backed loader used by AssetRuntime without leaking pygame into core APIs."""

    def __init__(self, pygame_module: Any):
        self.pygame = pygame_module

    def image(self, path: str | Path) -> Any:
        return self.pygame.image.load(str(path)).convert_alpha()

    def sound(self, path: str | Path) -> Any:
        return self.pygame.mixer.Sound(str(path))

    def font(self, path: str | Path, size: int) -> Any:
        return self.pygame.font.Font(str(path), int(size))
