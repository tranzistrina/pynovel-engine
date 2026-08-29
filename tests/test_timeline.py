from vnengine.animation.timeline import Keyframe, Timeline, Track, ease


def test_track_interpolates_with_easing():
    track = Track("Alice", "x")
    track.add(Keyframe(0, 0, "linear"))
    track.add(Keyframe(1, 100, "linear"))
    assert track.sample(0.5) == 50


def test_timeline_samples_multiple_properties_and_roundtrips():
    timeline = Timeline("enter", loop=True)
    timeline.add_keyframe("Alice", "x", 0, 0)
    timeline.add_keyframe("Alice", "x", 1, 100, "ease_out")
    timeline.add_keyframe("Alice", "opacity", 0, 0)
    timeline.add_keyframe("Alice", "opacity", 1, 1)
    timeline.seek(0.5)
    values = timeline.sample()
    assert 50 < values[("Alice", "x")] < 100
    assert values[("Alice", "opacity")] == 0.5
    restored = Timeline.from_dict(timeline.to_dict())
    assert restored.to_dict() == timeline.to_dict()


def test_looping_and_stop():
    timeline = Timeline("pulse", loop=True)
    timeline.add_keyframe("Alice", "scale", 0, 1)
    timeline.add_keyframe("Alice", "scale", 2, 2)
    timeline.play()
    timeline.update(2.5)
    assert timeline.time == 0.5
    timeline.stop()
    assert timeline.time == 0
    assert not timeline.playing


def test_unknown_easing_rejected():
    assert ease(0.5, "linear") == 0.5
    try:
        Keyframe(0, 1, "wat")
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown easing must raise ValueError")
