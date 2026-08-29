from pathlib import Path
import pytest

pygame = pytest.importorskip('pygame')
from vnengine.ui.layout import UIDocument
from vnengine.ui.widgets import build_widget, Button


def test_widget_tree_and_percent_anchor():
    data = {
        'type': 'panel', 'id': 'root', 'x': 0, 'y': 0, 'width': '100%', 'height': '100%',
        'children': [
            {'type': 'button', 'id': 'start', 'x': '50%', 'y': '50%', 'width': 240, 'height': 60, 'anchor': 'center', 'text': 'Start'}
        ],
    }
    root = build_widget(data)
    screen = pygame.Surface((1280, 720))
    assert root.rect(screen).size == (1280, 720)
    button = root.children[0]
    assert isinstance(button, Button)
    assert button.rect(screen).center == (640, 360)


def test_ui_document_click_returns_action(tmp_path: Path):
    path = tmp_path / 'ui.json'
    path.write_text('{"type":"button","id":"b","action":"open_menu","x":0,"y":0,"width":100,"height":50,"text":"Go"}', encoding='utf-8')
    pygame.init()
    doc = UIDocument.load(path)
    screen = pygame.Surface((200, 100))
    assert doc.click((20, 20), screen) == 'open_menu'
    pygame.quit()
