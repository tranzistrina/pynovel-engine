from vnengine.animation.timeline import Timeline
from vnengine.animation.preview import AnimationPreview


def test_preview_samples_transform_properties():
    timeline = Timeline("spin")
    timeline.add_keyframe("Alice", "x", 0.0, 20.0)
    timeline.add_keyframe("Alice", "x", 1.0, 60.0)
    timeline.add_keyframe("Alice", "scale", 0.0, 1.0)
    timeline.add_keyframe("Alice", "scale", 1.0, 1.5)
    timeline.add_keyframe("Alice", "opacity", 0.0, 0.0)
    timeline.add_keyframe("Alice", "opacity", 0.5, 1.0)
    timeline.add_keyframe("Alice", "rotation", 0.0, -5.0)
    timeline.add_keyframe("Alice", "rotation", 1.0, 5.0)
    preview = AnimationPreview()
    preview.ensure_target("Alice")
    preview.seek(timeline, 0.5)
    state = preview.targets["Alice"]
    assert state.x == 40.0
    assert state.scale == 1.25
    assert state.opacity == 1.0
    assert state.rotation == 0.0
