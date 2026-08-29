from vnengine.animation.preview import AnimationPreview, PreviewState
from vnengine.animation.timeline import Timeline


def test_preview_applies_sampled_properties():
    timeline = Timeline("Preview")
    timeline.add_keyframe("Alice", "x", 0.0, 10.0)
    timeline.add_keyframe("Alice", "x", 1.0, 90.0)
    timeline.add_keyframe("Alice", "rotation", 0.0, 0.0)
    timeline.add_keyframe("Alice", "rotation", 1.0, 12.0)

    preview = AnimationPreview({"Alice": PreviewState()})
    preview.seek(timeline, 0.5)

    assert preview.targets["Alice"].x == 50.0
    assert preview.targets["Alice"].rotation == 6.0


def test_preview_supports_all_transform_properties():
    timeline = Timeline("Transforms")
    for prop, value in (("x", 20), ("y", 30), ("scale", 1.2), ("opacity", 0.6), ("rotation", 5)):
        timeline.add_keyframe("Alice", prop, 0.0, value)

    preview = AnimationPreview()
    preview.seek(timeline, 0.0)
    snapshot = preview.snapshot()["Alice"]

    assert snapshot == {"x": 20.0, "y": 30.0, "scale": 1.2, "opacity": 0.6, "rotation": 5.0}
