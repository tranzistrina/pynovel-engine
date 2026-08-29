from vnengine.script.parser import VNParser
from vnengine.core.model import Character


def test_rotate_command_parses():
    story = VNParser().parse('rotate Alice 12 0.5')
    assert story.actions[0].kind == 'rotate'
    assert story.actions[0].data == {'name': 'Alice', 'rotation': 12.0, 'duration': 0.5}


def test_character_rotation_defaults_to_zero():
    char = Character('Alice', 'assets/alice.png')
    assert char.rotation == 0.0
