from vnengine.extensions.notifications import NotificationLog


def test_notification_log_tracks_order_unread_and_actions():
    log = NotificationLog()
    first = log.add("Supplies", "Low stock", severity="warning", icon="crate", timestamp=12, action="open:supplies")
    second = log.add("Battle", "Started", timestamp=13)

    assert [item.id for item in log.items] == ["notification-1", "notification-2"]
    assert log.unread_count == 2
    assert first.action == "open:supplies"
    assert second.timestamp == 13

    assert log.mark_read(first.id)
    assert log.unread_count == 1
    assert not log.mark_read("missing")


def test_notification_log_serializes_and_continues_ids():
    log = NotificationLog()
    log.add("One", timestamp=4)
    log.add("Two", timestamp=8)
    log.mark_all_read()

    restored = NotificationLog()
    restored.deserialize(log.serialize())
    next_item = restored.add("Three", timestamp=9)

    assert [item.id for item in restored.items] == ["notification-1", "notification-2", "notification-3"]
    assert restored.unread_count == 1
    assert all(not item.unread for item in restored.items[:2])


def test_notification_log_remove_and_clear():
    log = NotificationLog()
    first = log.add("One")
    second = log.add("Two")

    assert log.remove(first.id)
    assert not log.remove(first.id)
    assert [item.id for item in log.items] == [second.id]

    log.clear()
    assert log.items == ()
    assert log.unread_count == 0
