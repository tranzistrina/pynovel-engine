import pytest

from vnengine.extensions.scheduler import GameScheduler


def test_scheduler_is_deterministic_and_ordered():
    scheduler = GameScheduler()
    scheduler.schedule(2, "late")
    scheduler.schedule(1, "first", {"value": 1})
    scheduler.schedule(1, "second", {"value": 2})
    fired = scheduler.advance(1)
    assert [item.event for item in fired] == ["first", "second"]
    assert scheduler.tick == 1
    fired = scheduler.advance(1)
    assert [item.event for item in fired] == ["late"]


def test_scheduler_serializes_pending_events():
    scheduler = GameScheduler()
    scheduler.schedule(5, "campaign.day", {"day": 2})
    scheduler.advance(2)
    restored = GameScheduler()
    restored.deserialize(scheduler.serialize())
    assert restored.tick == 2
    assert [item.event for item in restored.advance(3)] == ["campaign.day"]


def test_scheduler_preserves_fractional_time_scale():
    scheduler = GameScheduler(tick_rate=10)
    scheduler.time_scale = 0.5
    first = scheduler.schedule(1, "first")
    assert scheduler.advance(1) == ()
    assert scheduler.tick == 0
    assert scheduler.advance(1) == (first,)
    assert scheduler.tick == 1


def test_scheduler_supports_absolute_schedule_and_cancel():
    scheduler = GameScheduler()
    item = scheduler.schedule_at(5, "later", {"value": 3})
    assert scheduler.cancel(item) is True
    assert scheduler.cancel(item) is False
    assert scheduler.advance(5) == ()


def test_scheduler_pause_and_restore_fractional_state():
    scheduler = GameScheduler(tick_rate=24)
    scheduler.time_scale = 0.25
    scheduler.advance(3)
    payload = scheduler.serialize()
    restored = GameScheduler()
    restored.deserialize(payload)
    assert restored.serialize() == payload
    restored.paused = True
    assert restored.advance(10) == ()
    assert restored.tick == 0


def test_scheduler_rejects_past_absolute_events():
    scheduler = GameScheduler()
    scheduler.advance(3)
    with pytest.raises(ValueError):
        scheduler.schedule_at(2, "past")
