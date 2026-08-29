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
