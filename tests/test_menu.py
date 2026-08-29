from pathlib import Path
import pytest

pygame = pytest.importorskip("pygame")
from vnengine.ui.menu import GameMenu

def test_menu_slot_navigation(tmp_path: Path):
    pygame.init()
    menu = GameMenu(tmp_path)
    menu.open()
    menu.handle_key(pygame.K_DOWN)
    assert menu.selected == 1
    result = menu.activate()
    assert result.action == "noop"
    assert menu.mode == "save_slots"
    menu.handle_key(pygame.K_2)
    assert menu.selected == 1
    assert menu.activate().slot == 2
    pygame.quit()
